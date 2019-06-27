import xlwt
from django.http import HttpResponse


def export_xls_camp(modeladmin, request, queryset):
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=teachers.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("MyModel")

    row_num = 0

    columns = [
        (u"عنوان قرارگاه", 8000),
        (u'شهرستان', 6000),
        (u"استان", 8000),
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
            obj.title,
            obj.county.title,
            obj.county.province.title,
        ]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


export_xls_camp.short_description = u"خروجی اکسل"
