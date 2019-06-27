from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html
from apps.user.models import student, teacher, advisor


class StudentForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"{}/password/\">this form</a>."
        ),
    )

    class Meta:
        model = student.Student
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        if "instance" in kwargs:
            if kwargs["instance"]:
                user_id = kwargs["instance"].id

                message = "Raw passwords are not stored, so there is no way to see this " + \
                          "user's password, but you can change the password using " + \
                          "<a href=\"{}/password/\">this form</a>."

                help_text = format_html(
                    message,
                    "/admin/auth/user/" + str(user_id)
                )
                self.base_fields["password"].help_text = _(help_text)

        super(StudentForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        return self.initial["password"]


class TeacherForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"{}/password/\">this form</a>."
        ),
    )

    class Meta:
        model = teacher.Teacher
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        if "instance" in kwargs:
            if kwargs["instance"]:
                user_id = kwargs["instance"].id

                message = "Raw passwords are not stored, so there is no way to see this " + \
                          "user's password, but you can change the password using " + \
                          "<a href=\"{}/password/\">this form</a>."

                help_text = format_html(
                    message,
                    "/admin/auth/user/" + str(user_id)
                )
                self.base_fields["password"].help_text = _(help_text)

        super(TeacherForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        return self.initial["password"]


class AdvisorForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"{}/password/\">this form</a>."
        ),
    )

    class Meta:
        model = advisor.Advisor
        fields = '__all__'

    def __init__(self, *args, **kwargs):

        if "instance" in kwargs:
            if kwargs["instance"]:
                user_id = kwargs["instance"].id

                message = "Raw passwords are not stored, so there is no way to see this " + \
                          "user's password, but you can change the password using " + \
                          "<a href=\"{}/password/\">this form</a>."

                help_text = format_html(
                    message,
                    "/admin/auth/user/" + str(user_id)
                )
                self.base_fields["password"].help_text = _(help_text)

        super(AdvisorForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        return self.initial["password"]
