from django import forms


class SubmitPoint(forms.Form):
    body = forms.CharField(required=False)
    point1 = forms.CharField()
    point2 = forms.CharField()
    point3 = forms.CharField()
    point4 = forms.CharField()
    point5 = forms.CharField()
    activity = forms.CharField()


class SimpleSearchForm(forms.Form):
    title = forms.CharField(required=False)


class FilterSearchForm(forms.Form):
    point_max = forms.IntegerField()
    point_min = forms.IntegerField()
    province = forms.CharField()
    city = forms.CharField()
    is_my_school = forms.BooleanField()
    sort_type = forms.CharField()


class SubmitSuggestForm(forms.Form):
    point_json = forms.CharField()
    activity_id = forms.IntegerField()
    description = forms.CharField()
