from apps.shop.models import SampleFormFields, SampleFormsGroup


def make_sample_form_fields():
    """
    this script add value for sample form fields for product group
    """
    print("start " + "make_sample_form_fields()")
    try:
        # add product Specifications
        product_group = SampleFormsGroup.objects.get_or_create(title="مشخصات محصول")[0]
        SampleFormFields.objects.filter(sample_form_group=product_group).delete()
        for i in range(1, 48, 3):
            SampleFormFields.objects.create(
                title="موضوع",
                sample_form_group=product_group,
                presentation="Type" + str(i),
                type="text_box",
                order=i
            )
            SampleFormFields.objects.create(
                title="تعداد",
                sample_form_group=product_group,
                presentation="Count" + str(i),
                type="number",
                order=i+1
            )
            SampleFormFields.objects.create(
                title="توضیحات",
                sample_form_group=product_group,
                presentation="Description" + str(i),
                type="text_box",
                order=i+2
            )

        # add services Specifications
        product_group = SampleFormsGroup.objects.get_or_create(title="مشخصات خدمات")[0]
        SampleFormFields.objects.filter(sample_form_group=product_group).delete()
        for i in range(1, 48, 3):
            SampleFormFields.objects.create(
                title="موضوع",
                sample_form_group=product_group,
                presentation="Type" + str(i),
                type="text_box",
                order=i
            )
            SampleFormFields.objects.create(
                title="تعداد",
                sample_form_group=product_group,
                presentation="Count" + str(i),
                type="number",
                order=i+1
            )
            SampleFormFields.objects.create(
                title="توضیحات",
                sample_form_group=product_group,
                presentation="Description" + str(i),
                type="text_box",
                order=i+2
            )
    except Exception as ex:
        print("Exception" + "make_sample_form_fields()\r\n" + str(ex))
    else:
        print("Success Completed" + "make_sample_form_fields()")
