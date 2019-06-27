"""
Used as a model field to generate thumbnail images along with
the source image
"""

import io
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from PIL import Image, ImageOps


def generate_thumb(original, size, preserve_ratio, output_format='JPG'):
    """
    Generates a thumbnail image and returns a ContentFile object with the thumbnail
    Arguments:
    original        -- The image being resize'd as `File`.
    size            -- Desired thumbnail size as `tuple`. Example: (70, 100)
    preserve_ratio  -- True if the thumbnail is to keep the aspect ratio of the full image
    format          -- Format of the original image ('JPEG', 'PNG', ...) The thumbnail will be generated using this same format.
    """
    original.seek(0)  # see http://code.djangoproject.com/ticket/8222 for details
    image = Image.open(original)
    # if image.mode not in ('L', 'RGB', 'RGBA'):
    image = image.convert('RGB')
    if preserve_ratio:
        image.thumbnail(size, Image.ANTIALIAS)
    else:
        image = ImageOps.fit(image, size, Image.ANTIALIAS)
    input_output = io.BytesIO()
    if output_format.upper() == 'JPG':
        output_format = 'JPEG'
    image.save(input_output, output_format, quality=100)
    return ContentFile(input_output.getvalue())


class ImageWithThumbsFieldFile(ImageFieldFile):
    """
    Django `ImageField` replacement with automatic generation of thumbnail images.
    See `ImageWithThumbsField` for usage example.
    """

    THUMB_SUFFIX = '%s.%sx%s.%s'

    def __init__(self, *args, **kwargs):
        super(ImageFieldFile, self).__init__(*args, **kwargs)

    def _url_for_size(self, size):
        """
        Return a URL pointing to the thumbnail image of the requested size.
        If `THUMBS_GENERATE_MISSING_THUMBNAILS` is True, the thumbnail will be created if it doesn't exist on disk.
        Arguments:
        size  -- A tuple with the desired width and height. Example: (100, 100)
        """
        if not self:
            return ''
        else:
            # generate missing thumbnail if needed
            file_base, extension = self.name.rsplit('.', 1)
            thumb_file = self.THUMB_SUFFIX % (file_base, size[0], size[1], extension)
            if not self.storage.exists(thumb_file):
                try:
                    self._generate_thumb(self.storage.open(self.name), size)
                except Exception:
                    if settings.DEBUG:
                        raise
            return self.storage.url(thumb_file)

    def __getattr__(self, name):
        """
        Return the url for the requested size.
        Arguments:
        name -- The field `url` with size suffix formatted as _WxH. Example: instance.url_100x70
        """
        if "url_" not in name:
            return getattr(super(ImageFieldFile), name)
        size_str = name.replace("url_", "")
        width, height = size_str.split("x")
        requested_size = (int(width), int(height))
        accepted_size = None
        for configured_size in self.field.sizes:
            if requested_size == configured_size:
                accepted_size = requested_size
                break
        if accepted_size is not None:
            return self._url_for_size(accepted_size)
        raise ValueError("The requested thumbnail size %s doesn't exist" % size_str)

    def _generate_thumb(self, image, size):
        """
        Generates a thumbnail of `size`.
        Arguments:
        image -- An `File` object with the image in its original size.
        size  -- A tuple with the desired width and height. Example: (100, 100)
        """
        base, extension = self.name.rsplit('.', 1)
        thumb_name = self.THUMB_SUFFIX % (base, size[0], size[1], extension)
        thumbnail = generate_thumb(image, size, self.field.preserve_ratio, extension)

        is_thumbnail_exist = self.storage.exists(thumb_name)
        if is_thumbnail_exist:
            self.storage.delete(thumb_name)

        saved_as = self.storage.save(thumb_name, thumbnail)
        if thumb_name != saved_as:
            raise ValueError('There is already a file named %s' % thumb_name)

    def save(self, name, content, save=True):
        super(ImageFieldFile, self).save(name, content, save)
        if self.field.sizes:
            for size in self.field.sizes:
                try:
                    self._generate_thumb(content, size)
                except Exception:
                    if settings.DEBUG:
                        raise

    def delete(self, save=True):
        if self.name and self.field.sizes:
            for size in self.field.sizes:
                base, extension = self.name.rsplit('.', 1)
                thumb_name = self.THUMB_SUFFIX % (base, size[0], size[1], extension)
                try:
                    self.storage.delete(thumb_name)
                except Exception:
                    if settings.DEBUG:
                        raise
        super(ImageFieldFile, self).delete(save)

    def generate_thumbnails(self):
        """
        """
        if self.field.sizes:
            for size in self.field.sizes:
                try:
                    self._generate_thumb(self.storage.open(self.name), size)
                except Exception:
                    if settings.DEBUG:
                        raise

    def thumbnail(self, width_or_size, height=None):
        """
        Return the thumbnail url for an specific size. The same thing as url_[width]x[height] without the magic.
        Arguments:
        widthOrSize -- Width as integer or size as tuple.
        height      -- Height as integer. Optional, will use `width_or_size` as height if missing.
        Usage:
        instance.thumbnail(48, 48)
        instance.thumbnail(64)
        instance.thumbnail( (100, 70) )
        """
        if type(width_or_size) is tuple:
            size = width_or_size
        else:
            if height is None:
                height = width_or_size
            size = (width_or_size, height)
        return self.__getattr__('url_%sx%s' % (size[0], size[1]))


class ImageWithThumbsField(ImageField):
    """
    Usage example:
    ==============
    photo = ImageWithThumbsField(upload_to='images', sizes=((125,125),(300,200),)
    To retrieve image URL, exactly the same way as with ImageField:
        my_object.photo.url
    To retrieve thumbnails URL's just add the size to it:
        my_object.photo.url_125x125
        my_object.photo.url_300x200
    Note: The 'sizes' attribute is not required. If you don't provide it,
    ImageWithThumbsField will act as a normal ImageField
    How it works:
    =============
    For each size in the 'sizes' attribute of the field it generates a
    thumbnail with that size and stores it following this format:
    available_filename.[width]x[height].extension
    Where 'available_filename' is the available filename returned by the storage
    backend for saving the original file.
    Following the usage example above: For storing a file called "photo.jpg" it saves:
    photo.jpg          (original file)
    photo.125x125.jpg  (first thumbnail)
    photo.300x200.jpg  (second thumbnail)
    With the default storage backend if photo.jpg already exists it will use these filename's:
    photo_.jpg
    photo_.125x125.jpg
    photo_.300x200.jpg
    Note: django-thumbs assumes that if filename "any_filename.jpg" is available
    filename's with this format "any_filename.[width]x[height].jpg" will be available, too.
    """
    attr_class = ImageWithThumbsFieldFile

    def __init__(self, verbose_name=None, name=None,
                 width_field=None, height_field=None,
                 sizes=None, preserve_ratio=False, **kwargs):

        super(ImageField, self).__init__(**kwargs)
        self.verbose_name = verbose_name
        self.name = name
        self.width_field = width_field
        self.height_field = height_field
        self.sizes = sizes
        self.preserve_ratio = preserve_ratio

