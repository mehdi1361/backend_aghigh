from rest_framework import serializers
from apps.shop.models import (
    Product,
    Category,
    SampleForms,
    ProductFile,
    ProductImage,
    ShopSlider,
    ProductSampleFormFields,
    Invoice,
    Basket,
    InvoiceProduct
)
from apps.user.serializers import BaseSerializer


class UrlField(serializers.HyperlinkedModelSerializer):
    def to_representation(self, value):
        return '/' + value.url

    def to_internal_value(self, data):
        pass


class ImageSerializer(serializers.ModelSerializer):
    image = UrlField(read_only=True)

    class Meta:
        model = ProductImage
        fields = '__all__'


class FilesSerializer(serializers.ModelSerializer):
    file = UrlField(read_only=True)

    class Meta:
        model = ProductFile
        fields = '__all__'


class ProductSampleFormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSampleFormFields
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryAndSubSerializer(serializers.ModelSerializer):

    @staticmethod
    def get_parent(obj):
        if obj.parent:
            try:
                return CategorySerializer(Category.objects.get(id=obj.parent_id), many=False).data
            except Category.DoesNotExist:
                return {}
        return {}
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'id',
            'title',
            'slug',
            'parent',
            'coupon',
            'created_at',
            'updated_at',
        )


class ManagerProductSerializer(serializers.ModelSerializer):
    creator = BaseSerializer(many=False, read_only=True)
    editor = BaseSerializer(many=False, read_only=True)
    images = ImageSerializer(many=True, read_only=True, source='get_images')
    files = FilesSerializer(many=True, read_only=True, source='get_files')
    sample_form_fields = ProductSampleFormFieldSerializer(many=True, read_only=True, source='get_sample_form_field')
    category = CategoryAndSubSerializer(many=False, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'title', 'description',
            'category', 'creator',
            'price', 'has_discount',
            'discount', 'is_free',
            'coupon', 'sample_form',
            'published', 'updated_at',
            'created_at', 'images',
            'gender', 'files', 'sample_form_fields',
            'creator', 'editor',
            'link_buy_direct', 'seller_name',
            'is_digital', 'for_student', 'for_teacher'
        )


class UpdateProductSerializer(serializers.ModelSerializer):
    creator = BaseSerializer(many=False, read_only=True)
    editor = BaseSerializer(many=False, read_only=True)
    images = ImageSerializer(many=True, read_only=True, source='get_images')
    files = FilesSerializer(many=True, read_only=True, source='get_files')
    sample_form_fields = ProductSampleFormFieldSerializer(many=True, read_only=True, source='get_sample_form_field')

    class Meta:
        model = Product
        fields = (
            'id',
            'title', 'description',
            'category', 'creator',
            'price', 'has_discount',
            'discount', 'is_free',
            'coupon', 'sample_form',
            'published', 'updated_at',
            'created_at', 'images',
            'gender', 'files', 'sample_form_fields',
            'creator', 'editor',
            'link_buy_direct', 'seller_name',
            'is_digital', 'for_student', 'for_teacher'
        )


class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductBoxSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True, source='get_images')

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'price',
            'has_discount',
            'discount',
            'is_free',
            'images',
        )


class SingleProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True, source='get_images')
    category = CategoryAndSubSerializer(many=False, read_only=True)
    files = FilesSerializer(many=True, read_only=True, source='get_files')
    sample_form_fields = ProductSampleFormFieldSerializer(many=True, read_only=True, source='get_sample_form_field')

    def get_user(self):
        r = self.context["request"]
        return r.user

    def _product_in_basket(self, obj):
        find = Basket.objects.filter(user=self.get_user(), product_id=obj.id)
        if find.exists():
            return True
        return False

    product_in_basket = serializers.SerializerMethodField('_product_in_basket')

    class Meta:
        model = Product
        fields = (
            'id',
            'title', 'description',
            'category', 'creator',
            'price', 'has_discount',
            'discount', 'is_free',
            'coupon', 'sample_form',
            'published', 'updated_at',
            'created_at', 'images',
            'gender', 'files',
            'sample_form_fields',
            'product_in_basket',
            'link_buy_direct', 'seller_name',
            'is_digital', 'for_student', 'for_teacher'
        )


class SampleFormsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleForms
        fields = ('id', 'title')


class SliderSerializer(serializers.ModelSerializer):
    @staticmethod
    def get_like_image(obj):
        return '/' + obj.image.url

    image = serializers.SerializerMethodField('get_like_image')

    class Meta:
        model = ShopSlider
        fields = '__all__'


class SampleFormsByGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleForms
        fields = ('id', 'title', 'groups')
        depth = 5


class BasketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Basket
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'
