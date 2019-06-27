import json

from apps.activity.models import *
from apps.activity.static import order_choice
from django.conf import settings


# def make_category_resanesh():
#     """
#     این اسکریپت برای ساخت ساختار جشنواره رسانش است
#     """
#     print("start " + "make_category_resanesh()")
#     try:
#
#         list_ad_field = []
#         departement_activity_category = Department.objects.get(title='برنامه های محوری')
#         ActivityCategory.objects.filter(title="جشنواره رسانش", slug='resanesh').delete()
#         activity_category = ActivityCategory.objects.create(title="جشنواره رسانش", slug='resanesh', status=True, max_count_activity=5, department=departement_activity_category, hide_in_list_app=True, hide_in_list_web=False)
#         list_ad_field.append({'دسته جشنواره رسانش': departement_activity_category.id})
#         print("activity_category id =" + str(departement_activity_category.id))
#         # activity_category.save()
#         additional_fields = AdditionalField.objects.filter(category=activity_category)
#         for additional in additional_fields:
#             DropDownFormSomeAdditionalField.objects.filter(additional_field=additional).delete()
#         additional_fields.delete()
#
#         # make group get id
#         group_additional_mokhatabin = GroupAdditionalFields.objects.create(label='مخاطبین', order=1, child_group=False, show_lable=True)
#
#         # group_additional_mokhatabin.save()
#
#         a = AdditionalField.objects.get_or_create(label='تعداد مخاطبین', order=1, field_type='number', category=activity_category, group=group_additional_mokhatabin, required=True)[0]
#         list_ad_field.append({'تعداد مخاطبین': a.id})
#         print("add field tedad mokhatabin =" + str(a.id))
#
#         a = aditional_field_no_mokhatabin = AdditionalField.objects.create(label='نوع مخاطبین', order=2, field_type='drop_down', category=activity_category, group=group_additional_mokhatabin, required=True)
#         list_ad_field.append({'نوع مخاطبین': a.id})
#         print("add field no mokhatabin =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=aditional_field_no_mokhatabin, )
#         list_ad_field.append({'نوع مخاطبین-سایر-مقدار': a.id})
#         print("add field no mokhatabin - sayer-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='اعضای انجمن', additional_field=aditional_field_no_mokhatabin, )
#         list_ad_field.append({'نوع مخاطبین-اعضای انجمن-مقدار': a.id})
#         print("add field no mokhatabin - azaye anjoman -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='اعضای هیات مرکزی', additional_field=aditional_field_no_mokhatabin, )
#         list_ad_field.append({'نوع مخاطبین-اعضای هیات مرکزی-مقدار': a.id})
#         print("add field no mokhatabin - azaye heyat markazi-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='عموم دانش آموزان', additional_field=aditional_field_no_mokhatabin, )
#         list_ad_field.append({'نوع مخاطبین-عموم دانش آموزان-مقدار': a.id})
#         print("add field no mokhatabin - omom danesh amozan -value =" + str(a.id))
#
#         a = aditional_field_hankar = AdditionalField.objects.create(label='تعداد همکار', order=3, field_type='drop_down', category=activity_category, group=group_additional_mokhatabin, required=False)
#         list_ad_field.append({'تعداد همکار': a.id})
#         print("add field tedad hamkar =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='۵', additional_field=aditional_field_hankar, )
#         list_ad_field.append({'تعدا همکار- ۵-مقدار': a.id})
#         print("add field tedad hamkar - 5 -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='۴', additional_field=aditional_field_hankar, )
#         list_ad_field.append({'تعدا همکار--مقدار۴': a.id})
#         print("add field tedad hamkar - 4 -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='۳', additional_field=aditional_field_hankar, )
#         list_ad_field.append({'تعدا همکار--مقدار۳': a.id})
#         print("add field tedad hamkar - 3 -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='۲', additional_field=aditional_field_hankar, )
#         list_ad_field.append({'تعدا همکار-۲-مقدار': a.id})
#         print("add field tedad hamkar - 2 -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='۱', additional_field=aditional_field_hankar, )
#         list_ad_field.append({'تعدا همکار-۱-مقدار': a.id})
#         print("add field tedad hamkar - 1 -value=" + str(a.id))
#
#         group_additional_masol = GroupAdditionalFields.objects.create(label='مسئول رسانه', order=2, child_group=False, show_lable=True)
#
#         a = AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_masol, required=True)
#         list_ad_field.append({'نام و نام خانوادگی- مسئول رسانه-مقدار': a.id})
#         print("add field name masol resaneh-value =" + str(a.id))
#
#         semat_anjaman = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_masol, required=True)
#         list_ad_field.append({'سمت در انجمن- مسئول رسانه-': semat_anjaman.id})
#         print("add field semat dar anjoman masol resaneh- =" + str(semat_anjaman.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman, )
#         list_ad_field.append({'سمت در انجمن- مسئول رسانه-عضو فعال-مقدار': a.id})
#         print("add field semat dar anjoman - masol resaneh- ozv faal-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman, )
#         list_ad_field.append({'سمت در انجمن- مسئول رسانه-مسئول واحد علمی درسی-مقدار': a.id})
#         print("add field semat dar anjoman - masol resaneh- masol elmi -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman, )
#         list_ad_field.append({'سمت در انجمن- مسئول رسانه-مسئول واحد فرهنگی-مقدار': a.id})
#         print("add field semat dar anjoman - masol resaneh- masol farhangi-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman, )
#         list_ad_field.append({'سمت در انجمن- مسئول رسانه-مسئول انجمن اسلامی-مقدار': a.id})
#         print("add field semat dar anjoman - masol resaneh- masol anjoman -value=" + str(a.id))
#
#         paye_tahsili = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_masol, required=True)
#         list_ad_field.append({'پایه تحصیلی-مسئول رسانه': paye_tahsili.id})
#         print("add field paye tahsili- masol resaneh =" + str(paye_tahsili.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili, )
#         list_ad_field.append({'پایه تحصیلی-پایه ۱۲-مقدار': a.id})
#         print("add value paye tahsili 12- masol resaneh -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili, )
#         list_ad_field.append({'پایه تحصیلی-پایه 11-مقدار': a.id})
#         print("add value paye tahsili 11- masol resaneh -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili, )
#         list_ad_field.append({'پایه تحصیلی-پایه 10-مقدار': a.id})
#         print("add value paye tahsili 10- masol resaneh -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_masol, required=False)
#         list_ad_field.append({'سمت در رسانه- مسئول رسانه': a.id})
#         print("add field semat dar resane masol resaneh =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_masol, required=False)
#         list_ad_field.append({'میزان فعالیت ساعت- مسئول رسانه': a.id})
#         print("add field saat masol resaneh =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_masol, required=False)
#         list_ad_field.append({'شرح وظایف- مسئول رسانه': a.id})
#         print("add field sharh vazaef masol resaneh =" + str(a.id))
#
#         group_additional_ozv1 = GroupAdditionalFields.objects.create(label='عضو ۱ رسانه', order=3, child_group=False, show_lable=True)
#
#         a = AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv1, required=False)
#         list_ad_field.append({'نام و نام خانوادگی- عضو۱': a.id})
#         print("add field name ozv1 =" + str(a.id))
#
#         semat_anjaman1 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv1, required=False)
#         list_ad_field.append({'سمت در انجمن- عضو۱-': semat_anjaman1.id})
#         print("add field semat dar anjoman ozv1- =" + str(semat_anjaman1.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman1, )
#         list_ad_field.append({'سمت در انجمن- عضو۱ -عضو فعال-مقدار': a.id})
#         print("add field semat dar anjoman -ozv1- ozv faal -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman1, )
#         list_ad_field.append({'سمت در انجمن-- عضو۱ -مسئول واحد علمی درسی-مقدار': a.id})
#         print("add field semat dar anjoman -ozv1- masol elmi -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman1, )
#         list_ad_field.append({'سمت در انجمن-- عضو۱ -مسئول واحد فرهنگی-مقدار': a.id})
#         print("add field semat dar anjoman-ozv1 - masol farhangi -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman1, )
#         list_ad_field.append({'سمت در انجمن-- عضو۱ -مسئول انجمن اسلامی-مقدار': a.id})
#         print("add field semat dar anjoman -ozv1 - masol anjoman -value=" + str(a.id))
#
#         paye_tahsili1 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv1, required=False)
#         list_ad_field.append({'پایه تحصیلی-عضو 1': paye_tahsili1.id})
#         print("add field paye tahsili- ozv 1 =" + str(paye_tahsili1.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili1, )
#         list_ad_field.append({'پایه تحصیلی عضو۱-پایه ۱۲-مقدار': a.id})
#         print("add value paye tahsili 12- ozv1 -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili1, )
#         list_ad_field.append({'پایه تحصیلی عضو۱-پایه 11-مقدار': a.id})
#         print("add value paye tahsili 11- ozv1 -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili1, )
#         list_ad_field.append({'پایه تحصیلی عضو۱-پایه 10-مقدار': a.id})
#         print("add value paye tahsili 10- ozv1 -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv1, required=False)
#         list_ad_field.append({'سمت در رسانه-  عضو۱': a.id})
#         print("add field semat dar resane ozv1 =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv1, required=False)
#         list_ad_field.append({'میزان فعالیت ساعت- عضو1': a.id})
#         print("add field saat ozv1 =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv1, required=False)
#         list_ad_field.append({'شرح وظایف- عضو۱': a.id})
#         print("add field sharh vazaef ozv1 =" + str(a.id))
#
#         group_additional_ozv2 = GroupAdditionalFields.objects.create(label='عضو ۲ رسانه', order=4, child_group=False, show_lable=True)
#
#         a = AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv2, required=False)
#         list_ad_field.append({'نام و نام خانوادگی- عضو۲': a.id})
#         print("add field name -ozv2 =" + str(a.id))
#
#         semat_anjaman2 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv2, required=False)
#         list_ad_field.append({'سمت در انجمن- عضو2-': semat_anjaman2.id})
#         print("add field semat dar anjoman ozv2- =" + str(semat_anjaman2.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman2, )
#         list_ad_field.append({'سمت در انجمن- عضو۲-عضو فعال-مقدار': a.id})
#         print("add field semat dar anjoman - ozv2- ozv faal-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman2, )
#         list_ad_field.append({'سمت در انجمن- عضو۲-مسئول واحد علمی درسی-مقدار': a.id})
#         print("add field semat dar anjoman - ozv2- masol elmi -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman2, )
#         list_ad_field.append({'سمت در انجمن- عضو۲-مسئول واحد فرهنگی-مقدار': a.id})
#         print("add field semat dar anjoman - ozv2- masol farhangi-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman2, )
#         list_ad_field.append({'سمت در انجمن- عضو۲-مسئول انجمن اسلامی-مقدار': a.id})
#         print("add field semat dar anjoman - ozv2- masol anjoman -value=" + str(a.id))
#
#         paye_tahsili2 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv2, required=False)
#         list_ad_field.append({'پایه تحصیلی-عضو 2': paye_tahsili2.id})
#         print("add field paye tahsili- ozv 2 =" + str(paye_tahsili2.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili2, )
#         list_ad_field.append({'پایه تحصیلی عضو2-پایه ۱۲-مقدار': a.id})
#         print("add value paye tahsili 12- ozv2 -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili2, )
#         list_ad_field.append({'پایه تحصیلی عضو2-پایه 11-مقدار': a.id})
#         print("add value paye tahsili 11- ozv2 -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili2, )
#         list_ad_field.append({'پایه تحصیلی عضو2-پایه 10-مقدار': a.id})
#         print("add value paye tahsili 10- ozv2 -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv2, required=False)
#         list_ad_field.append({'سمت در رسانه-  عضو2': a.id})
#         print("add field semat dar resane ozv2 =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv2, required=False)
#         list_ad_field.append({'میزان فعالیت ساعت- عضو2': a.id})
#         print("add field saat ozv2 =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv2, required=False)
#         list_ad_field.append({'شرح وظایف- عضو2': a.id})
#         print("add field sharh vazaef ozv2 =" + str(a.id))
#
#         group_additional_ozv3 = GroupAdditionalFields.objects.create(label='عضو ۳ رسانه', order=5, child_group=False, show_lable=True)
#         a = AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv3, required=False)
#         list_ad_field.append({'نام و نام خانوادگی- عضو3': a.id})
#         print("add field name -ozv3 =" + str(a.id))
#
#         semat_anjaman3 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv3, required=False)
#         list_ad_field.append({'سمت در انجمن- عضو3-': semat_anjaman3.id})
#         print("add field semat dar anjoman ozv3- =" + str(semat_anjaman3.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman3, )
#         list_ad_field.append({'سمت در انجمن- عضو۳-عضو فعال-مقدار': a.id})
#         print("add field semat dar anjoman - ozv۳- ozv faal-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman3, )
#         list_ad_field.append({'سمت در انجمن- عضو3-مسئول واحد علمی درسی-مقدار': a.id})
#         print("add field semat dar anjoman - ozv3- masol elmi -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman3, )
#         list_ad_field.append({'سمت در انجمن- عضو3-مسئول واحد فرهنگی-مقدار': a.id})
#         print("add field semat dar anjoman - ozv3- masol farhangi-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman3, )
#         list_ad_field.append({'سمت در انجمن- عضو3-مسئول انجمن اسلامی-مقدار': a.id})
#         print("add field semat dar anjoman - ozv3- masol anjoman -value=" + str(a.id))
#
#         paye_tahsili3 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv3, required=False)
#         list_ad_field.append({'پایه تحصیلی-عضو 3': paye_tahsili3.id})
#         print("add field paye tahsili- ozv 3 =" + str(paye_tahsili3.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili3, )
#         list_ad_field.append({'پایه تحصیلی عضو3-پایه ۱۲-مقدار': a.id})
#         print("add value paye tahsili 12- ozv3 -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili3, )
#         list_ad_field.append({'پایه تحصیلی عضو3-پایه 11-مقدار': a.id})
#         print("add value paye tahsili 11- ozv3 -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili3, )
#         list_ad_field.append({'پایه تحصیلی عضو3-پایه 10-مقدار': a.id})
#         print("add value paye tahsili 10- ozv3 -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv3, required=False)
#         list_ad_field.append({'سمت در رسانه-  عضو3': a.id})
#         print("add field semat dar resane ozv3 =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv3, required=False)
#         list_ad_field.append({'میزان فعالیت ساعت- عضو3': a.id})
#         print("add field saat ozv3 =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv3, required=False)
#         list_ad_field.append({'شرح وظایف- عضو3': a.id})
#         print("add field sharh vazaef ozv3 =" + str(a.id))
#
#         group_additional_ozv4 = GroupAdditionalFields.objects.create(label='عضو ۴ رسانه', order=6, child_group=False, show_lable=True)
#         a = AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv4, required=False)
#         list_ad_field.append({'نام و نام خانوادگی- عضو4': a.id})
#         print("add field name -ozv4 =" + str(a.id))
#
#         semat_anjaman4 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv4, required=False)
#         list_ad_field.append({'سمت در انجمن- عضو4-': semat_anjaman4.id})
#         print("add field semat dar anjoman ozv4- =" + str(semat_anjaman4.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman4, )
#         list_ad_field.append({'سمت در انجمن- عضو4-عضو فعال-مقدار': a.id})
#         print("add field semat dar anjoman - ozv4- ozv faal-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman4, )
#         list_ad_field.append({'سمت در انجمن- عضو4-مسئول واحد علمی درسی-مقدار': a.id})
#         print("add field semat dar anjoman - ozv4- masol elmi -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman4, )
#         list_ad_field.append({'سمت در انجمن- عضو4-مسئول واحد فرهنگی-مقدار': a.id})
#         print("add field semat dar anjoman - ozv4- masol farhangi-value =" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman4, )
#         list_ad_field.append({'سمت در انجمن- عضو4-مسئول انجمن اسلامی-مقدار': a.id})
#         print("add field semat dar anjoman - ozv4- masol anjoman -value=" + str(a.id))
#
#         paye_tahsili4 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv4, required=False)
#         list_ad_field.append({'پایه تحصیلی-عضو ۴': paye_tahsili4.id})
#         print("add field paye tahsili- ozv 4 =" + str(paye_tahsili4.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili4, )
#         list_ad_field.append({'پایه تحصیلی عضو4-پایه ۱۲-مقدار': a.id})
#         print("add value paye tahsili 12- ozv4 -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili4, )
#         list_ad_field.append({'پایه تحصیلی عضو4-پایه 11-مقدار': a.id})
#         print("add value paye tahsili 11- ozv4 -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili4, )
#         list_ad_field.append({'پایه تحصیلی عضو4-پایه ۱۲-مقدار': a.id})
#         print("add value paye tahsili 12- ozv4 -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv4, required=False)
#         list_ad_field.append({'سمت در رسانه-  عضو4': a.id})
#         print("add field semat dar resane ozv4 =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv4, required=False)
#         list_ad_field.append({'میزان فعالیت ساعت- عضو۴': a.id})
#         print("add field saat ozv4 =" + str(a.id))
#
#         a = AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv4, required=False)
#         list_ad_field.append({'شرح وظایف- عضو۴': a.id})
#         print("add field sharh vazaef ozv۴ =" + str(a.id))
#
#         group_additional_khalagh = GroupAdditionalFields.objects.create(label='ایده خلاق', order=7, child_group=False, show_lable=True)
#
#         a = AdditionalField.objects.create(label='فایل ایده خلاق', order=1, field_type='file_upload', category=activity_category, group=group_additional_khalagh, required=False, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#         list_ad_field.append({'فایل ایده خلاق۴': a.id})
#         print("add field file ideh khalagh = " + str(a.id))
#
#         group_additional_type_nashriat = GroupAdditionalFields.objects.create(label='نشریات', order=9, child_group=True, show_lable=True)
#
#         no_nashreye = AdditionalField.objects.create(label='نوع نشریات', order=1, field_type='drop_down', category=activity_category, group=group_additional_type_nashriat, required=True)
#         list_ad_field.append({'نوع نشریات': no_nashreye.id})
#         print("add field neo nashreye = " + str(no_nashreye.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='روزنامه دیواری', additional_field=no_nashreye, )
#         list_ad_field.append({'نوع نشریات-روزنامه دیواری-مقدار': a.id})
#         print("add value type nashreye- rozname divari -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='اینفوگرافیک', additional_field=no_nashreye, )
#         list_ad_field.append({'نوع نشریات-اینفوگرافیک-مقدار': a.id})
#         print("add value type nashreye- info graphic -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='نشریه الکترونیک', additional_field=no_nashreye, )
#         list_ad_field.append({'نوع نشریات-نشریه الکترونیک-مقدار': a.id})
#         print("add value type nashreye- nashreye electronic -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='نشریه مجلد', additional_field=no_nashreye, )
#         list_ad_field.append({'نوع نشریات-نشریه مجلد-مقدار': a.id})
#         print("add value type nashreye- nashreye mojalad -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='تک برگی', additional_field=no_nashreye, )
#         list_ad_field.append({'نوع نشریات-تک برگی-مقدار': a.id})
#         print("add value type nashreye- tak bargi -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='فایل های نشریه', order=2, field_type='file_upload', category=activity_category, group=group_additional_type_nashriat, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#         list_ad_field.append({'فایل های نشریه': a.id})
#         print("add field file nashreye = " + str(a.id))
#
#         group_additional_type_sound = GroupAdditionalFields.objects.create(label='قطعه صوتی', order=10, child_group=True, show_lable=True)
#         no_sound = AdditionalField.objects.create(label='نوع قطعه صوتی', order=1, field_type='drop_down', category=activity_category, group=group_additional_type_sound, required=True)
#         list_ad_field.append({'نوع قطعه صوتی': no_sound.id})
#         print("add value type sound=" + str(no_sound.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='پادکست', additional_field=no_sound, )
#         list_ad_field.append({'نوع قطعه صوتی-پادکست-مقدار': a.id})
#         print("add value type sound- padcast -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='رادیو مدرسه', additional_field=no_sound, )
#         list_ad_field.append({'نوع قطعه صوتی-رادیو مدرسه-مقدار': a.id})
#         print("add value type sound- radio madrese -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='فایل قطعه صوتی', order=2, field_type='file_upload', category=activity_category, group=group_additional_type_sound, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#         list_ad_field.append({'فایل قطعه صوتی': a.id})
#         print("add field file sound = " + str(a.id))
#
#         group_additional_type_social_media = GroupAdditionalFields.objects.create(label='شبکه اجتماعی', order=13, child_group=True, show_lable=True)
#
#         type_social_media1 = AdditionalField.objects.create(label='نوع شبکه اجتماعی۱', order=1, field_type='drop_down', category=activity_category, group=group_additional_type_social_media, required=True)
#         list_ad_field.append({'نوع شبکه اجتماعی۱': type_social_media1.id})
#         print("add field type social 1 = " + str(type_social_media1.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=type_social_media1, )
#         list_ad_field.append({'نوع شبکه اجتماعی۱-سایر-مقدار': a.id})
#         print("add value type social1- other -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='گپ', additional_field=type_social_media1, )
#         list_ad_field.append({'نوع شبکه اجتماعی۱-گپ-مقدار': a.id})
#         print("add value type social1- gap -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='ایتا', additional_field=type_social_media1, )
#         list_ad_field.append({'نوع شبکه اجتماعی۱-ایتا-مقدار': a.id})
#         print("add value type social1- eitaa -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سروش', additional_field=type_social_media1, )
#         list_ad_field.append({'نوع شبکه اجتماعی۱-سروش-مقدار': a.id})
#         print("add value type social1- soroush -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='آدرس کانال۱', order=2, field_type='text_box', category=activity_category, group=group_additional_type_social_media, required=True)
#         list_ad_field.append({'آدرس کانال۱': a.id})
#         print("add field address channel1 = " + str(a.id))
#
#         type_social_media2 = AdditionalField.objects.create(label='نوع شبکه اجتماعی۲', order=3, field_type='drop_down', category=activity_category, group=group_additional_type_social_media, required=False)
#         list_ad_field.append({'نوع شبکه اجتماعی2': type_social_media2.id})
#         print("add field type social 2 = " + str(type_social_media2.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=type_social_media2, )
#         list_ad_field.append({'نوع شبکه اجتماعی2-سایر-مقدار': a.id})
#         print("add value type social2- other -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='گپ', additional_field=type_social_media2, )
#         list_ad_field.append({'نوع شبکه اجتماعی2-گپ-مقدار': a.id})
#         print("add value type social2- gap -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='ایتا', additional_field=type_social_media2, )
#         list_ad_field.append({'نوع شبکه اجتماعی2-ایتا-مقدار': a.id})
#         print("add value type social2- eitaa -value=" + str(a.id))
#         a = DropDownFormSomeAdditionalField.objects.create(value='سروش', additional_field=type_social_media2, )
#         list_ad_field.append({'نوع شبکه اجتماعی2-سروش-مقدار': a.id})
#         print("add value type social2- soroush -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='آدرس کانال۲', order=4, field_type='text_box', category=activity_category, group=group_additional_type_social_media, required=False)
#         list_ad_field.append({'آدرس کانال2': a.id})
#         print("add field address channel2 = " + str(a.id))
#
#         type_social_media3 = AdditionalField.objects.create(label='نوع شبکه اجتماعی۳', order=5, field_type='drop_down', category=activity_category, group=group_additional_type_social_media, required=False)
#         list_ad_field.append({'نوع شبکه اجتماعی3': type_social_media3.id})
#         print("add field type social 3 = " + str(type_social_media3.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=type_social_media3, )
#         list_ad_field.append({'نوع شبکه اجتماعی3-سایر-مقدار': a.id})
#         print("add value type social3- other -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='گپ', additional_field=type_social_media3, )
#         list_ad_field.append({'نوع شبکه اجتماعی3-گپ-مقدار': a.id})
#         print("add value type social3- gap -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='ایتا', additional_field=type_social_media3, )
#         list_ad_field.append({'نوع شبکه اجتماعی3-ایتا-مقدار': a.id})
#         print("add value type social3- eitaa -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سروش', additional_field=type_social_media3, )
#         list_ad_field.append({'نوع شبکه اجتماعی3-سروش-مقدار': a.id})
#         print("add value type social3- soroush -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='آدرس کانال۳', order=6, field_type='text_box', category=activity_category, group=group_additional_type_social_media, required=False)
#         list_ad_field.append({'آدرس کانال3': a.id})
#         print("add field address channel3 = " + str(a.id))
#
#         type_social_media4 = AdditionalField.objects.create(label='نوع شبکه اجتماعی۴', order=7, field_type='drop_down', category=activity_category, group=group_additional_type_social_media, required=False)
#         list_ad_field.append({'نوع شبکه اجتماعی4': type_social_media4.id})
#         print("add field type social 4 = " + str(type_social_media4.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=type_social_media4, )
#         list_ad_field.append({'نوع شبکه اجتماعی4-سایر-مقدار': a.id})
#         print("add value type social4- other -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='گپ', additional_field=type_social_media4, )
#         list_ad_field.append({'نوع شبکه اجتماعی4-گپ-مقدار': a.id})
#         print("add value type social4- gap -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='ایتا', additional_field=type_social_media4, )
#         list_ad_field.append({'نوع شبکه اجتماعی4-ایتا-مقدار': a.id})
#         print("add value type social4- eitaa -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سروش', additional_field=type_social_media4, )
#         list_ad_field.append({'نوع شبکه اجتماعی4-سروش-مقدار': a.id})
#         print("add value type social4- soroush -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='آدرس کانال۴', order=8, field_type='text_box', category=activity_category, group=group_additional_type_social_media, required=False)
#         list_ad_field.append({'آدرس کانال4': a.id})
#         print("add field address channel4 = " + str(a.id))
#
#         type_social_media5 = AdditionalField.objects.create(label='نوع شبکه اجتماعی۵', order=9, field_type='drop_down', category=activity_category, group=group_additional_type_social_media, required=False)
#         list_ad_field.append({'نوع شبکه اجتماعی5': type_social_media5.id})
#         print("add field type social 5 = " + str(type_social_media5.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=type_social_media5, )
#         list_ad_field.append({'نوع شبکه اجتماعی5-سایر-مقدار': a.id})
#         print("add value type social5- sayer -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='گپ', additional_field=type_social_media5, )
#         list_ad_field.append({'نوع شبکه اجتماعی5-گپ-مقدار': a.id})
#         print("add value type social5- gap -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='ایتا', additional_field=type_social_media5, )
#         list_ad_field.append({'نوع شبکه اجتماعی5-ایتا-مقدار': a.id})
#         print("add value type social5- eitaa -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سروش', additional_field=type_social_media5, )
#         list_ad_field.append({'نوع شبکه اجتماعی5-سروش-مقدار': a.id})
#         print("add value type social5- soroush -value=" + str(a.id))
#
#         a = AdditionalField.objects.create(label='آدرس کانال۵', order=10, field_type='text_box', category=activity_category, group=group_additional_type_social_media, required=False)
#         list_ad_field.append({'آدرس کانال5': a.id})
#         print("add field address channel5 = " + str(a.id))
#
#         group_additional_type_site = GroupAdditionalFields.objects.create(label='سایت', order=14, child_group=True, show_lable=True)
#         a = AdditionalField.objects.create(label='آدرس سایت۱', order=1, field_type='text_box', category=activity_category, group=group_additional_type_site, required=True)
#         list_ad_field.append({'آدرس سایت۱': a.id})
#         print("add field address site1 = " + str(a.id))
#
#         a = AdditionalField.objects.create(label='آدرس سایت۲', order=2, field_type='text_box', category=activity_category, group=group_additional_type_site, required=False)
#         list_ad_field.append({'آدرس سایت2': a.id})
#         print("add field address site2 = " + str(a.id))
#
#         a = AdditionalField.objects.create(label='آدرس سایت۳', order=3, field_type='text_box', category=activity_category, group=group_additional_type_site, required=False)
#         list_ad_field.append({'آدرس سایت3': a.id})
#         print("add field address site3 = " + str(a.id))
#
#         group_additional_type_weblog = GroupAdditionalFields.objects.create(label='وبلاگ', order=15, child_group=True, show_lable=True)
#         a = AdditionalField.objects.create(label='آدرس وبلاگ۱', order=1, field_type='text_box', category=activity_category, group=group_additional_type_weblog, required=True)
#         list_ad_field.append({'آدرس وبلاگ1': a.id})
#         print("add field address weblog1 = " + str(a.id))
#
#         a = AdditionalField.objects.create(label='آدرس وبلاگ۲', order=2, field_type='text_box', category=activity_category, group=group_additional_type_weblog, required=False)
#         list_ad_field.append({'آدرس وبلاگ2': a.id})
#         print("add field address weblog2 = " + str(a.id))
#
#         a = AdditionalField.objects.create(label='آدرس وبلاگ۳', order=3, field_type='text_box', category=activity_category, group=group_additional_type_weblog, required=False)
#         list_ad_field.append({'آدرس وبلاگ3': a.id})
#         print("add field address weblog3 = " + str(a.id))
#
#         group_additional_type_soft = GroupAdditionalFields.objects.create(label='نرم‌افزار', order=18, child_group=True, show_lable=True)
#
#         a = AdditionalField.objects.create(label='فایل نرم‌افزار', order=1, field_type='file_upload', category=activity_category, group=group_additional_type_soft, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#         list_ad_field.append({'فایل نرم‌افزار': a.id})
#         print("add field file software = " + str(a.id))
#
#         group_additional_tablo = GroupAdditionalFields.objects.create(label='تابلو اعلانات', order=12, child_group=True, show_lable=True)
#         a = AdditionalField.objects.create(label='فایل تابلو اعلانات', order=1, field_type='file_upload', category=activity_category, group=group_additional_tablo, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1}, )
#         list_ad_field.append({'فایل فایل تابلو اعلانات': a.id})
#         print("add field file Tablo = " + str(a.id))
#
#         group_additional_type_cyber_space = GroupAdditionalFields.objects.create(label='فضای مجازی', order=17, child_group=True, show_lable=True)
#         no_cyber = AdditionalField.objects.create(label='نوع فضای مجازی', order=1, field_type='drop_down', category=activity_category, group=group_additional_type_cyber_space, required=True)
#         list_ad_field.append({'نوع فضای مجازی': no_cyber.id})
#         print("add field type cyber = " + str(no_cyber.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='نرم افزار', additional_field=no_cyber)
#         a.group_select.add(*[group_additional_type_soft.id])
#         list_ad_field.append({'نوع فضای مجازی-نرم افزار-مقدار': a.id})
#         print("add value type cyber- software -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='وبلاگ', additional_field=no_cyber)
#         a.group_select.add(*[group_additional_type_weblog.id])
#         list_ad_field.append({'نوع فضای مجازی-وبلاگ-مقدار': a.id})
#         print("add value type cyber- weblog -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سایت', additional_field=no_cyber)
#         a.group_select.add(*[group_additional_type_site.id])
#         list_ad_field.append({'نوع فضای مجازی-سایت-مقدار': a.id})
#         print("add value type cyber- site -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='شبکه اجتماعی', additional_field=no_cyber)
#         a.group_select.add(*[group_additional_type_social_media.id])
#         list_ad_field.append({'نوع فضای مجازی-شبکه اجتماعی-مقدار': a.id})
#         print("add value type cyber- social -value=" + str(a.id))
#
#         group_additional_type_resane = GroupAdditionalFields.objects.create(label='نوع رسانه', order=8, child_group=False, show_lable=False)
#         no_resane = AdditionalField.objects.create(label='نوع رسانه', order=1, field_type='drop_down', category=activity_category, group=group_additional_type_resane, required=True)
#         list_ad_field.append({'نوع رسانه': no_resane.id})
#         print("add field type resane = " + str(no_resane.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='تابلو اعلانات', additional_field=no_resane)
#         a.group_select.add(*[group_additional_tablo.id])
#         list_ad_field.append({'نوع رسانه-تابلو اعلانات-مقدار': a.id})
#         print("add value type resaneh- Tablo -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='قطعات صوتی', additional_field=no_resane)
#         a.group_select.add(*[group_additional_type_sound.id])
#         list_ad_field.append({'نوع رسانه-قطعات صوتی-مقدار': a.id})
#         print("add value type resaneh- sound -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='فضای مجازی', additional_field=no_resane)
#         a.group_select.add(*[group_additional_type_cyber_space.id])
#         list_ad_field.append({'نوع رسانه-فضای مجازی-مقدار': a.id})
#         print("add value type resaneh- cyber -value=" + str(a.id))
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='نشریات', additional_field=no_resane)
#         a.group_select.add(*[group_additional_type_nashriat.id])
#         list_ad_field.append({'نوع رسانه-نشریات-مقدار': a.id})
#         print("add value type resaneh- nashreyat -value=" + str(a.id))
#
#         f = open(settings.BASE_DIR + '/static/ResaneshAdditionalField.txt', 'w')
#         print(f)
#         for item in list_ad_field:
#             f.write(str(item) + '\n')
#         f.close()
#
#
#     except Exception as ex:
#         print("Exception" + "make_category_resanesh()\r\n" + str(ex))
#     else:
#         print("Success Compeleted" + "make_category_resanesh()")


# def make_category_enghelab():
#     """
#     این اسکریپت برای ساخت ساختار مدرسه انقلاب است
#     """
#     print("start " + "make_category_enghelab()")
#     try:
#
#         # Todo check for value title
#         departement_activity_category = Department.objects.get(title='برنامه های محوری')
#         ActivityCategory.objects.filter(slug="main_activity").delete()
#         activity_category = ActivityCategory.objects.create(title="فعالیت محوری", slug='main_activity', status=True, max_count_activity=5, department=departement_activity_category, hide_in_list_app=False, hide_in_list_web=False)
#
#         additional_fields = AdditionalField.objects.filter(category=activity_category)
#         for additional in additional_fields:
#             DropDownFormSomeAdditionalField.objects.filter(additional_field=additional).delete()
#         additional_fields.delete()
#
#         group_additional_mokhatabin = GroupAdditionalFields.objects.filter(label='مخاطبین', order=1, child_group=False, show_lable=True)
#
#         if group_additional_mokhatabin:
#             group_additional_mokhatabin = group_additional_mokhatabin[0]
#         else:
#             group_additional_mokhatabin = GroupAdditionalFields.objects.create(label='مخاطبین', order=1, child_group=False, show_lable=True)
#
#         AdditionalField.objects.create(label='تعداد مخاطبین', order=1, field_type='number', category=activity_category, group=group_additional_mokhatabin, required=True)
#
#         aditional_field_no_mokhatabin = AdditionalField.objects.create(label='نوع مخاطبین', order=2, field_type='drop_down', category=activity_category, group=group_additional_mokhatabin, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='عموم دانش آموزان', additional_field=aditional_field_no_mokhatabin, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='اعضای هیات مرکزی', additional_field=aditional_field_no_mokhatabin, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='اعضای انجمن', additional_field=aditional_field_no_mokhatabin, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=aditional_field_no_mokhatabin, )
#
#         aditional_field_hankar = AdditionalField.objects.create(label='تعداد همکار', order=3, field_type='drop_down', category=activity_category, group=group_additional_mokhatabin, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='۱', additional_field=aditional_field_hankar, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='۲', additional_field=aditional_field_hankar, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='۳', additional_field=aditional_field_hankar, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='۴', additional_field=aditional_field_hankar, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='5', additional_field=aditional_field_hankar, )
#
#         group_additional_masol = GroupAdditionalFields.objects.create(label='مسئول مدرسه انقلاب', order=2, child_group=False, show_lable=True)
#
#         AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_masol, required=True)
#
#         semat_anjaman = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_masol, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman, )
#
#         paye_tahsili = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_masol, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili, )
#
#         AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_masol, required=False)
#
#         AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_masol, required=False)
#
#         AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_masol, required=False)
#
#         group_additional_ozv1 = GroupAdditionalFields.objects.create(label='عضو ۱ انجمنی', order=3, child_group=False, show_lable=True)
#
#         AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv1, required=False)
#
#         semat_anjaman1 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv1, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman1, )
#
#         paye_tahsili1 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv1, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili1, )
#
#         AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv1, required=False)
#
#         AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv1, required=False)
#
#         AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv1, required=False)
#
#         group_additional_ozv2 = GroupAdditionalFields.objects.create(label='عضو ۲ انجمنی', order=4, child_group=False, show_lable=True)
#
#         AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv2, required=False)
#
#         semat_anjaman2 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv2, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman2)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman2)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman2)
#
#         DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman2)
#
#         paye_tahsili2 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv2, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili2, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili2, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili2, )
#
#         AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv2, required=False)
#
#         AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv2, required=False)
#
#         AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv2, required=False)
#
#         group_additional_ozv3 = GroupAdditionalFields.objects.create(label='عضو ۳ انجمنی', order=5, child_group=False, show_lable=True)
#         AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv3, required=False)
#
#         semat_anjaman3 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv3, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman3, )
#
#         paye_tahsili3 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv3, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili3, )
#
#         AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv3, required=False)
#
#         AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv3, required=False)
#
#         AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv3, required=False)
#
#         group_additional_ozv4 = GroupAdditionalFields.objects.create(label='عضو ۴ انجمنی', order=6, child_group=False, show_lable=True)
#         AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv4, required=False)
#
#         semat_anjaman4 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv4, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman4, )
#
#         paye_tahsili4 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv4, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili4, )
#
#         AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv4, required=False)
#
#         AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv4, required=False)
#
#         AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv4, required=False)
#
#         group_additional_ozv1 = GroupAdditionalFields.objects.create(label='عضو ۱ غیر انجمنی', order=7, child_group=False, show_lable=True)
#
#         AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv1, required=False)
#
#         semat_anjaman1 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv1, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman1, )
#
#         paye_tahsili1 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv1, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili1, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili1, )
#
#         AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv1, required=False)
#
#         AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv1, required=False)
#
#         AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv1, required=False)
#
#         group_additional_ozv2 = GroupAdditionalFields.objects.create(label='عضو ۲ غیر انجمنی', order=8, child_group=False, show_lable=True)
#
#         AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv2, required=False)
#
#         semat_anjaman2 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv2, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman2)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman2)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman2)
#
#         DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman2)
#
#         paye_tahsili2 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv2, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili2, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili2, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili2, )
#
#         AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv2, required=False)
#
#         AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv2, required=False)
#
#         AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv2, required=False)
#
#         group_additional_ozv3 = GroupAdditionalFields.objects.create(label='عضو ۳ غیر انجمنی', order=9, child_group=False, show_lable=True)
#         AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv3, required=False)
#
#         semat_anjaman3 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv3, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman3, )
#
#         paye_tahsili3 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv3, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili3, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili3, )
#
#         AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv3, required=False)
#
#         AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv3, required=False)
#
#         AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv3, required=False)
#
#         group_additional_ozv4 = GroupAdditionalFields.objects.create(label='عضو ۴ غیر انجمنی', order=10, child_group=False, show_lable=True)
#         AdditionalField.objects.create(label='نام و نام خانوادگی', order=1, field_type='text_box', category=activity_category, group=group_additional_ozv4, required=False)
#
#         semat_anjaman4 = AdditionalField.objects.create(label='سمت در انجمن', order=2, field_type='drop_down', category=activity_category, group=group_additional_ozv4, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول انجمن اسلامی', additional_field=semat_anjaman4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد فرهنگی', additional_field=semat_anjaman4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='مسئول واحد علمی درسی', additional_field=semat_anjaman4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='عضو فعال', additional_field=semat_anjaman4, )
#
#         paye_tahsili4 = AdditionalField.objects.create(label='پایه تحصیلی', order=3, field_type='drop_down', category=activity_category, group=group_additional_ozv4, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۰', additional_field=paye_tahsili4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۱', additional_field=paye_tahsili4, )
#
#         DropDownFormSomeAdditionalField.objects.create(value='پایه ۱۲', additional_field=paye_tahsili4, )
#
#         AdditionalField.objects.create(label='سمت در رسانه', order=4, field_type='text_box', category=activity_category, group=group_additional_ozv4, required=False)
#
#         AdditionalField.objects.create(label='میزان فعالیت ساعت', order=5, field_type='number', category=activity_category, group=group_additional_ozv4, required=False)
#
#         AdditionalField.objects.create(label='شرح وظایف', order=6, field_type='text_box', category=activity_category, group=group_additional_ozv4, required=False)
#
#         group_additional_sections = GroupAdditionalFields.objects.create(label='بخش ها', order=12, child_group=False, show_lable=True)
#
#         section_type = AdditionalField.objects.create(label='نوع بخش', order=1, field_type='drop_down', category=activity_category, group=group_additional_sections, required=True)
#
#         # for section exhibition
#
#         group_exhibit_location = GroupAdditionalFields.objects.create(label='مختصات نمایشگاه', order=13, child_group=True, show_lable=True)
#
#         AdditionalField.objects.create(label='تعداد غرفه ها', field_type='number', order=1, category=activity_category, group=group_exhibit_location, required=False)
#
#         location_place = AdditionalField.objects.create(label='محل برگزاری', field_type='drop_down', order=2, category=activity_category, group=group_exhibit_location, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='نماز خانه مدرسه', additional_field=location_place)
#         DropDownFormSomeAdditionalField.objects.create(value='حیات مدرسه', additional_field=location_place)
#         DropDownFormSomeAdditionalField.objects.create(value='سالن بین کلاس ها', additional_field=location_place)
#         DropDownFormSomeAdditionalField.objects.create(value='دفتر انجمن', additional_field=location_place)
#         DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=location_place)
#
#         group_exhibit_run = GroupAdditionalFields.objects.create(label='کادر اجرایی نمایشگاه', order=14, child_group=True, show_lable=True)
#
#         frame_type = AdditionalField.objects.create(label='نوع کادر', field_type='drop_down', order=1, category=activity_category, group=group_exhibit_run, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='اعضای عادی انجمن اسلامی', additional_field=frame_type)
#         DropDownFormSomeAdditionalField.objects.create(value='سایر تشکل های مدرسه', additional_field=frame_type)
#         DropDownFormSomeAdditionalField.objects.create(value='مربی قرارگاه', additional_field=frame_type)
#         DropDownFormSomeAdditionalField.objects.create(value='کادر مدرسه', additional_field=frame_type)
#         DropDownFormSomeAdditionalField.objects.create(value='خانواده', additional_field=frame_type)
#         DropDownFormSomeAdditionalField.objects.create(value='اعضای کادر اتحادیه', additional_field=frame_type)
#
#         group_features = GroupAdditionalFields.objects.create(label='بودجه و امکانات', order=15, child_group=True, show_lable=True)
#
#         features_options = AdditionalField.objects.create(label='دانش آموز', field_type='drop_down', order=1, category=activity_category, group=group_features, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='کمک نقدی', additional_field=features_options)
#         DropDownFormSomeAdditionalField.objects.create(value='کمک غیر نقدی', additional_field=features_options)
#
#         features_options = AdditionalField.objects.create(label='اتحادیه شهرستان', field_type='drop_down', order=2, category=activity_category, group=group_features, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='کمک نقدی', additional_field=features_options)
#         DropDownFormSomeAdditionalField.objects.create(value='کمک غیر نقدی', additional_field=features_options)
#
#         features_options = AdditionalField.objects.create(label='کادر مدرسه', field_type='drop_down', order=3, category=activity_category, group=group_features, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='کمک نقدی', additional_field=features_options)
#         DropDownFormSomeAdditionalField.objects.create(value='کمک غیر نقدی', additional_field=features_options)
#
#         features_options = AdditionalField.objects.create(label='خانواده', field_type='drop_down', order=4, category=activity_category, group=group_features, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='کمک نقدی', additional_field=features_options)
#         DropDownFormSomeAdditionalField.objects.create(value='کمک غیر نقدی', additional_field=features_options)
#
#         features_options = AdditionalField.objects.create(label='سایر تشکلها', field_type='drop_down', order=5, category=activity_category, group=group_features, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='کمک نقدی', additional_field=features_options)
#         DropDownFormSomeAdditionalField.objects.create(value='کمک غیر نقدی', additional_field=features_options)
#
#         group_drop_1 = GroupAdditionalFields.objects.create(label="کارنامه سیاه پهلوی", order=17, child_group=True)
#         drop_down_1 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_1, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='فساد اقتصادی', additional_field=drop_down_1)
#         DropDownFormSomeAdditionalField.objects.create(value='فساد سیاسی', additional_field=drop_down_1)
#         DropDownFormSomeAdditionalField.objects.create(value='وابستگی', additional_field=drop_down_1)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_drop_1, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_drop_1, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_drop_1, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_drop_2 = GroupAdditionalFields.objects.create(label="اسوه های انقلابی", order=17, child_group=True)
#         drop_down_2 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_2, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='شخصیت منحصر به فرد امام و اصحاب امام(ره)', additional_field=drop_down_2)
#         DropDownFormSomeAdditionalField.objects.create(value='شهدای شاخص شهر', additional_field=drop_down_2)
#         DropDownFormSomeAdditionalField.objects.create(value='برزگان انقلاب در شهر', additional_field=drop_down_2)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_drop_2, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_drop_2, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_drop_2, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_drop_3 = GroupAdditionalFields.objects.create(label="آفتاب ولایت", order=17, child_group=True)
#         drop_down_3 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_3, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='تبیین جایگاه ولایت فقیه', additional_field=drop_down_3)
#         DropDownFormSomeAdditionalField.objects.create(value='نقش آفرینی رهبری', additional_field=drop_down_3)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_drop_3, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_drop_3, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_drop_3, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_drop_3, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_drop_3, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_drop_3, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_drop_3, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_drop_3, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_drop_3, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_drop_4 = GroupAdditionalFields.objects.create(label="دیوار فریاد", order=17, child_group=True)
#         drop_down_4 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_4, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='دشمن شناسی', additional_field=drop_down_4)
#         DropDownFormSomeAdditionalField.objects.create(value='عرصه های نفوذ دشمن', additional_field=drop_down_4)
#         DropDownFormSomeAdditionalField.objects.create(value='راه های مقابله با دشمن', additional_field=drop_down_4)
#         DropDownFormSomeAdditionalField.objects.create(value='سراب غرب', additional_field=drop_down_4)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_drop_4, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_drop_4, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_drop_4, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_drop_4, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_drop_4, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_drop_4, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_drop_4, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_drop_4, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_drop_4, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_drop_5 = GroupAdditionalFields.objects.create(label="موج پنجم", order=17, child_group=True)
#         drop_down_5 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_5, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='تولید ملی و کالای ملی', additional_field=drop_down_5)
#         DropDownFormSomeAdditionalField.objects.create(value='سبک زندگی ایرانی', additional_field=drop_down_5)
#         DropDownFormSomeAdditionalField.objects.create(value='اسلامی', additional_field=drop_down_5)
#         DropDownFormSomeAdditionalField.objects.create(value='نقش انقلابی دهه هشتادی ها', additional_field=drop_down_5)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_drop_5, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_drop_5, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_drop_5, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_drop_5, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_drop_5, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_drop_5, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_drop_5, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_drop_5, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_drop_5, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_drop_6 = GroupAdditionalFields.objects.create(label="مجاهدان سایبری", order=17, child_group=True)
#         drop_down_6 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_6, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='فرصت های فضای مجازی', additional_field=drop_down_6)
#         DropDownFormSomeAdditionalField.objects.create(value='تهدیدهای فضای مجازی', additional_field=drop_down_6)
#         DropDownFormSomeAdditionalField.objects.create(value='راه های مقابله و چگونگی', additional_field=drop_down_6)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_drop_6, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_drop_6, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_drop_6, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_drop_6, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_drop_6, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_drop_6, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_drop_6, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_drop_6, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_drop_6, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_drop_7 = GroupAdditionalFields.objects.create(label="انصارالمهدی (عج)", order=17, child_group=True)
#         drop_down_7 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_7, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='ویژگی های منتظران', additional_field=drop_down_7)
#         DropDownFormSomeAdditionalField.objects.create(value='سیمای حکومت اسلامی عصر ظهور', additional_field=drop_down_7)
#         DropDownFormSomeAdditionalField.objects.create(value='اربعین حسینی زادگاه انصار المهدی (عج)', additional_field=drop_down_7)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_drop_7, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_drop_7, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_drop_7, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_drop_7, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_drop_7, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_drop_7, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_drop_7, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_drop_7, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_drop_7, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_booths = GroupAdditionalFields.objects.create(label="غرفه ها", order=16, child_group=True)
#         booth_drop_down = AdditionalField.objects.create(label='عنوان غرفه', field_type='drop_down', order=1, category=activity_category, group=group_booths, required=True)
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='کارنامه سیاه پهلوی', additional_field=booth_drop_down)
#         a.group_select.add(*[group_drop_1])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='اسوه های انقلابی', additional_field=booth_drop_down)
#         a.group_select.add(*[group_drop_2])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='آفتاب ولایت', additional_field=booth_drop_down)
#         a.group_select.add(*[group_drop_3])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='دیوار فریاد', additional_field=booth_drop_down)
#         a.group_select.add(*[group_drop_4])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='موج پنجم', additional_field=booth_drop_down)
#         a.group_select.add(*[group_drop_5])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مجاهدان سایبری', additional_field=booth_drop_down)
#         a.group_select.add(*[group_drop_6])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='انصارالمهدی (عج)', additional_field=booth_drop_down)
#         a.group_select.add(*[group_drop_7])
#
#         group_drop_1 = GroupAdditionalFields.objects.create(label="چهل برگ", order=19, child_group=True)
#         drop_down_1 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_1, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='میز پاسخگویی به شبهات انقلاب اسلامی', additional_field=drop_down_1)
#         DropDownFormSomeAdditionalField.objects.create(value='پویش ملی شتر درخواب بیند پنبه دانه', additional_field=drop_down_1)
#         DropDownFormSomeAdditionalField.objects.create(value='دستاوردهای معنوی انقلاب', additional_field=drop_down_1)
#         DropDownFormSomeAdditionalField.objects.create(value='چهل سال چالش', additional_field=drop_down_1)
#         DropDownFormSomeAdditionalField.objects.create(value='چهل سال پیروزی', additional_field=drop_down_1)
#         DropDownFormSomeAdditionalField.objects.create(value='خرمشهر ها در پیش است', additional_field=drop_down_1)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_drop_1, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_drop_1, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_drop_1, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_drop_1, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_drop_2 = GroupAdditionalFields.objects.create(label="هویت بانوی مسلمان", order=19, child_group=True)
#         drop_down_2 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_2, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='ضریح بی نشان', additional_field=drop_down_2)
#         DropDownFormSomeAdditionalField.objects.create(value='الگوی سوم زن', additional_field=drop_down_2)
#         DropDownFormSomeAdditionalField.objects.create(value='جاهلیت مدرن', additional_field=drop_down_2)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_drop_2, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_drop_2, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_drop_2, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_drop_2, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#         # ==========================
#         group_design = GroupAdditionalFields.objects.create(label="طراحی غرفه", order=20, child_group=True)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_design, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_design, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_design, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_design, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_design, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_design, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_design, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_design, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_design, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#         # =========================
#         group_race = GroupAdditionalFields.objects.create(label="مسابقه", order=20, child_group=True)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_race, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_race, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_race, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_race, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_race, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_race, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_race, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_race, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_race, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         # =========================
#         group_play = GroupAdditionalFields.objects.create(label="بازی", order=20, child_group=True)
#
#         AdditionalField.objects.create(label='مسئول غرفه', field_type='text_box', order=2, category=activity_category, group=group_play, required=False)
#
#         AdditionalField.objects.create(label='راوی غرفه', field_type='text_box', order=3, category=activity_category, group=group_play, required=False)
#
#         AdditionalField.objects.create(label='سایر توضیحات', field_type='text_box', order=4, category=activity_category, group=group_play, required=False)
#
#         AdditionalField.objects.create(label='معرفی کتاب', order=5, field_type='file_upload', category=activity_category, group=group_play, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='منابع ماخذ', order=6, field_type='file_upload', category=activity_category, group=group_play, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس', order=7, field_type='file_upload', category=activity_category, group=group_play, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='صوت', order=8, field_type='file_upload', category=activity_category, group=group_play, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فیلم', order=9, field_type='file_upload', category=activity_category, group=group_play, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=10, field_type='file_upload', category=activity_category, group=group_play, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_drop_3 = GroupAdditionalFields.objects.create(label="آیه سال", order=19, child_group=True)
#         drop_down_3 = AdditionalField.objects.create(label='موضوعات', field_type='drop_down', order=1, category=activity_category, group=group_drop_3, required=True)
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='طراحی غرفه', additional_field=drop_down_3)
#         a.group_select.add(*[group_design])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='مسابقه', additional_field=drop_down_3)
#         a.group_select.add(*[group_race])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='بازی', additional_field=drop_down_3)
#         a.group_select.add(*[group_play])
#
#         group_special_section = GroupAdditionalFields.objects.create(label="بخش ویژه", order=18, child_group=True)
#         special_section_drop_down = AdditionalField.objects.create(label='عنوان بخش', field_type='drop_down', order=1, category=activity_category, group=group_special_section, required=True)
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='چهل برگ ', additional_field=special_section_drop_down)
#         a.group_select.add(*[group_drop_1])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='هویت بانوی مسلمان', additional_field=special_section_drop_down)
#         a.group_select.add(*[group_drop_2])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='آیه سال', additional_field=special_section_drop_down)
#         a.group_select.add(*[group_drop_3])
#
#         group_holding_model = GroupAdditionalFields.objects.create(label="مدل برگزاری", order=21, child_group=True)
#         drop_down_holding_model = AdditionalField.objects.create(label='نوع تبلیغات', field_type='drop_down', order=1, category=activity_category, group=group_holding_model, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='کارت دعوت', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='پوستر', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='چهره به چهره', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='صبحگاه مدرسه', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='وبلاگ', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='کانال', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='بروشور', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='پیامک', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='نصب بنر', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='تابلو اعلانات انجمن', additional_field=drop_down_holding_model)
#         DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=drop_down_holding_model)
#
#         group_help_teacher = GroupAdditionalFields.objects.create(label='استفاده از استاد راهنمای تاریخ', order=22, child_group=True, show_lable=True)
#
#         AdditionalField.objects.create(label='مصاحبه', field_type='text_box', order=1, category=activity_category, group=group_help_teacher, required=False)
#
#         AdditionalField.objects.create(label='مصاحبه شونده', field_type='text_box', order=2, category=activity_category, group=group_help_teacher, required=False)
#
#         group_arts_others = GroupAdditionalFields.objects.create(label='استفاده از سایر هنر ها', order=23, child_group=True, show_lable=True)
#         drop_down_arts_others = AdditionalField.objects.create(label='نوع هنر', field_type='drop_down', order=1, category=activity_category, group=group_arts_others, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='هنرهای دستی', additional_field=drop_down_arts_others)
#         DropDownFormSomeAdditionalField.objects.create(value='هنرهای نمایشی', additional_field=drop_down_arts_others)
#         DropDownFormSomeAdditionalField.objects.create(value='هنرهای تجسمی', additional_field=drop_down_arts_others)
#         DropDownFormSomeAdditionalField.objects.create(value='سایر هنرها', additional_field=drop_down_arts_others)
#
#         AdditionalField.objects.create(label='توضیحات', field_type='text_box', order=2, category=activity_category, group=group_arts_others, required=False)
#
#         group_inside_and_out_side = GroupAdditionalFields.objects.create(label='فضاسازی داخل و خارج نمایشگاه', order=24, child_group=True, show_lable=True)
#         drop_down_inside_and_out_side = AdditionalField.objects.create(label='نوع فضاسازی', field_type='drop_down', order=1, category=activity_category, group=group_inside_and_out_side, required=True)
#
#         DropDownFormSomeAdditionalField.objects.create(value='نور پردازی', additional_field=drop_down_inside_and_out_side)
#         DropDownFormSomeAdditionalField.objects.create(value='صداپردازی', additional_field=drop_down_inside_and_out_side)
#         DropDownFormSomeAdditionalField.objects.create(value='سازه نمایشگاهی', additional_field=drop_down_inside_and_out_side)
#         DropDownFormSomeAdditionalField.objects.create(value='عناوین غرفه ها', additional_field=drop_down_inside_and_out_side)
#         DropDownFormSomeAdditionalField.objects.create(value='سایر', additional_field=drop_down_inside_and_out_side)
#
#         AdditionalField.objects.create(label='توضیحات', field_type='text_box', order=2, category=activity_category, group=group_inside_and_out_side, required=False)
#
#         group_khalagh = GroupAdditionalFields.objects.create(label='ایده ها و مسابقه ها', order=25, child_group=True, show_lable=True)
#
#         AdditionalField.objects.create(label='ایده ها و مسابقه های بومی', order=1, field_type='file_upload', category=activity_category, group=group_khalagh, required=False, validate_data={'format': ['pdf', 'doc', 'docx'], 'min_file_size': -1, 'max_file_size': -1, 'min_file_count': -1, 'max_file_count': -1})
#         AdditionalField.objects.create(label='ایده ها و مسابقه های غیر بومی', order=1, field_type='file_upload', category=activity_category, group=group_khalagh, required=False, validate_data={'format': ['pdf', 'doc', 'docx'], 'min_file_size': -1, 'max_file_size': -1, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_organ_others = GroupAdditionalFields.objects.create(label='استفاده از ظرفیت سایر تشکل ها', order=26, child_group=True, show_lable=True)
#
#         AdditionalField.objects.create(label='تشکل', field_type='text_box', order=1, category=activity_category, group=group_organ_others, required=False)
#
#         AdditionalField.objects.create(label='نوع همکاری', field_type='text_box', order=2, category=activity_category, group=group_organ_others, required=False)
#
#         group_special = GroupAdditionalFields.objects.create(label='بازدیدکنندگان ویژه', order=27, child_group=True, show_lable=True)
#
#         AdditionalField.objects.create(label='نام', field_type='text_box', order=1, category=activity_category, group=group_special, required=False)
#
#         AdditionalField.objects.create(label='سمت', field_type='text_box', order=2, category=activity_category, group=group_special, required=False)
#
#         group_views = GroupAdditionalFields.objects.create(label='نظرسنجی بازدیدکنندگان', order=28, child_group=True, show_lable=True)
#
#         AdditionalField.objects.create(label='تعداد', field_type='number', order=1, category=activity_category, group=group_views, required=False)
#
#         AdditionalField.objects.create(label='مخاطبین', field_type='text_box', order=2, category=activity_category, group=group_views, required=False)
#
#         AdditionalField.objects.create(label='عکس', order=3, field_type='file_upload', category=activity_category, group=group_views, required=False, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='گزارش مکتو ب مصور', order=4, field_type='file_upload', category=activity_category, group=group_views, required=False, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_start_way = GroupAdditionalFields.objects.create(label='حضور در راهپیمایی', order=29, child_group=True, show_lable=True)
#         drop_down_group_main = AdditionalField.objects.create(label='نوع حضور', field_type='drop_down', order=1, category=activity_category, group=group_start_way, required=False)
#
#         DropDownFormSomeAdditionalField.objects.create(value='اجتماعی', additional_field=drop_down_group_main)
#         DropDownFormSomeAdditionalField.objects.create(value='فردی', additional_field=drop_down_group_main)
#
#         AdditionalField.objects.create(label='توضیحات', field_type='text_box', order=2, category=activity_category, group=group_start_way, required=False)
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='بخش نمایشگاهی', additional_field=section_type)
#         group_list = [
#             group_exhibit_location.id,
#             group_exhibit_run.id,
#             group_features.id,
#             group_booths.id,
#             group_special_section.id,
#             group_holding_model.id,
#             group_khalagh.id,
#             group_help_teacher.id,
#             group_arts_others.id,
#             group_inside_and_out_side.id,
#             group_organ_others.id,
#             group_special.id,
#             group_views.id,
#             group_start_way.id
#         ]
#         a.group_select.add(*group_list)
#
#         # for seen
#         group_seen = GroupAdditionalFields.objects.create(label="سرود", order=14, child_group=True)
#
#         AdditionalField.objects.create(label='فایل های ویدئویی', order=1, field_type='file_upload', category=activity_category, group=group_seen, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فایل های صوتی', order=2, field_type='file_upload', category=activity_category, group=group_seen, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس ها', order=3, field_type='file_upload', category=activity_category, group=group_seen, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فایل های متنی', order=4, field_type='file_upload', category=activity_category, group=group_seen, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         # for theater
#         group_theater = GroupAdditionalFields.objects.create(label="تئاتر", order=14, child_group=True)
#
#         AdditionalField.objects.create(label='فایل های ویدئویی', order=1, field_type='file_upload', category=activity_category, group=group_theater, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس ها', order=3, field_type='file_upload', category=activity_category, group=group_theater, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فایل های متنی', order=4, field_type='file_upload', category=activity_category, group=group_theater, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         # for short story
#         group_short_story = GroupAdditionalFields.objects.create(label="داستان کوتاه", order=14, child_group=True)
#
#         AdditionalField.objects.create(label='فایل های ویدئویی', order=1, field_type='file_upload', category=activity_category, group=group_short_story, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فایل های متنی', order=4, field_type='file_upload', category=activity_category, group=group_short_story, required=True, validate_data={'format': ['word'], 'min_file_size': -1, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         # for Revolutionary idea
#         group_revolutionary_idea = GroupAdditionalFields.objects.create(label="ایده های انقلابی", order=14, child_group=True)
#
#         AdditionalField.objects.create(label='فایل های ویدئویی', order=1, field_type='file_upload', category=activity_category, group=group_revolutionary_idea, required=True, validate_data={'format': ['mp4', 'avi'], 'min_file_size': -1, 'max_file_size': 102400, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فایل های صوتی', order=2, field_type='file_upload', category=activity_category, group=group_revolutionary_idea, required=True, validate_data={'format': ['mp3', 'wav', 'amr'], 'min_file_size': 2048, 'max_file_size': 20480, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='عکس ها', order=3, field_type='file_upload', category=activity_category, group=group_revolutionary_idea, required=True, validate_data={'format': ['jpg'], 'min_file_size': 10, 'max_file_size': 500, 'min_file_count': -1, 'max_file_count': -1})
#
#         AdditionalField.objects.create(label='فایل های متنی', order=4, field_type='file_upload', category=activity_category, group=group_revolutionary_idea, required=True, validate_data={'format': ['pdf'], 'min_file_size': 10, 'max_file_size': 300, 'min_file_count': -1, 'max_file_count': -1})
#
#         group_additional_select_title = GroupAdditionalFields.objects.create(label="عنوان", order=13, child_group=True)
#         select_title = AdditionalField.objects.create(label='انتخاب عنوان', order=1, field_type='drop_down', category=activity_category, group=group_additional_select_title, required=True)
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='سرود', additional_field=select_title)
#         a.group_select.add(*[group_seen.id])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='تئاتر', additional_field=select_title)
#         a.group_select.add(*[group_theater.id])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='داستان کوتاه', additional_field=select_title)
#         a.group_select.add(*[group_short_story.id])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='ایده های انقلابی', additional_field=select_title)
#         a.group_select.add(*[group_revolutionary_idea.id])
#
#         a = DropDownFormSomeAdditionalField.objects.create(value='غیر نمایشگاهی', additional_field=section_type)
#         a.group_select.add(*[group_additional_select_title.id])
#
#         # f = open(settings.BASE_DIR + '/static/ResaneshAdditionalField.txt', 'w')
#         # print(f)
#         # for item in list_ad_field:
#         #     f.write(str(item) + '\n')
#         # f.close()
#
#     except Exception as ex:
#         print("Exception" + "make_category_enghelab()\r\n" + str(ex))
#     else:
#         delete_extra_group()
#         print("Success Completed" + "make_category_enghelab()")


# def delete_extra_group():
#     extra_groups = 0
#     for group in GroupAdditionalFields.objects.all():
#         if not AdditionalField.objects.filter(group=group):
#             extra_groups += 1
#             group.delete()
#     print("extra_groups: " + str(extra_groups))
