from django.db import models
from django.utils.translation import ugettext as _


class AnnualEvents(models.Model):
    date_type_choices = (
        ('ISLAMIC', 'قمری'),
        ('HIJRI', 'شمسی'),
        ('AD', 'میلادی')
    )
    insert_type_choices = (
        ('SYSTEM', 'قمری'),
        ('MANUAL', 'شمسی'),
    )

    date_type = models.CharField(max_length=8, choices=date_type_choices, verbose_name=_("date type"))
    insert_type = models.CharField(max_length=8, choices=insert_type_choices, verbose_name=_("date type"))
    day = models.IntegerField(verbose_name=_("day of annual"))
    month = models.IntegerField(verbose_name=_("month of annual"))
    title = models.CharField(max_length=255, verbose_name=_("title of event"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Annual Event")
        verbose_name_plural = _("Annual Events")
