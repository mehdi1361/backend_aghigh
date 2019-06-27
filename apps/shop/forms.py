from django import forms


class ShopSearchForm(forms.Form):
    title = forms.CharField(required=False)
