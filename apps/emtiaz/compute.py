import json
import math

from django.db.models import Sum, Q, Avg, F
from .models import HistoryScore

from apps.league.models import (
    School,
    Department,
    Province,
    County
)
from apps.activity.models import (
    AdditionalField,
    Activity,
    ActivityAdditionalFields,
    RateActivity,
    DropDownFormSomeAdditionalField,
    ActivityCategory
)
from apps.emtiaz.static import (
    ALPHA_IN_EVENT,
    BETA_WITH_EVENT,
    MINIMUM_PERCENTAGE_POINT,
    COUNT_RATE_ACTIVITIES,
    LOGARITHMIC_BASIS,
    QUALITY_INDEX, LICKERT,
    IN_EVENT_NUMBER, WITH_EVENT_NUMBER)


class ComputingPoint(object):

    @staticmethod
    def activity_point(activity_id):
        # sample params: [{"start":"x","end":"y%", "score":"z"},{},...]
        _activity = Activity.objects.filter(id=activity_id).select_related('school')
        if _activity.exists():
            activity = _activity.get()
            all_additional_fields = AdditionalField.objects.filter(
                category=activity.category_id,
                func_name__in=['func1', 'func2', 'func3']
            )
            score = 0
            for field in all_additional_fields:

                params = field.params
                try:
                    params = json.loads(params)
                except:
                    params = []

                func_total_type = field.func_total_type

                func_name = field.func_name
                if func_name == 'func3':
                    if isinstance(params, int):
                        """serfe bargozari maghadiresh fargh darad va admin vared mikonad"""
                        score += params
                    continue

                additional_field = ActivityAdditionalFields.objects.filter(
                    activity_id=activity_id,
                    additional_field_id=field.id
                )

                if not additional_field:
                    continue

                _value = additional_field.get().value
                if not _value.isdigit():
                    continue

                input_value = int(_value)

                if func_name == "func1":
                    drop = DropDownFormSomeAdditionalField.objects.filter(id=input_value)
                    if drop.exists():
                        try:
                            input_value = int(drop.get().value) + 1
                        except:
                            continue
                    else:
                        continue

                anjoman_count = activity.school.anjoman_count
                student_count = activity.school.student_count

                if func_total_type == 'school_count':
                    total_value = student_count

                elif func_total_type == 'anjoman_count':
                    total_value = anjoman_count

                new_score = 0
                for item in params:
                    start_value = item['start']
                    end_value = item['end']
                    if func_name == 'func2':
                        start_value = int(int(start_value.split('%')[0]) / 100 * total_value)
                        end_value = int(int(end_value.split('%')[0]) / 100 * total_value)

                    else:
                        end_value = int(end_value)
                        start_value = int(start_value)

                    if start_value < input_value < end_value:
                        new_score = int(item['score'])
                        break

                score += new_score
            activity.point = score
            activity.save()

    @staticmethod
    def get_categories(department, categories):
        results = []
        for cat in categories:
            if cat.department_id == department.id:
                results.append(cat)

        return results

    def school_point(self, schools=None):
        """
        محاسبه امتیازهای مدرسه و ذخیره در جدول تاریخچه امتیاز مدرسه
        """

        departments = Department.objects.filter(~Q(max_count_activity=0))  # حوزه
        categories = ActivityCategory.objects.all()  # زیر حوزه

        dict_main_max_activity, max_activity_count_in_all_department = self.get_dict_main_max_activity(categories, departments)  # حداکثر  تعداد فعالیت هر حوزه و زیر حوزه را محاسبه می کند

        if not schools:
            # schools = School.objects.filter(id=9867)
            schools = School.objects.filter(active=True)

        activities = Activity.objects.filter(state="ACCEPT")

        for school in schools:
            g2, dict_school_params = self.evaluation_activity_and_their_relationship(
                dict_main_max_activity.copy(),
                max_activity_count_in_all_department,
                departments,
                categories,
                activities,
                school.id,
            )
            g1, list_best_activity, count_activities = self.get_point_system_from_school(school.id, dict_school_params)

            g4 = self.get_point_from_student_of_activity(list_best_activity)

            g3 = self.get_acting_points_on_the_site(school)

            _percent = int(math.ceil(((g1 + g2 + g4) * MINIMUM_PERCENTAGE_POINT) / 100))

            point = g1 + g2 + min(g3, _percent) + g4

            school.point = point
            school.save()

            for item in list_best_activity:
                item.use_in_league = True  # چرا؟
                item.save()
                # print(item.id)

            if point:
                self.save_history_school(_percent, count_activities, g1, g2, g3, g4, list_best_activity, point, school)

    @staticmethod
    def save_history_school(_percent, count_activities, g1, g2, g3, g4, list_best_activity, point, school):
        history_score = HistoryScore()
        history_score.school = school
        history_score.g1 = g1
        history_score.g2 = g2
        history_score.g3 = g3
        history_score.g4 = g4
        history_score.percent = _percent
        history_score.count_all_activity = count_activities
        history_score.count_best_activity = len(list_best_activity)
        history_score.final_point = point
        history_score.save()

    def get_dict_main_max_activity(self, categories, departments):
        """
        در این تابع دیکشنری از دسته و زیر دسته هایی ساخته می شود
         که حداکثر تعداد آن بزرگتر از صفر باشد

         همچنین جمع حداکثر تعداد فعالیت محاسبه می شود

        """
        dict_main_max_activity = {}
        max_activity_count_in_all_department = 0

        for department in departments:
            list_cat = []
            cats = self.get_categories(department, categories)
            for cat in cats:
                if cat.max_count_activity:
                    list_cat.append({
                        "id": cat.id,
                        "max_count": cat.max_count_activity,
                    })
            max_activity_count_in_all_department += department.max_count_activity

            if department.max_count_activity:
                dict_main_max_activity[department.id] = {
                    "max_count": department.max_count_activity,
                    "list_cat": list_cat,
                }
        return dict_main_max_activity, max_activity_count_in_all_department

    @staticmethod
    def get_point_system_from_school(school_id, dict_school_params):
        """
        تابعی برای انتخاب فعالیت های برتر بر اساس محدودیت زیر دسته ها
        همچنین محاسبه امتیاز سیستمی و امتیاز گرفته شده در امتیاز بده امتیاز بگیر
        """

        final_point_sum = 0
        list_best_activity = []
        count_activities = 0
        for _id, school_p in dict_school_params.items():
            activities = Activity.objects.filter(
                school_id=school_id,
                category__department_id=_id
            ).annotate(
                sum_point=(F('point_emtiaz_sum') + F('point'))
            ).order_by('-sum_point')
            # چرا امتیازبده امتیاز داده شده توسط دیگران هم جمع شده؟
            count_activities += activities.count()

            activities = activities[0:school_p["number_of_allowed_activities_in_get_point_system"]]
            # چرا تعداد فعالیت های انتخاب شده بر اساس عدد داخلی دسته است
            point_sum = activities.aggregate(Sum('point'))["point__sum"]
            if point_sum is not None:
                list_best_activity.extend(list(activities))
                final_point_sum += point_sum

        return final_point_sum, list_best_activity, count_activities

    def get_acting_points_on_the_site(self, school):
        """ تابعی برای محاسبه امتایزهای گفته شده توسط دانش آموزان مدرسه در امتیاز بده امتیاز بگیر"""
        students = school.student_set.all()

        """ در کد زیر امتیازهایی که دانش آموز از امتیاز بده امتیاز بگیر گرفته استخراج می شود"""
        # آیا همه دانش آموزان آن مدرسه لحاظ می شود یا آخرین دانش آموز مدرسه
        activities_point = RateActivity.objects.filter(
            student__in=students,
        ).aggregate(Sum('point_student'))["point_student__sum"]

        if activities_point is not None:
            return activities_point
        return 0

    def get_point_from_student_of_activity(self, list_best_activity):
        """
        امتیاز هایی که دانش آموزان به فعالیت ها داده اند.
        :param list_best_activity: بهترین فعالیت های قابل انتخاب

        :return: final_point * QUALITY_INDEX * LICKERT * avg_activities_point
        """
        activities_point = RateActivity.objects.filter(
            activity__in=list_best_activity,
            rate__gt=3
        )  # چرا باید امتیاز بزرگتر از ۳ باشد

        count_rate_activities = activities_point.count()

        avg_activities_point = activities_point.aggregate(Avg('average_absolute'))["average_absolute__avg"]
        # average_absolute چیه

        if avg_activities_point is None:
            return 0

        if count_rate_activities <= COUNT_RATE_ACTIVITIES:
            final_point = (math.log(COUNT_RATE_ACTIVITIES, LOGARITHMIC_BASIS) / COUNT_RATE_ACTIVITIES) * count_rate_activities

        else:
            final_point = math.log(count_rate_activities, LOGARITHMIC_BASIS)

        return final_point * QUALITY_INDEX * LICKERT * avg_activities_point

    @staticmethod
    def get_category_activities_count(category, school, activities):
        """تعداد فعالیت های مدرسه در زیر دسته خواسته شده  را محاسبه می کند """
        count = 0

        for activity in activities:

            if activity.category_id == category and activity.school_id == school:
                count += 1

        return count

    def evaluation_activity_and_their_relationship(
            self,
            dict_main_max_activity,
            max_activity_count_in_all_department,
            departments,
            categories,
            activities,
            school_id
    ):
        """
        ارزیابی فعالیت و ارتباط هایش  بر اساس دسته و زیردسته

        :param dict_main_max_activity: حداکثر تعداد فعالیت های هر دسته و زیر دسته
        :param max_activity_count_in_all_department: حداکثر تعداد جمع همه حداکثر فعالیت ها در همه دسته ها
        :param departments:
        :param categories:
        :param activities:
        :param school_id:

        :return: (ALPHA_IN_EVENT * in_event) + (BETA_WITH_EVENT * with_event)
        """
        dict_school_params = self.get_all_activity_from_school_separation_categories_and_departments(
            departments,
            categories,
            activities,
            school_id,
        )

        in_event = 0
        with_event = 0
        some_all_department_act = 0  # جمع همه فعالیت های مدرسه
        for _id, school_p in dict_school_params.items():
            some_all_department_act += school_p["count_dep"]

        for _id, main_p in dict_main_max_activity.items():
            for _id_s, school_p in dict_school_params.items():
                if _id == _id_s:
                    with_event += self.get_with_event_point(max_activity_count_in_all_department, main_p, school_p, some_all_department_act)
                    # متغیر زیر تعداد فعالیت هایی که می تواند در محاسبه امتیاز مدرسه لحاظ شود ذخیره می شود
                    # چرا از ماکزیمم تعداد آن زیر دسته استفاده نمی کنیم
                    number_of_allowed_activities_in_get_point_system = self.get_in_event_point(main_p, school_p)

                    in_event += number_of_allowed_activities_in_get_point_system

                    school_p['number_of_allowed_activities_in_get_point_system'] = number_of_allowed_activities_in_get_point_system

        gx = (ALPHA_IN_EVENT * in_event) + (BETA_WITH_EVENT * with_event)  # چرا

        return gx, dict_school_params

    @staticmethod
    def get_with_event_point(max_activity_count_in_all_department, main_p, school_p, some_all_department_act):
        """
        این تابع  برای محاسبه ارتباط میان دسته ها استفاده می شود
        main_p['max_count'] is all activity in this department حداکثر تعداد فعالیت در این دسته
        max_activity_count_in_all_department is all activity in all department جمع حداکثر فعالیت ها در همه دسته ها
        some_all_department_act is all activity of school in all department جمع همه فعالیت ها در همه دسته ها
        school_p["count_dep"] is all activity in of school in this department  جمع  فعالیت های این دسته مدرسه

        """
        with_event = 0
        if some_all_department_act > WITH_EVENT_NUMBER:
            with_event += WITH_EVENT_NUMBER  # چرا
            with_event += min(math.ceil((main_p['max_count'] / max_activity_count_in_all_department) * some_all_department_act), school_p["count_dep"] - WITH_EVENT_NUMBER)  # چرا
            return with_event
        else:
            return school_p["count_dep"]

    @staticmethod
    def get_in_event_point(main_p, school_p):
        """
        این تابع  برای محاسبه ارتباط زیر دسته ها استفاده می شود
        main_cat['max_count'] is all activity in this category  حداکثر تعداد فعالیت های این زیر دسته
        main_p['max_count'] is all activity in this department
        school_p['count_dep'] is all activity of school in this department
        school_cat["count"] is all activity in of school in this category  تعداد فعالیت های این دسته مدرسه

        """

        in_event = 0
        for main_cat in main_p["list_cat"]:
            for school_cat in school_p["list_cat"]:
                if main_cat["id"] == school_cat["id"]:
                    if school_p['count_dep'] >= IN_EVENT_NUMBER:  # احتمالا اشتباه
                        in_event += min(math.ceil((main_cat['max_count'] / main_p['max_count']) * school_p['count_dep']), school_cat["count"] - IN_EVENT_NUMBER)  # چرا
                        in_event += IN_EVENT_NUMBER  # چرا
                    else:
                        in_event += school_cat["count"]
                    break
        return in_event

    def get_all_activity_from_school_separation_categories_and_departments(self, departments, categories, activities, school_id):
        """این تابع تعداد فعالیت های هر دسته و زیر دسته مدرسه را محاسبه می کند"""
        dict_school_params = {}

        for department in departments:
            if department.max_count_activity:  # این خط اضافه شد تا دسته های صفر مدرسه را نیاورد
                count_dep = 0
                list_cat = []
                cats = self.get_categories(department, categories)
                for cat in cats:
                    if cat.max_count_activity:  # این خط اضافه شد تا زیر دسته های صفر مدرسه را نیاورد
                        count = self.get_category_activities_count(cat.id, school_id, activities)
                        list_cat.append({
                            "id": cat.id,
                            "count": count,
                        })
                        count_dep += count

                dict_school_params[department.id] = {
                    "count_dep": count_dep,
                    "list_cat": list_cat,
                }
        return dict_school_params

    @staticmethod
    def school_ranking():
        schools_male = School.objects.filter(gender='male').order_by('-point')
        schools_female = School.objects.filter(gender='female').order_by('-point')

        print("ComputingPoint.actions_set_ranking(schools_male)")
        ComputingPoint.actions_set_ranking(schools_male, "rank")

        print("ComputingPoint.actions_set_ranking(schools_female)")
        ComputingPoint.actions_set_ranking(schools_female, "rank")

        print("ComputingPoint.province_ranking(schools_male, schools_female)")
        ComputingPoint.province_ranking(schools_male, schools_female)

        print("ComputingPoint.county_ranking(schools_male, schools_female)")
        ComputingPoint.county_ranking(schools_male, schools_female)

    @staticmethod
    def actions_set_ranking(schools, field):
        rank = 1
        for index, school in enumerate(schools):
            if index != 0:
                school_point = schools[index].point
                last_school_point = schools[index - 1].point
                if school_point == last_school_point:
                    rank = getattr(schools[index - 1], field)
                else:
                    rank += 1

            setattr(school, field, rank)
            school.save()

    @staticmethod
    def county_ranking(schools_male, schools_female):
        counties = County.objects.all()
        for county in counties:
            schools = schools_male.filter(county=county.id).order_by('-point')
            ComputingPoint.actions_set_ranking(schools, "county_rank")

            schools = schools_female.filter(county=county.id).order_by('-point')
            ComputingPoint.actions_set_ranking(schools, "county_rank")

    @staticmethod
    def province_ranking(schools_male, schools_female):
        provinces = Province.objects.all()
        for province in provinces:
            schools = schools_male.filter(province=province.id).order_by('-point')
            ComputingPoint.actions_set_ranking(schools, "province_rank")

            schools = schools_female.filter(province=province.id).order_by('-point')
            ComputingPoint.actions_set_ranking(schools, "province_rank")

    def activities_point(self):
        activities = Activity.objects.filter(
            state="ACCEPT",
            category_id__in=[33, 34, 35]
        )
        for activity in activities:
            all_additional_fields = AdditionalField.objects.filter(
                category=activity.category_id,
                func_name__in=['func1', 'func2', 'func3']
            )
            score = 0
            for field in all_additional_fields:

                params = field.params
                try:
                    params = json.loads(params)
                except:
                    params = []

                func_total_type = field.func_total_type

                func_name = field.func_name
                if func_name == 'func3':
                    if isinstance(params, int):
                        score = score + params  # serfe bargozari maghadiresh fargh darad va admin vared mikonad
                    continue

                additional_field = ActivityAdditionalFields.objects.filter(
                    activity_id=activity.id,
                    additional_field_id=field.id
                )

                if not additional_field:
                    continue

                _value = additional_field.get().value
                if not _value.isdigit():
                    continue

                input_value = int(_value)

                if func_name == "func1":
                    drop = DropDownFormSomeAdditionalField.objects.filter(id=input_value)
                    if drop.exists():
                        try:
                            input_value = int(drop.get().value) + 1
                        except:
                            continue
                    else:
                        continue

                anjoman_count = activity.school.anjoman_count
                student_count = activity.school.student_count

                if func_total_type == 'school_count':
                    total_value = student_count

                elif func_total_type == 'anjoman_count':
                    total_value = anjoman_count

                new_score = 0
                for item in params:
                    start_value = item['start']
                    end_value = item['end']
                    if func_name == 'func2':
                        start_value = int(int(start_value.split('%')[0]) / 100 * total_value)
                        end_value = int(int(end_value.split('%')[0]) / 100 * total_value)

                    else:
                        end_value = int(end_value)
                        start_value = int(start_value)

                    if start_value < input_value < end_value:
                        new_score = int(item['score'])
                        break

                score += new_score
            activity.point = score
            activity.save()
