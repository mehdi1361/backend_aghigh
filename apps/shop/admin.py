from django.contrib import admin
# from django.contrib.admin.utils import flatten_fieldsets
from django.utils.translation import ugettext as _

from apps.shop.models import (
    ProductImage,
    ProductFile,
    # Coupon,
    # CouponCode,
    Category,
    Product,
    # ProductRate,
    Param,
    ProductComment,
    # ParamProductComment,
    # SumProductParam,
    # Basket,
    Invoice,
    InvoiceProduct,
    SampleForms,
    SampleFormsGroup,
    SampleFormFields,
    ProductSampleFormFields,
    ShopSlider,
)


class SampleFormFieldsAdminInline(admin.TabularInline):
    model = SampleFormFields
    extra = 0


class SampleFormsGroupAdmin(admin.ModelAdmin):
    inlines = [SampleFormFieldsAdminInline]
    list_display = ('title',)


class SampleFormsAdminInline(admin.StackedInline):
    model = SampleForms


class InvoiceProductInline(admin.StackedInline):
    model = InvoiceProduct
    extra = 0
    fields = ('title', "price")
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        # make all fields readonly
        readonly_fields = list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))
        return readonly_fields


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    extra = 0
    fields = ('image', 'image_tag')

    def get_readonly_fields(self, request, obj=None):
        return ['image_tag']


class ProductFileInline(admin.StackedInline):
    model = ProductFile
    extra = 0
    fields = ('file',)


class ProductSampleFormFieldsInline(admin.StackedInline):
    model = ProductSampleFormFields
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'deleted', 'updated_at', '_get_editor')
    inlines = [ProductImageInline, ProductFileInline, ProductSampleFormFieldsInline]
    readonly_fields = ('creator', 'editor')

    def _get_editor(self, obj):
        try:
            if obj.editor:
                return obj.editor.first_name + " " + obj.editor.last_name
            else:
                return ""
        except Exception as ex:
            pass

    _get_editor.short_description = _("Editor")


class ShopSliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'for_student', 'for_teacher')
    search_fields = ('title',)
    list_filter = ('gender',)
    fields = ('title', 'link', 'type', 'gender', 'for_student', 'for_teacher', 'image_tag', 'image')
    readonly_fields = ('image_tag',)


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('code', 'created_at')
    inlines = (InvoiceProductInline,)

    def get_readonly_fields(self, request, obj=None):
        # make all fields readonly
        readonly_fields = list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ))
        return readonly_fields


admin.site.register(SampleFormsGroup, SampleFormsGroupAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(ShopSlider, ShopSliderAdmin)
admin.site.register(SampleForms)

admin.site.register(Category)
admin.site.register(Param)
admin.site.register(ProductComment)
# admin.site.register(Coupon)
