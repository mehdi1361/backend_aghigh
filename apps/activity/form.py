from django import forms
from apps.activity.models import ActivityAdditionalFields, ImageActivity, FileActivity


class ActivityAdditionalFieldForm(forms.ModelForm):
    class Meta:
        model = ActivityAdditionalFields
        fields = [
            'additional_field',
            'value',
            'comment',
            'status'
        ]

    def __init__(self, *args, **kwargs):
        super(ActivityAdditionalFieldForm, self).__init__(*args, **kwargs)
        if "instance" in kwargs and kwargs["instance"].status:
            self.fields['comment'].widget.attrs["readonly"] = "readonly"
            self.fields['status'].widget.attrs["disabled"] = "disabled"


class ActivityFileForm(forms.ModelForm):
    class Meta:
        model = FileActivity
        fields = [
            'comment',
            'status'
        ]

    def __init__(self, *args, **kwargs):
        super(ActivityFileForm, self).__init__(*args, **kwargs)
        if "instance" in kwargs and kwargs["instance"].status:
            self.fields['comment'].widget.attrs["readonly"] = "readonly"
            self.fields['status'].widget.attrs["disabled"] = "disabled"


class ActivityImageForm(forms.ModelForm):
    class Meta:
        model = ImageActivity
        fields = [
            'comment',
            'status'
        ]

    def __init__(self, *args, **kwargs):
        super(ActivityImageForm, self).__init__(*args, **kwargs)
        if "instance" in kwargs and kwargs["instance"].status:
            self.fields['comment'].widget.attrs["readonly"] = "readonly"
            self.fields['status'].widget.attrs["disabled"] = "disabled"
