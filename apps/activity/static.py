from django.utils.translation import ugettext as _

REVIEW_STATE = {
    "GREEN": "green",
    "YELLOW": "yellow",
    "RED": "red",
    "DARK": "dark"
}

GENDER = {
    "female": "female",
    "male": "male"
}

gender_choice = (
    ('female', _('female')),
    ('male', _('male'))
)

activity_state_choice = (
    ('NEW', _('New Activity')),
    ('SHE', _('Should Edit')),
    ('SHR', _('Should Review')),
    ('ACCEPT', _('Accept')),
    ('TIL', _('Temporary in league')),
    ('ARCHIVE', _('Temporary archive')),
    ('BAN', _('Ban')),
)

field_type_choice = (
    ('number', 'Number'),
    ('recommended', 'Recommended'),
    ('text_box', 'Text Box'),
    ('check_box', 'Check Box'),
    ('drop_down', 'Drop Down'),
    ('sub_form', 'Sub Form'),
    ('file_upload', 'File Upload'),
    ('image_upload', 'Image Upload'),
)

function_department_choice = (
    ('func1', 'Function 1'),
    ('func2', 'Function 2'),
    ('func3', 'Function 3'),
)

function_additional_fields_choice = (
    ('func1', 'صرف تعداد'),
    ('func2', 'محاسبه از کل'),
    ('func3', 'صرف برگزاری'),
)

function_additional_fields_total_number_type = (
    ('school_count', 'تعداد دانش آموزان مدرسه'),
    ('anjoman_count', 'تعداد اعضای فعال انجمن'),
    # ('func3', 'تعداد اعضای کلاس در مقطع'),
)

order_choice = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    (11, 11),
    (12, 12),
    (13, 13),
    (14, 14),
    (15, 15),
    (16, 16),
    (17, 17),
    (18, 18),
    (19, 19),
    (20, 20),
    (21, 21),
    (22, 22),
    (23, 23),
    (24, 24),
    (25, 25)
)
rate_choice = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5)
)

PROVINCE_DATA = {
    "10": {
        "province_name": "آذربایجان شرقی",
        "male": 0,
        "female": 0
    },
    "11": {
        "province_name": "آذربایجان غربی",
        "male": 0,
        "female": 0
    },
    "12": {
        "province_name": "اردبیل",
        "male": 0,
        "female": 0
    },
    "13": {
        "province_name": "اصفهان",
        "male": 0,
        "female": 0
    },
    "14": {
        "province_name": "البرز",
        "male": 0,
        "female": 0
    },
    "15": {
        "province_name": "ایلام",
        "male": 0,
        "female": 0
    },
    "16": {
        "province_name": "بوشهر",
        "male": 0,
        "female": 0
    },
    "17": {
        "province_name": "تهران",
        "male": 0,
        "female": 0
    },
    "18": {
        "province_name": "چهارمحال و بختیاری",
        "male": 0,
        "female": 0
    },
    "19": {
        "province_name": "خراسان جنوبی",
        "male": 0,
        "female": 0
    },
    "20": {
        "province_name": "خراسان رضوی",
        "male": 0,
        "female": 0
    },
    "21": {
        "province_name": "خراسان شمالی",
        "male": 0,
        "female": 0
    },
    "22": {
        "province_name": "خوزستان",
        "male": 0,
        "female": 0
    },
    "23": {
        "province_name": "زنجان",
        "male": 0,
        "female": 0
    },
    "24": {
        "province_name": "سمنان",
        "male": 0,
        "female": 0
    },
    "25": {
        "province_name": "سیستان و بلوچستان",
        "male": 0,
        "female": 0
    },
    "26": {
        "province_name": "فارس",
        "male": 0,
        "female": 0
    },
    "27": {
        "province_name": "قزوین",
        "male": 0,
        "female": 0
    },
    "28": {
        "province_name": "قم",
        "male": 0,
        "female": 0
    },
    "29": {
        "province_name": "کردستان",
        "male": 0,
        "female": 0
    },
    "30": {
        "province_name": "کرمان",
        "male": 0,
        "female": 0
    },
    "31": {
        "province_name": "کرمانشاه",
        "male": 0,
        "female": 0
    },
    "32": {
        "province_name": "کهگیلویه وبویراحمد",
        "male": 0,
        "female": 0
    },
    "33": {
        "province_name": "گلستان",
        "male": 0,
        "female": 0
    },
    "34": {
        "province_name": "گیلان",
        "male": 0,
        "female": 0
    },
    "35": {
        "province_name": "لرستان",
        "male": 0,
        "female": 0
    },
    "36": {
        "province_name": "مازندران",
        "male": 0,
        "female": 0
    },
    "37": {
        "province_name": "مرکزی",
        "male": 0,
        "female": 0
    },
    "38": {
        "province_name": "هرمزگان",
        "male": 0,
        "female": 0
    },
    "39": {
        "province_name": "همدان",
        "male": 0,
        "female": 0
    },
    "40": {
        "province_name": "یزد",
        "female": 0,
        "male": 0
    },
    "41": {
        "province_name": "استان تهران",
        "female": 0,
        "male": 0
    },
    "123456789": {
        "province_name": "استان تست",
        "female": 0,
        "male": 0
    }
}
