#**In the name of God.**

####**This document shows the structure of the requested api from bagheri system.**

##### Notes :
1) all api urls must have versioning in their path.
- for example: **`v1`** for version number one.

> */api/v1/students*

2) all api urls must have the ability to return a `resourses` object and return specific objects with it's ID as a unique identifier.
-for example: the example below returns a `resources` object that contains a list of all students.
>*/api/v1/students/*

- for example: one (1) is student id and will return a specific object containing information about student with ID 1.

>*/api/v1/students/1*

3) All api urls must authenticate with JWT header token with bearer named **`JWT`**

4) Any person that has any kind of organizational power will be referred as **`Teacher`** in this document.

5) In all api's that return a list, must have pagination ability with following parameters:
- **`page_size`** keyword to change number of results.
- **`page`** for page number .
- **`offset`** for changing offset.

- for example: returns page 2 of student list with page size 20 and from 6th student .
>*/api/v1/students?page=2&page_size=20&offset=5*

**Resources:**

####`Teachers:`

> should return a list of teachers

**Structure (Yaml):**

~~~yaml
info:
  description: "Provinces api response"
  #
  # pagination information
  #
  required:
    - "count"
    - "per_page"
    - "next_page"
    - "prev_page"
    - "teachers"
  properties:
    count:
      type: "number"
    per_page:
      type: "number"
    next_page:
      type: "number"
    prev_page:
      type: "number"
    teachers:
      type: "array"
      items:
        type: "object"
        properties:
          bagheri_id:
            type: "number"
          #
          # Student national id
          #
          username:
            type: "string"
          phone_number:
            type: "string"
          first_name:
            type: "string"
          last_name:
            type: "string"
          #
          # can be female or male
          #
          gender:
            type: "string"
          email:
            type: "string"
          #
          # level of a teacher
          # 1 => coach
          # 2 => camp
          # 3 => county
          # 4 => province
          # 5 => province_f
          # 6 => province_m
          # 7 => country
          #
          level:
            type: "number"
~~~

**Sample (json):**

~~~Json
{
  "count": 2000,
  "per_page": 100,
  "next_page": 2,
  "prev_page": 1,
  "teachers": [
    {
      "bagheri_id": 1,
      "username": "4623500000",
      "phone_number": "09xxxxxxxxxx",
      "first_name": "mo",
      "last_name": "rm",
      "gender": "female|male",
      "email": "mo@rm.com",
      "level": "country"
    },
    {
      "bagheri_id": 2,
      "username": "4623500000",
      "phone_number": "09xxxxxxxxxx",
      "first_name": "mo",
      "last_name": "rm",
      "gender": "female|male",
      "email": "mo@rm.com",
      "level": "coach"
    },
    {
      "bagheri_id": 3,
      "username": "4623500000",
      "phone_number": "09xxxxxxxxxx",
      "first_name": "mo",
      "last_name": "rm",
      "gender": "female|male",
      "email": "mo@rm.com",
      "level": "province"
    },
    {
      "bagheri_id": 4,
      "username": "4623500000",
      "phone_number": "09xxxxxxxxxx",
      "first_name": "mo",
      "last_name": "rm",
      "gender": "female|male",
      "email": "mo@rm.com",
      "level": "province_f"
    }
  ]
}
~~~

####`Provinces:`

> should return a list of provinces

**Structure (Yaml):**

~~~yaml
info:
  description: "Provinces api response"
  #
  # pagination information
  #
  required:
    - "count"
    - "per_page"
    - "next_page"
    - "prev_page"
    - "provinces"
  properties:
    count:
      type: "number"
    per_page:
      type: "number"
    next_page:
      type: "number"
    prev_page:
      type: "number"
    provinces:
      type: "array"
      items:
        type: "object"
        properties:
          bagheri_id:
            type: "number"
          name:
            type: "string"
          en_name:
            type: "string"
          #
          # if province hasn't a teacher ,teacher id of
          # a higher level should be returned
          #
          teacher_id:
            type: "number"

          teacher_id_f:
            type: "number"

          teacher_id_m:
            type: "number"
~~~
**Sample (json):**

~~~Json
{
  "count": 2000,
  "per_page": 100,
  "next_page": 2,
  "prev_page": 1,
  "provinces": [
    {
      "bagheri_id": 1,
      "name": "چهار محال و بختیاری",
      "en_name": "chahar-mahal-va-bakhtiari",
      "teacher_id": 1,
      "teacher_id_f": 1,
      "teacher_id_m": 1
    },
    {
      "bagheri_id": 2,
      "name": "قم",
      "en_name": "Qom",
      "teacher_id": 2,
      "teacher_id_f": 1,
      "teacher_id_m": 1
    },
    {
      "bagheri_id": 3,
      "name": "مرکزی",
      "en_name": "Markazi",
      "teacher_id": 3,
      "teacher_id_f": 1,
      "teacher_id_m": 1
    },
    {
      "bagheri_id": 4,
      "name": "تهران",
      "en_name": "Tehran",
      "teacher_id": 4,
      "teacher_id_f": 1,
      "teacher_id_m": 1
    }
  ]
}

~~~

####`Counties:`

> should return a list of counties (cities)

**Structure (Yaml):**

~~~yaml
info:
  description: "County (city) api response"
  #
  # pagination information
  #
  required:
    - "count"
    - "per_page"
    - "next_page"
    - "prev_page"
    - "counties"
  properties:
    count:
      type: "number"
    per_page:
      type: "number"
    next_page:
      type: "number"
    prev_page:
      type: "number"
    counties:
      type: "array"
      items:
        type: "object"
        properties:
          bagheri_id:
            type: "number"
          name:
            type: "string"
          en_name:
            type: "string"
          province_id:
            type: "number"
          #
          # if county hasn't a teacher ,teacher id of
          # a higher level should be returned
          #
          teacher_id:
            type: "number"
~~~

**Sample (json)**

~~~Json
{
  "count": 2000,
  "per_page": 100,
  "next_page": 2,
  "prev_page": 1,
  "counties": [
    {
      "bagheri_id": 1,
      "name": "شهرکرد",
      "en_name": "shahr-e-kord",
      "province_id": 1,
      "teacher_id": 1
    },
    {
      "bagheri_id": 2,
      "name": "قم",
      "en_name": "Qom",
      "province_id": 2,
      "teacher_id": 2
    },
    {
      "bagheri_id": 3,
      "name": "مرکزی",
      "en_name": "Markazi",
      "province_id": 3,
      "teacher_id": 3
    },
    {
      "bagheri_id": 4,
      "name": "تهران",
      "en_name": "Tehran",
      "province_id": 4,
      "teacher_id": 4
    }
  ]
}
~~~

####`Camps:`

> should return a list of Camps

**Structure (Yaml):**

~~~yaml
info:
  description: "Camp api response"
  #
  # pagination information
  #
  required:
    - "count"
    - "per_page"
    - "next_page"
    - "prev_page"
    - "camps"
  properties:
    count:
      type: "number"
    per_page:
      type: "number"
    next_page:
      type: "number"
    prev_page:
      type: "number"
    camps:
      type: "array"
      items:
        type: "object"
        properties:
          bagheri_id:
            type: "number"
          name:
            type: "string"
          county_id:
            type: "number"
          #
          # if camp hasn't a teacher ,teacher id of
          # a higher level should be returned
          #
          teacher_id:
            type: "number"
~~~

**Sample (json):**

~~~Json
{
  "count": 2000,
  "per_page": 100,
  "next_page": 2,
  "prev_page": 1,
  "camps": [
    {
      "bagheri_id": 1,
      "name": "نام فارسی قرارگاه",
      "county_id": 1,
      "teacher_id": 1
    },
    {
      "bagheri_id": 2,
      "name": "نام فارسی قرارگاه",
      "county_id": 2,
      "teacher_id": 2
    },
    {
      "bagheri_id": 3,
      "name": "نام فارسی قرارگاه",
      "county_id": 3,
      "teacher_id": 3
    },
    {
      "bagheri_id": 4,
      "name": "نام فارسی قرارگاه",
      "county_id": 4,
      "teacher_id": 4
    }
  ]
}
~~~

####`Schools:`

> should return a list of Schools

**Structure (Yaml):**

~~~yaml
info:
  description: "School api response"
  #
  # pagination information
  #
  required: 
    - "count"
    - "per_page"
    - "next_page"
    - "prev_page"
    - "schools"
  properties: 
    count: 
      type: "number"
    per_page: 
      type: "number"
    next_page: 
      type: "number"
    prev_page: 
      type: "number"
    schools: 
      type: "array"
      items: 
        type: "object"
        properties: 
          bagheri_id: 
            type: "number"
          name: 
            type: "string"
          #
          # can be female or male
          #
          gender: 
            type: "string"
          camp_id:
            type: "number"
          #
          # if school hasn't a teacher ,teacher id of
          # a higher level should be returned
          #
          teacher_id:
            type: "number"
          number_of_students:
            type: "number"
          number_of_users:
            type: "number"
~~~

**Sample (json):**

~~~Json
{
  "count": 2000,
  "per_page": 100,
  "next_page": 2,
  "prev_page": 1,
  "schools": [
    {
      "bagheri_id": 1,
      "name": "نام فارسی مدرسه",
      "gender": "female|male",
      "camp_id": 1,
      "teacher_id": 1,
      "number_of_students": 1,
      "number_of_users": 1
    },
    {
      "bagheri_id": 1,
      "name": "نام فارسی مدرسه",
      "gender": "female|male",
      "camp_id": 1,
      "teacher_id": 1,
      "number_of_students": 1,
      "number_of_users": 1
    }
  ]
}
~~~
	
####`Student:`

> should return a list of Students

**Structure (Yaml):**

~~~yaml
info:
  description: "Student api response"
  required:
    - "count"
    - "per_page"
    - "next_page"
    - "prev_page"
    - "students"
  properties:
    count:
      type: "number"
    per_page:
      type: "number"
    next_page:
      type: "number"
    prev_page:
      type: "number"
    students:
      type: "array"
      items:
        type: "object"
        properties:
          first_name:
            type: "string"
          last_name:
            type: "string"
          phone_number:
            type: "string"
          #
          # can be female or male
          #
          gender:
            type: "string"
          #
          # Student national id
          #
          username:
            type: "string"
          bagheri_school_id:
            type: "number"
~~~

**Sample (json):**

~~~Json
{
  "count": 2000,
  "per_page": 100,
  "next_page": 2,
  "prev_page": 1,
  "students": [
    {
      "first_name": "mo",
      "last_name": "mi",
      "phone_number": "09xxxxxxxxxx",
      "gender": "female|male",
      "username": "4621234569",
      "bagheri_school_id": 1
    },
    {
      "first_name": "mo",
      "last_name": "mi",
      "phone_number": "09xxxxxxxxxx",
      "gender": "female|male",
      "username": "4621234569",
      "bagheri_school_id": 1
    },
    {
      "first_name": "mo",
      "last_name": "mi",
      "phone_number": "09xxxxxxxxxx",
      "gender": "female|male",
      "username": "4621234569",
      "bagheri_school_id": 1
    },
    {
      "first_name": "mo",
      "last_name": "mi",
      "phone_number": "09xxxxxxxxxx",
      "gender": "female|male",
      "username": "4621234569",
      "bagheri_school_id": 1
    }
  ]
}
~~~