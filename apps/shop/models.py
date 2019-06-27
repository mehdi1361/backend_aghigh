from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from scripts.get_video_information import get_video_duration
from apps.activity import static
from apps.common.models import Image
from apps.common.fields import ImageWithThumbsField
from apps.common.helpers.media_filename_hash import MediaFileNameHash


class Coupon(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name=_("title")
    )
    type_of_discount_c = (
        ("PERCENT", 'percent'),
        ('MONEY', 'money'),
    )
    percent = models.PositiveIntegerField(verbose_name=_("Percent"), null=True, blank=True)
    money = models.PositiveIntegerField(verbose_name=_("Money"), null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=static.gender_choice,
        verbose_name=_("Gender")
    )

    expire_at = models.DateTimeField(verbose_name=_("Expire at"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __str__(self):
        return self.title


class CouponCode(models.Model):
    code = models.CharField(max_length=32, verbose_name=_("Code"))
    coupon = models.ForeignKey(to=Coupon, verbose_name=_("Coupon"))
    number_of_user_usage = models.PositiveIntegerField(verbose_name=_("Number Of Students"))

    class Meta:
        verbose_name = _("Coupon Code")
        verbose_name_plural = _("Coupons Code")


class Category(models.Model):
    title = models.CharField(max_length=50, verbose_name=_("Name"))
    slug = models.SlugField(max_length=100, verbose_name=_("Slug"))
    parent = models.ForeignKey("self", verbose_name=_("Parent"), null=True, blank=True)

    coupon = models.ForeignKey(to=Coupon, verbose_name=_("Coupon"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")


class SampleFormsGroup(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Title"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Sample Forms Group")
        verbose_name_plural = _("Sample Forms Group")

    def __str__(self):
        return self.title


class SampleFormFields(models.Model):
    field_type_choice = (
        ('number', 'Number'),
        ('text_box', 'Text Box'),
        # ('check_box', 'Check Box'),
    )

    title = models.CharField(max_length=100, verbose_name=_("Title"))
    sample_form_group = models.ForeignKey(to=SampleFormsGroup, verbose_name=_("Sample Form Group"))

    presentation = models.CharField(max_length=32, verbose_name=_("Presentation"), null=True, blank=True)
    is_required = models.BooleanField(default=False, verbose_name=_("Is Required"))
    type = models.CharField(max_length=32, verbose_name=_("Type"), choices=field_type_choice, default='text_box')
    order = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("order")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Sample Form Fields")
        verbose_name_plural = _("Sample Form Fields")

    def __str__(self):
        return self.title


class SampleForms(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    groups = models.ManyToManyField(to=SampleFormsGroup)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Sample Forms")
        verbose_name_plural = _("Sample Forms")

    def __str__(self):
        return self.title


class Product(models.Model):
    gender_choice = (
        ('both', _('both')),
        ('female', _('female')),
        ('male', _('male'))
    )
    title = models.CharField(max_length=150, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))

    category = models.ForeignKey(to=Category, verbose_name=_("Category"))
    creator = models.ForeignKey(to=User, verbose_name=_("User"), related_name="user_creator")
    editor = models.ForeignKey(to=User, verbose_name=_("Editor"), related_name="user_editor", null=True)

    price = models.PositiveIntegerField(default=0, verbose_name=_("Price"))
    has_discount = models.BooleanField(default=False, verbose_name=_("Has Discount"))
    discount = models.PositiveIntegerField(default=0, verbose_name=_("Discount"))
    is_free = models.BooleanField(default=False, verbose_name=_("Is Free"))
    deleted = models.BooleanField(default=False, verbose_name=_("Deleted"))

    coupon = models.ForeignKey(to=Coupon, verbose_name=_("Coupon"), null=True, blank=True)
    sample_form = models.ForeignKey(to=SampleForms, verbose_name=_("Sample Form"), null=True, blank=True)

    published = models.BooleanField(default=False, verbose_name=_("Published"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    gender = models.CharField(
        max_length=10,
        choices=gender_choice,
        verbose_name=_("Gender"),
        null=True, blank=True
    )

    link_buy_direct = models.URLField(max_length=300, blank=True, null=True, verbose_name=_("Link Buy Direct"))  # لینک خرید از خارج از سایت
    seller_name = models.CharField(default='دفتر مرکزی',max_length=150, blank=True, null=True, verbose_name=_("Seller Name"))  # نام فروشنده
    is_digital = models.BooleanField(default=True, verbose_name=_("Digital"))  # نوع محصول دیجیتال است یا فیزیکی
    for_student = models.BooleanField(default=True, verbose_name=_("For Student"))  # محصول برای دانش آموزان است یا نه؟
    for_teacher = models.BooleanField(default=False, verbose_name=_("For Teacher"))  # محصول برای مربی و ادمین ها است یا نه؟

    def get_sample_form_field(self):
        values = ProductSampleFormFields.objects.filter(product_id=self.id)
        return values

    def get_images(self):
        values = ProductImage.objects.filter(product_id=self.id, archive=False)
        return values

    def get_files(self):
        values = ProductFile.objects.filter(product_id=self.id, archive=False)
        return values

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


class ProductImage(models.Model):
    image = ImageWithThumbsField(
        upload_to=MediaFileNameHash("shop_image"),
        default=None,
        sizes=((320, 180), (145, 145), (711, 400),),
        preserve_ratio=True,
        verbose_name=_("Address")
    )
    size = models.CharField(max_length=150, default="", blank=True, null=True)
    product = models.ForeignKey(to=Product, verbose_name=_("Product"))
    archive = models.BooleanField(default=False, verbose_name=_("Archive"))

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            self.size = self.image.size
            try:
                self.title = self.image.name.split("@")[0]
            except:
                pass

        super(ProductImage, self).save()

    def image_tag(self):
        return u'<img src="/{0}" style="{1}" {2}/>'.format(self.image.url, "width: 100%", 'height=150')

    image_tag.allow_tags = True


class ProductFile(models.Model):
    file = models.FileField(
        upload_to=MediaFileNameHash("shop_files"),
        verbose_name=_("File")
    )
    product = models.ForeignKey(to=Product, verbose_name=_("Product"))
    size = models.CharField(max_length=150, default="", blank=True, null=True)
    title = models.CharField(max_length=150, default="", blank=True, null=True)
    duration = models.TimeField(blank=True, null=True)
    archive = models.BooleanField(default=False, verbose_name=_("Archive"))

    class Meta:
        verbose_name = _("File Product")
        verbose_name_plural = _("File Products")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.id is None:
            try:
                self.title = self.file.name.split("@")[0]
            except:
                pass
            self.size = self.file.size

        super(ProductFile, self).save()
        # get file format
        file_format = self.file.name.split(".")[-1].upper()
        if file_format in ['MP4', 'FLV', 'MOV', 'AVI', 'MPEG', 'WMV', '3GP', 'VOB', 'MPG', 'MP3', 'M4A', 'OGG', 'WMA']:
            # get duration for video or audio
            self.duration = get_video_duration(self.file.path)
            super(ProductFile, self).save()


class ProductRate(models.Model):
    product = models.ForeignKey(to=Product, related_name='rates', verbose_name=_("Product"))
    user = models.ForeignKey(to=User, default=None, verbose_name=_("User"))
    rate = models.PositiveIntegerField(default=0, choices=static.rate_choice, verbose_name=_("Rate"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Rate")
        verbose_name_plural = _("Rates")


class Param(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Param")
        verbose_name_plural = _("Param")


class ProductComment(models.Model):
    product = models.ForeignKey(to=Product, verbose_name=_("Product"))
    sender = models.ForeignKey(to=User, verbose_name=_("Sender"))
    comment = models.TextField(verbose_name=_("Comment"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    def get_param(self):
        params = ParamProductComment.objects.filter(product_comment_id=self.id) \
            .select_related('param')
        return params

    class Meta:
        verbose_name = _("Product Comment")
        verbose_name_plural = _("Product Comments")

    def __str__(self):
        return str(self.id)


class ParamProductComment(models.Model):
    product_comment = models.ForeignKey(to=ProductComment, verbose_name=_("Product comment"))
    param = models.ForeignKey(to=Param, verbose_name=_("param"))
    value = models.PositiveIntegerField(verbose_name=_("value"), default=0, choices=static.rate_choice)

    class Meta:
        verbose_name = _("Param Product Comment")
        verbose_name_plural = _("Param Product Comments")


class SumProductParam(models.Model):
    Product = models.ForeignKey(to=Product)
    param = models.ForeignKey(to=Param, verbose_name=_("Param"))

    sum = models.IntegerField(verbose_name=_("Sum"))
    count = models.IntegerField(verbose_name=_("Count"))

    class Meta:
        verbose_name = _("Sum Product Param")
        verbose_name_plural = _("Sum Product Params")


class Basket(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("Product"))
    user = models.ForeignKey(User, verbose_name=_("User"))

    class Meta:
        verbose_name = _("Basket")
        verbose_name_plural = _("Basket")


class Invoice(models.Model):
    code = models.CharField(max_length=32, verbose_name=_("Code"), null=True, blank=True)
    user = models.ForeignKey(User, verbose_name=_("User"))
    paid = models.BooleanField(default=False, verbose_name=_("paid"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def __str__(self):
        return self.code


class InvoiceProduct(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("Product"))
    invoice = models.ForeignKey(Invoice, verbose_name=_("Invoice"))

    title = models.CharField(max_length=50, verbose_name=_("Title"))
    description = models.TextField(verbose_name=_("Description"))

    price = models.PositiveIntegerField(verbose_name=_("Price"))
    has_discount = models.BooleanField(default=False, verbose_name=_("Has Discount"))
    discount = models.PositiveIntegerField(verbose_name=_("Discount"), null=True, blank=True)
    is_free = models.BooleanField(default=False, verbose_name=_("Is Free"))

    coupon = models.ForeignKey(to=Coupon, verbose_name=_("Coupon"), null=True, blank=True)
    sample_form = models.ForeignKey(to=SampleForms, verbose_name=_("Sample Form"), null=True, blank=True)

    gender = models.CharField(max_length=10)

    class Meta:
        verbose_name = _("Invoice Product")
        verbose_name_plural = _("Invoice Product")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.title = self.product.title
        self.description = self.product.description
        self.price = self.product.price
        self.has_discount = self.product.has_discount
        self.is_free = self.product.is_free
        self.gender = self.product.gender
        self.coupon = self.product.coupon
        self.discount = self.product.discount

        super(InvoiceProduct, self).save()


class ProductSampleFormFields(models.Model):
    product = models.ForeignKey(to=Product, verbose_name=_("Product"))
    sample_form_field = models.ForeignKey(to=SampleFormFields, verbose_name=_("Sample Form Fields"))
    value = models.CharField(max_length=100, verbose_name=_("value"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name = _("Product Sample Form Fields")
        verbose_name_plural = _("Product Sample Form Fields")


class ShopSlider(models.Model):
    gender_choice = (
        ('both', _('both')),
        ('female', _('female')),
        ('male', _('male'))
    )
    type_slider = (
        ("PRODUCT", 'product'),
        ('BANNER', 'banner'),
    )
    title = models.CharField(max_length=150, verbose_name=_("Title"))
    link = models.CharField(max_length=100, verbose_name=_("Link"), null=True, blank=True)
    type = models.CharField(max_length=32, verbose_name=_("Type"), choices=type_slider)
    image = ImageWithThumbsField(
        upload_to=MediaFileNameHash("banners"),
        default=None,
        sizes=((320, 180), (145, 145), (711, 400),),
        preserve_ratio=True,
        verbose_name=_("Image")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    for_student = models.BooleanField(default=True, verbose_name=_("Student"))  # محصول برای دانش آموزان است یا نه؟
    for_teacher = models.BooleanField(default=False, verbose_name=_("get_coach"))  # محصول برای مربی و ادمین ها است یا نه؟
    gender = models.CharField(
        max_length=10,
        choices=gender_choice,
        verbose_name=_("Gender"),
        null=True, blank=True
    )
    # product_related = models.ForeignKey(null=True,blank=True,to=Product, verbose_name=_("Product")) # برای اتصال

    def image_tag(self):
        return u'<img src="/{0}" style="{1}" {2}/>'.format(self.image.url, "width: 100%", 'height=150')

    image_tag.allow_tags = True

    class Meta:
        verbose_name = _("Shop Slider")
        verbose_name_plural = _("Shop Sliders")

    def __str__(self):
        return self.title
