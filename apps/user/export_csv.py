import xlwt
from django.http import HttpResponse


def export_xls_teacher(modeladmin, request, queryset):
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=teachers.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("MyModel")

    row_num = 0

    columns = [
        (u"نام و نام خانوادگی", 8000),
        (u"شماره ملی", 6000),
        (u"سطح", 8000),
    ]

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = columns[col_num][1]

    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1

    for obj in queryset:
        row_num += 1
        row = [
            obj.first_name + "\b\b" + obj.last_name,
            obj.username,
            "\n ,".join([p.title for p in obj.coach_levels.all()]),
        ]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


export_xls_teacher.short_description = u"خروجی اکسل"
