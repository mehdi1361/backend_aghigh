from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User as DjangoUser
from apps.activity import static
from apps.common.fields import ImageWithThumbsField
from apps.common.helpers.media_filename_hash import MediaFileNameHash
from apps.common.models import TimeStampedModel


class BaseUser(DjangoUser, TimeStampedModel):
    gender = models.CharField(max_length=10, choices=static.gender_choice, default=None, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    last_visit = models.DateTimeField(null=True, blank=True, verbose_name=_("Last visit"))
    user_is_test = models.BooleanField(default=False, verbose_name=_("User Is Test"))
    image = ImageWithThumbsField(
        upload_to=MediaFileNameHash("user_image"),
        default=None,
        sizes=((200, 200), ),
        preserve_ratio=True,
        null=True,
        blank=True,
        verbose_name=_("Image")
    )

    class Meta:
        verbose_name = _("Base User")
        verbose_name_plural = _("Base User")

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    # def last_visit_persian_date(self):
    #     from apps.common.utils import gregorian_to_persian_chart
    #     if self.last_visit:
    #         return gregorian_to_persian_chart(self.last_visit, str_type="%Y/%m/%d %H:%M:%S")
    #     else:
    #         return ""
    #
    # last_visit_persian_date.admin_order_field = 'last_visit'

    def last_login_persian_date(self):
        from apps.common.utils import gregorian_to_persian_chart
        if self.last_login:
            return gregorian_to_persian_chart(self.last_login, str_type="%Y/%m/%d %H:%M:%S")
        else:
            return ""

    last_login_persian_date.admin_order_field = 'last_login'


class UserSession(models.Model):
    user_name = models.CharField(_('user'), unique=True, max_length=200)
    name = models.CharField(_('name'), max_length=200, null=True)
    role = models.CharField(_('role'), max_length=50, null=True)
    created_date = models.DateTimeField(_('created date'), auto_now_add=True)
    updated_date = models.DateTimeField(_('updated date'), null=True, blank=True)
    last_login_date = models.DateTimeField(_('last login date'), null=True, blank=True)

    def __str__(self):
        return "{}".format(self.user_name)

    class Meta:
        db_table = "user_session"
        verbose_name = _('user_session')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        from utils.user_type import get_user_type

        base_user = BaseUser.objects.filter(
            is_active=True,
            username=self.user_name,
        )
        user = base_user.get()
        self.role = get_user_type(user)
        self.name = "{} {}".format(user.first_name, user.last_name)
        super(UserSession, self).save()

        @property
        def active(self):
            return
