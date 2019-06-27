from apps.league.models import School, County, Camp, Province
from apps.user.models.student import Student


def get_user_type(user):
    try:
        if user.baseuser.student:
            return 'student'
    except:
        try:
            if user.baseuser.teacher:
                return 'teacher'
        except:
            try:
                if user.baseuser.advisor:
                    return 'advisor'
            except:
                return 'admin'


def get_user_level(user, user_type=None):
    if not user_type:
        user_type = get_user_type(user)

    if user_type == "student":
        return ["student"]

    if user_type == "teacher":
        levels = []
        db_levels = user.baseuser.teacher.coach_levels.all()
        for item in db_levels:
            if item.level_code == "province":
                if item.show_activity == "both":
                    levels.append(item.level_code)
                    continue

                if item.show_activity == "female":
                    levels.append("province_f")
                    continue

                if item.show_activity == "male":
                    levels.append("province_m")
                    continue

            levels.append(item.level_code)
        return levels

    if user_type == 'advisor':
        levels = []
        db_levels = user.baseuser.advisor.levels.all()
        for item in db_levels:
            levels.append(item.level_code)
        return levels


def get_user_location(user, levels=None):
    if levels is None:
        levels = get_user_level(user)

    province_id = 0
    county_id = 0
    camp_id = 0
    if 'student' in levels:
        student = Student.objects.filter(id=user.id)
        if student.exists():
            student = student.get()
            province_id = student.school.province_id
            county_id = student.school.county_id
            camp_id = student.school.camp_id
    else:
        if "coach" in levels:
            school = School.objects.filter(teacher_id=user.id)
            if school.exists():
                school = school[0]

                province_id = school.province_id
                county_id = school.county_id
                camp_id = school.camp_id

        if 'camp' in levels:
            camp = Camp.objects.filter(coach_id=user.id).select_related('county__province')
            if camp.exists():
                camp = camp[0]
                province_id = camp.county.province_id
                county_id = camp.county_id

        if 'county' in levels:
            county = County.objects.filter(coach_id=user.id)
            if county.exists():
                county = county[0]
                province_id = county.province_id
                county_id = county.id

        if 'province' in levels or 'province_f' in levels or 'province_m' in levels:
            province = Province.objects.filter(coaches__in=[user.id])
            if province.exists():
                province = province[0]
                province_id = province.id

    return camp_id, county_id, province_id


def get_user_location_role(user, role):

    levels = get_user_level(user)

    province_id = 0
    county_id = 0
    camp_id = 0

    try:
        if 'student' in levels and role == 'student':
            student = Student.objects.filter(id=user.id)
            if student.exists():
                student = student.get()
                province_id = student.school.province_id
                county_id = student.school.county_id
                camp_id = student.school.camp_id
        else:
            if "coach" in levels and role == 'coach':
                school = School.objects.filter(teacher_id=user.id)
                if school.exists():
                    school = school[0]

                    province_id = school.province_id
                    county_id = school.county_id
                    camp_id = school.camp_id

            if 'camp' in levels and role == 'camp':
                camp = Camp.objects.filter(coach_id=user.id).select_related('county__province')
                if camp.exists():
                    camp = camp[0]
                    province_id = camp.county.province_id
                    county_id = camp.county_id

            if 'county' in levels and role == 'county':
                county = County.objects.filter(coach_id=user.id)
                if county.exists():
                    county = county[0]
                    province_id = county.province_id
                    county_id = county.id

            if ('province' in levels or 'province_f' in levels or 'province_m' in levels) and (role in ['province', 'province_f', 'province_m']):
                province = Province.objects.filter(coaches__in=[user.id])
                if province.exists():
                    province = province[0]
                    province_id = province.id
    except:
        pass
    finally:
        return camp_id, county_id, province_id


def get_user_location_name(user, levels=None):
    if levels is None:
        levels = get_user_level(user)

    province = ""
    county = ""
    camp = ""
    if 'student' in levels:
        student = Student.objects.filter(id=user.id)
        if student.exists():
            student = student.get()
            province = student.school.province.title
            county = student.school.county.title
            # if student.school.camp:
            #     camp = student.school.camp.title
    else:
        if "coach" in levels:
            school = School.objects.filter(teacher_id=user.id)
            if school.exists():
                school = school[0]

                province = school.province.title
                county = school.county.title
                # if school.camp:
                #     camp = school.camp.title

        if 'camp' in levels:
            camp_find = Camp.objects.filter(coach_id=user.id).select_related('county__province')
            if camp_find.exists():
                camp_find = camp_find[0]
                province = camp_find.county.province.title
                county = camp_find.county.title

        if 'county' in levels:
            county_find = County.objects.filter(coach_id=user.id)
            if county_find.exists():
                county_find = county_find[0]
                province = county_find.province.title
                county = county_find.title

        if 'province' in levels or 'province_f' in levels or 'province_m' in levels:
            province_find = Province.objects.filter(coaches__in=[user.id])
            if province_find.exists():
                province_find = province_find[0]
                province = province_find.title

    return camp, county, province


def has_perm_both_gender(user):
    levels = get_user_level(user)

    if "province" in levels or "county" in levels or "country" in levels:
        return True
    return False
