import datetime
import json
import requests

# from django.db import transaction
from dashboard.logger import logger_api
from apps.user.models.teacher import Teacher
from apps.user.models.student import Student
from apps.league.models import Province, County, Camp, School
from apps.user.models.base import BaseUser


class BagheriApi(object):
    def __init__(self, *args, **kwargs):
        self.username = "bagheri_api_user"
        self.password = "B>9Jd%mJD}<>cyL3"
        self.server_api = "http://shbagheri.com"

    def get_token(self):
        post_req = {
            "username": self.username,
            "password": self.password,
        }
        get_res = requests.post(
            url=self.server_api + "/api/auth/",
            data=json.dumps(post_req),
            headers={"Content-Type": "application/json"}
        )
        if get_res.status_code == 200:
            token = get_res.json().get("token")
            return token

        else:

            logger_api.error("get_token bagheri api", extra={
                "detail": {
                    "error": get_res,
                }
            })
            return ""

    def send_message(self, user, code):
        token = ""
        for i in range(1, 2):
            token = self.get_token()
            if token:
                break

        if not token:
            return False

        post_req = {
            "ID_hash": user,
            "message": str(code)
        }
        get_res = requests.post(
            url=self.server_api + "/api/send-message/",
            data=json.dumps(post_req),
            headers={"Content-Type": "application/json", "authorization": "JWT " + token}
        )

        return get_res

    def set_teachers(self, next_url=None):
        token = self.get_token()
        print(next_url)

        if next_url is None:
            get_res = requests.get(
                url=self.server_api + "/api/v1/teachers/",
                headers={"authorization": "JWT " + token}
            )

        else:
            get_res = requests.get(
                url=next_url,
                headers={"authorization": "JWT " + token}
            )

        if get_res.status_code == 200:
            results = get_res.json()
            next_url = results["next"]
            teachers = results["results"]
            # 1: coach | 2:camp | 3: county | 4:province | 5: province_f | 6:province_m | 7: country
            level_choices = {1: 4, 2: 3, 3: 8, 4: 9, 5: 6, 6: 5, 7: 7}

            list_error_teachers = []
            for _teacher in teachers:
                try:
                    teacher = Teacher.objects.filter(username=_teacher["username"])
                    if not teacher.exists():
                        teacher = Teacher()
                        teacher.username = _teacher["username"]
                        teacher.password = _teacher["username"]
                    else:
                        teacher = teacher.get()

                    teacher.first_name = _teacher["first_name"]
                    teacher.last_name = _teacher["last_name"]
                    teacher.gender = _teacher["gender"]
                    teacher.is_active = True

                    # if BaseUser.objects.filter(phone_number=_teacher["phone_number"]).exclude(id=teacher.id).exists():
                    #     list_error_teachers.append({
                    #         "teacher_phone_error": _teacher
                    #     })
                    #     continue

                    teacher.phone_number = _teacher["phone_number"]

                    teacher.save()

                    try:
                        teacher.coach_levels.clear()
                    except Exception as e:
                        print(e)

                    try:
                        for level in _teacher["levels"]:
                            teacher.coach_levels.add(level_choices[level])
                    except:
                        list_error_teachers.append({
                            "teacher_coach_levels_error": _teacher
                        })
                        continue

                    teacher.updated_at = datetime.datetime.now()
                    teacher.save()

                except Exception as e:

                    logger_api.error(
                        "teacher has error >> {0}".format(datetime.datetime.now()),
                        extra={
                            "teachers error": (_teacher, e),
                        })
                    continue

            if list_error_teachers:
                logger_api.error(
                    "teachers bagheri api {0} >> ".format(datetime.datetime.now()) + str(next_url),
                    extra={
                        "teachers error": list_error_teachers,
                    })

            if next_url:
                self.set_teachers(next_url=next_url)

            else:
                logger_api.info("Completed teachers completion.")

        elif get_res.status_code == 401:
            self.set_teachers(next_url)

        else:
            logger_api.error("teachers bagheri api", extra={
                "detail": {
                    "error": get_res,
                }
            })

    def set_provinces(self, next_url=None):
        token = self.get_token()
        print(next_url)

        if next_url is None:
            get_res = requests.get(
                url=self.server_api + "/api/v1/provinces/",
                headers={"authorization": "JWT " + token}
            )

        else:
            get_res = requests.get(
                url=next_url,
                headers={"authorization": "JWT " + token}
            )

        if get_res.status_code == 200:
            results = get_res.json()
            next_url = results["next"]
            provinces = results["results"]

            list_error_teacher = []
            for _province in provinces:
                province = Province.objects.filter(code=_province["code"])
                if not province.exists():
                    province = Province()
                    province.slug = _province["code"]
                    province.code = _province["code"]
                else:
                    province = province.get()

                province.title = _province["name"]
                province.save()
                province.coaches.clear()

                try:
                    if _province["teacher_id"]:
                        province.coaches.add(Teacher.objects.get(username=_province["teacher_id"]))
                except:
                    list_error_teacher.append({
                        "province_name": _province["name"],
                        "teacher_error": _province["teacher_id"]
                    })

                try:
                    if _province["teacher_id_f"]:
                        province.coaches.add(Teacher.objects.get(username=_province["teacher_id_f"]))
                except:
                    list_error_teacher.append({
                        "province_name": _province["name"],
                        "teacher_error": _province["teacher_id_f"]
                    })

                try:
                    if _province["teacher_id_m"]:
                        province.coaches.add(Teacher.objects.get(username=_province["teacher_id_m"]))
                except:
                    list_error_teacher.append({
                        "province_name": _province["name"],
                        "teacher_error": _province["teacher_id_m"]
                    })

                province.save()

            if list_error_teacher:
                logger_api.error(
                    "province bagheri api {0} >> ".format(datetime.datetime.now()) + str(next_url),
                    extra={
                        "teachers_error_not_found": list_error_teacher,
                    })

            if next_url:
                self.set_provinces(next_url=next_url)

            else:
                logger_api.info("Completed provinces completion.")

        elif get_res.status_code == 401:
            self.set_provinces(next_url)

        else:
            logger_api.error("province bagheri api", extra={
                "detail": {
                    "error": get_res,
                }
            })

    def set_counties(self, next_url=None):
        token = self.get_token()
        print(next_url)

        if next_url is None:
            get_res = requests.get(
                url=self.server_api + "/api/v1/counties/",
                headers={"authorization": "JWT " + token}
            )

        else:
            get_res = requests.get(
                url=next_url,
                headers={"authorization": "JWT " + token}
            )

        if get_res.status_code == 200:
            results = get_res.json()
            next_url = results["next"]
            counties = results["results"]
            list_error_county = []
            for _county in counties:
                county = County.objects.filter(code=_county["code"])
                if not county.exists():
                    county = County()
                    county.slug = _county["code"]
                    county.code = _county["code"]
                else:
                    county = county.get()

                county.title = _county["name"]
                try:
                    county.province = Province.objects.get(code=_county["province_id"])
                except:
                    list_error_county.append({
                        "county_error": _county
                    })
                    continue

                try:
                    county.coach = Teacher.objects.get(username=_county["teacher_id"])

                except:
                    list_error_county.append({
                        "teacher_error": _county
                    })
                    continue

                county.save()

            if list_error_county:
                logger_api.error(
                    "county bagheri api {0} >> ".format(datetime.datetime.now()) + str(next_url),
                    extra={
                        "county error": list_error_county,
                    })

            if next_url:
                self.set_counties(next_url=next_url)

            else:
                logger_api.info("Completed cities completion.")

        elif get_res.status_code == 401:
            self.set_counties(next_url)

        else:
            logger_api.error("province bagheri api", extra={
                "detail": {
                    "error": get_res,
                }
            })

    def set_camps(self, next_url=None):
        token = self.get_token()
        print(next_url)

        if next_url is None:
            get_res = requests.get(
                url=self.server_api + "/api/v1/camps/",
                headers={"authorization": "JWT " + token}
            )

        else:
            get_res = requests.get(
                url=next_url,
                headers={"authorization": "JWT " + token}
            )

        if get_res.status_code == 200:
            results = get_res.json()
            next_url = results["next"]
            camps = results["results"]

            list_error_camps = []
            for _camp in camps:
                camp = Camp.objects.filter(code=_camp["camp_id"])
                if not camp.exists():
                    camp = Camp()
                    camp.slug = _camp["camp_id"]
                    camp.code = _camp["camp_id"]
                else:
                    camp = camp.get()

                try:
                    camp.county = County.objects.get(code=_camp["county_id"])
                except:
                    list_error_camps.append({
                        "camp_error": _camp
                    })
                    continue

                camp.title = _camp["name"]

                try:
                    camp.coach = Teacher.objects.get(username=_camp["teacher_id"])
                except:
                    list_error_camps.append({
                        "teacher_error": _camp
                    })
                    continue

                camp.save()

            if list_error_camps:
                logger_api.error(
                    "camps bagheri api {0} >> ".format(datetime.datetime.now()) + str(next_url),
                    extra={
                        "camp error": list_error_camps,
                    })

            if next_url:
                self.set_camps(next_url=next_url)

            else:
                logger_api.info("Completed camps completion.")

        elif get_res.status_code == 401:
            self.set_camps(next_url)

        else:
            logger_api.error("province bagheri api", extra={
                "detail": {
                    "error": get_res,
                }
            })

    def set_schools(self, next_url=None):
        token = self.get_token()
        print(next_url)
        students_count = {
            "1": 50,
            "2": 75,
            "3": 100,
            "4": 150,
            "5": 200,
            "6": 300,
        }

        if next_url is None:
            get_res = requests.get(
                url=self.server_api + "/api/v1/schools/?limit=100",
                headers={"authorization": "JWT " + token}
            )

        else:
            get_res = requests.get(
                url=next_url,
                headers={"authorization": "JWT " + token}
            )

        if get_res.status_code == 200:
            results = get_res.json()
            next_url = results["next"]
            schools = results["results"]
            list_error_school = []
            for _school in schools:
                school = School.objects.filter(code_bagheri=_school["code"])
                if not school.exists():
                    school = School()
                    school.code_bagheri = _school["code"]
                else:
                    school = school.get()

                school.name = _school["name"]
                school.gender = _school["gender"]
                school.student_count = students_count.get(str(_school["students_count"]), 400)
                school.anjoman_count = _school["number_of_users"]

                try:
                    school.county = County.objects.get(code=_school["county_id"])
                except:
                    list_error_school.append({
                        "school.county": _school
                    })
                    continue

                try:
                    school.province = Province.objects.get(code=_school["province_id"])
                except:
                    list_error_school.append({
                        "school.province": _school
                    })
                    continue

                # if _school["camp_id"] is not None:
                #     try:
                #         school.camp = Camp.objects.get(code=_school["camp_id"])
                #     except:
                #         list_error_school.append({
                #             "school.camp": _school
                #         })
                #         # continue

                try:
                    school.teacher = Teacher.objects.get(username=_school["teacher_id"])

                except:
                    list_error_school.append({
                        "school.Teacher": _school
                    })
                    continue

                school.updated_at = datetime.datetime.now()
                school.active = True
                school.save()

            if list_error_school:
                logger_api.error(
                    "schools bagheri api {0} >> ".format(datetime.datetime.now()) + str(next_url),
                    extra={
                        "school error": list_error_school,
                    })

            if next_url:
                self.set_schools(next_url=next_url)

            else:
                logger_api.info("Completed schools completion.")

        elif get_res.status_code == 401:
            self.set_schools(next_url)

        else:
            logger_api.error("province bagheri api", extra={
                "detail": {
                    "error": get_res,
                }
            })

    def set_students(self, next_url=None):
        token = self.get_token()
        print(next_url)

        if next_url is None:
            get_res = requests.get(
                url=self.server_api + "/api/v1/students/?limit=100",
                headers={"authorization": "JWT " + token}
            )

        else:
            get_res = requests.get(
                url=next_url,
                headers={"authorization": "JWT " + token}
            )

        if get_res.status_code == 200:
            results = get_res.json()
            next_url = results["next"]
            students = results["results"]
            list_error_student = []
            for _student in students:
                try:
                    student = Student.objects.filter(username=_student["username"])
                    if not student.exists():
                        student = Student()
                        student.username = _student["username"]
                        student.password = _student["username"]
                    else:
                        student = student.get()

                    student.first_name = _student["first_name"]
                    student.last_name = _student["last_name"]
                    student.gender = _student["gender"]
                    student.is_active = True

                    # if BaseUser.objects.filter(phone_number=_student["phone_number"]).exclude(id=student.id).exists():
                    #     list_error_student.append({
                    #         "student_phone_error": _student
                    #     })
                    #     continue

                    student.phone_number = _student["phone_number"]
                    try:
                        school = School.objects.get(code_bagheri=_student["school_code"])
                    except:
                        list_error_student.append({
                            "school_not_find": _student
                        })
                        continue

                    student.school = school
                    student.updated_at = datetime.datetime.now()

                    student.save()

                except Exception as e:
                    logger_api.error(
                        "student has error >> {0}".format(datetime.datetime.now()),
                        extra={
                            "student error": _student,
                            "error": e,
                        })
                    continue

            if list_error_student:
                logger_api.error(
                    "student bagheri api {0} >> ".format(datetime.datetime.now()) + str(next_url),
                    extra={
                        "student error": list_error_student,
                    })

            if next_url:
                self.set_students(next_url=next_url)

            else:
                logger_api.info("Completed student completion.")

        elif get_res.status_code == 401:
            self.set_students(next_url)

        else:
            logger_api.error("province bagheri api", extra={
                "detail": {
                    "error": get_res,
                }
            })
