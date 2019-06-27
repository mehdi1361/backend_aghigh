import xlwt
from django.db.models import Avg, Q
from apps.emtiaz.compute import ComputingPoint
from apps.emtiaz.static import QUALITY_INDEX, LICKERT

from apps.activity.models import (
    Activity,
    Student,
    RateActivity,
    Department,
    ActivityState,
    ActivityCategory
)
from apps.league.models import County, Province
from apps.user.models import Teacher
from utils.user_type import get_user_level, get_user_location


def export_xls_activities_like():
    queryset = RateActivity.objects.all()
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("activities")
    row_num = 0

    columns = [
        (u"serial", 4000),
        (u"activity id", 8000),
        (u"school id", 8000),
        (u"school like id", 8000),
        (u"G3 -> emtiazi ke dahande grefte", 8000),
        (u"average_absolute", 8000),
        (u"like position", 8000),
        (u"first like", 8000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1

    for idx, obj in enumerate(queryset):
        row_num += 1
        point_student = obj.point_student
        row = [
            idx,
            obj.activity.id,
            obj.activity.school.code_bagheri,
            obj.student.school.code_bagheri,
            point_student,
            obj.average_absolute,
        ]
        county = False
        if obj.activity.school.county == obj.student.school.county:
            row.append("county")
            county = True

        elif obj.activity.school.province == obj.student.school.province:
            row.append("province")

        else:
            row.append("meli")

        if (point_student == 2 and county) or point_student == 4 or point_student == 6:
            row.append(True)
            obj.first_like = True
            obj.save()

        else:
            row.append(False)

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save("activities_like.xls")


def export_xls_activities():
    queryset = Activity.objects.all()
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("activities")
    row_num = 0
    departments = Department.objects.filter(~Q(max_count_activity=0))
    categories = ActivityCategory.objects.all()

    dict_main_max_activity, max_activity_count_in_all_department = ComputingPoint().get_dict_main_max_activity(categories, departments)

    columns = [
        (u"ردیف", 4000),
        (u"state", 8000),
        (u"کد باقری", 8000),
        (u"نام مدرسه", 8000),
        (u"ای دی دانش آموز", 8000),
        (u"نام و نام خانوادگی", 8000),
        (u"شهرستان", 8000),
        (u"استان", 8000),

        (u"ای دی مربی مدرسه", 8000),
        (u"نام مربی مدرسه", 8000),
        (u"ای دی مربی تایید کننده فعالیت", 8000),
        (u"نام مربی تایید کننده فعالیت", 8000),

        (u"جنسیت", 8000),
        (u"ای دی فعالیت ", 8000),
        (u"حوزه", 8000),
        (u"شاخه", 8000),
        (u"عنوان", 8000),
        (u"مکان", 8000),
        (u"تاریخ ایجاد", 8000),
        (u"تاریخ انجام فعالیت", 8000),
        (u"num of customers", 8000),
        (u"activity customers", 8000),
        (u"num of colleagues", 8000),
        (u"customers percent", 8000),
        (u"G1 score", 8000),
        (u"G2 score", 8000),
        (u"G4 score", 8000),
        (u"final score", 8000),
        (u"Permission axis", 8000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1

    for idx, obj in enumerate(queryset):
        row_num += 1
        row = [
            idx,
            obj.state,
            obj.school.code_bagheri,
            obj.school.name,
            obj.student.id,
            obj.student.first_name + " " + obj.student.last_name,
            obj.school.county.title,
            obj.school.province.title,

            obj.school.teacher.id,
            obj.school.teacher.first_name + " " + obj.school.teacher.last_name,
            obj.checker.id if obj.checker else "",
            obj.checker.first_name + " " + obj.checker.last_name if obj.checker else ""
                                                                                     "",
            obj.gender,
            obj.id,
            obj.category.department.title,
            obj.category.title,
            obj.title,
            obj.location,
            obj.created_at,
            obj.start_date,
            obj.school.student_count,
        ]

        activity_customers = added_activity_customers(obj)
        row.append(activity_customers)

        colleagues = added_colleagues(obj)
        row.append(colleagues)
        try:
            row.append((int(activity_customers) * 100) / obj.school.student_count)
        except:
            row.append("null")

        row.append(obj.point)

        g2, dict_school_params = ComputingPoint().evaluation_activity_and_their_relationship(
            dict_main_max_activity.copy(),
            max_activity_count_in_all_department,
            departments,
            categories,
            [obj],
            obj.school.id,
        )
        row.append(g2)

        row.append(get_point_from_student_of_activity(obj))
        row.append(obj.school.point)
        row.append(obj.use_in_league)

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save("activities.xls")


def export_xls_view_student(database="default", x=None, y=None):
    queryset = ActivityState.objects.using(database).filter(
        viewer_id__in=Student.objects.all()
    ).order_by('id')[x:y]
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("xls_view")
    row_num = 0
    columns = [
        (u"ردیف", 4000),
        (u"ای دی فعالیت", 4000),
        (u"عنوان", 8000),
        (u"کد محور", 4000),
        (u"محور فعالیت", 8000),
        (u"کد دسته", 4000),
        (u" دسته فعالیت", 8000),
        (u"ایدی مدرسه", 8000),
        (u"شهر فعالیت", 8000),
        (u"استان فعالیت", 8000),
        (u"روز ثبت فعالیت", 8000),
        (u"جنسیت", 8000),
        (u"تاریخ اولین بازدید", 8000),

        (u"ایدی دانش آموز", 8000),
        (u"ایدی مدرسه", 8000),
        (u"شهر ", 8000),
        (u"استان ", 8000),
        (u"لایک", 8000),
        (u"position", 8000),

        (u"روز لایک ", 8000),
        (u"تعداد ستاره", 8000),
        (u"امتیاز لایک کننده از این لایک", 8000),
        (u"میانگین متوسط با کامنتش", 8000),
        (u"اولین لایک", 8000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1

    for idx, obj in enumerate(queryset):
        row_num += 1
        row = [
            idx,
            obj.activity_id,
            obj.activity.title,
            obj.activity.category.department.id,
            obj.activity.category.department.title,
            obj.activity.category.id,
            obj.activity.category.title,
            obj.activity.school.code_bagheri,
            obj.activity.school.county.title,
            obj.activity.school.province.title,
            obj.activity.created_at.date(),
            obj.activity.gender,
            obj.created_at.date(),
            obj.viewer.student.id,
            obj.viewer.student.school.code_bagheri,
            obj.viewer.student.school.county.title,
            obj.viewer.student.school.province.title,
        ]
        try:
            liker = RateActivity.objects.using(database).get(activity=obj.activity, student_id=obj.viewer_id)
            row.append(True)
            county = False
            if obj.activity.school.county == liker.student.school.county:
                row.append("county")
                county = True

            elif obj.activity.school.province == liker.student.school.province:
                row.append("province")

            else:
                row.append("national")

            row.extend([
                liker.created_at.date(),
                liker.rate,
                liker.point_student,
                liker.average_absolute,
            ])
            if (liker.point_student == 2 and county) or liker.point_student == 4 or liker.point_student == 6:
                row.append(True)
                obj.first_like = True
                obj.save()

            else:
                row.append(False)

        except:
            row.append(False)
            if obj.activity.school.county == obj.viewer.student.school.county:
                row.append("county")

            elif obj.activity.school.province == obj.viewer.student.school.province:
                row.append("province")

            else:
                row.append("national")

            for i in range(0, 5):
                row.append("")

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save("xls_view.xls")


def export_xls_view_teacher(database="default", x=None, y=None):
    queryset = ActivityState.objects.using(database).filter(
        viewer_id__in=Teacher.objects.all()
    ).order_by('id')[x:y]

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("xls_view_teacher")

    row_num = 0
    columns = [
        (u"ردیف", 4000),
        (u"ای دی فعالیت", 4000),
        (u"عنوان", 8000),
        (u"کد محور", 4000),
        (u"محور فعالیت", 8000),
        (u"کد دسته", 4000),
        (u" دسته فعالیت", 8000),
        (u"ایدی مدرسه", 8000),
        (u"شهر فعالیت", 8000),
        (u"استان فعالیت", 8000),
        (u"روز ثبت فعالیت", 8000),
        (u"جنسیت", 8000),
        (u"ایا خودش تایید کرده", 8000),
        (u"نقش مشاهده کننده", 8000),
        (u"ایدی مشاهده کننده", 8000),
        (u"استان مشاهده کننده", 8000),
        (u"شهر مشاهده کننده", 8000),
        (u"روز مشاهده فعالیت", 8000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1

    for idx, obj in enumerate(queryset):
        row_num += 1
        row = [
            idx,
            obj.activity_id,
            obj.activity.title,
            obj.activity.category.department.id,
            obj.activity.category.department.title,
            obj.activity.category.id,
            obj.activity.category.title,
            obj.activity.school.code_bagheri,
            obj.activity.school.county.title,
            obj.activity.school.province.title,
            obj.activity.created_at.date(),
            obj.activity.gender,
        ]

        if obj.activity.checker and obj.activity.checker.id == obj.viewer.id:
            row.append(True)
        else:
            row.append(False)

        user_levels = obj.viewer.teacher.coach_levels.all()
        levels = []
        for item in user_levels:
            levels.append(item.level_code)

        user_level_added(levels, row)
        row.append(obj.viewer.teacher.id)

        camp_id, county_id, province_id = get_user_location(obj.viewer, levels)
        if province_id:
            row.append(Province.objects.get(id=province_id).title)
        else:
            row.append("نامشخص")

        if county_id:
            row.append(County.objects.get(id=county_id).title)
        else:
            row.append("نامشخص")

        row.append(obj.created_at.date())

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save("xls_view_teacher.xls")


def user_level_added(levels, row):
    if "country" in levels:
        row.append('country')

    elif "province" in levels:
        row.append('province')

    elif "county" in levels:
        row.append('county')

    elif "camp" in levels:
        row.append('camp')

    elif "coach" in levels:
        row.append('coach')


def added_activity_customers(obj):
    additional_fields = obj.activityadditionalfields_set.all()
    for item in additional_fields:
        if item.additional_field.label == "تعداد مخاطبین":
            return item.value
    return "null"


def added_colleagues(obj):
    additional_fields = obj.activityadditionalfields_set.all()
    for item in additional_fields:
        if item.additional_field.label == "تعداد همکار":
            try:
                return item.additional_field.dropdownformsomeadditionalfield_set.filter(id=item.value)[0].value
            except:
                pass
            break
    return "null"


def get_point_from_student_of_activity(activity):
    activities_point = RateActivity.objects.filter(
        activity=activity,
        rate__gt=3
    )

    avg_activities_point = activities_point.aggregate(Avg('average_absolute'))["average_absolute__avg"]

    if avg_activities_point is None:
        return 0

    return avg_activities_point * QUALITY_INDEX * LICKERT
