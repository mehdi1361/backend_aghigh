# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import datetime

from dateutil import rrule
from django.conf import settings as django_settings
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.base import ModelBase
from django.template.defaultfilters import date
from django.utils import timezone
from django.utils.six import with_metaclass
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.contrib.auth.models import User as DjangoUser

from apps.schedule.models.calendars import Calendar
from apps.schedule.models.rules import Rule
from apps.schedule.utils import OccurrenceReplacer, get_model_bases

freq_dict_order = {
    'YEARLY': 0,
    'MONTHLY': 1,
    'WEEKLY': 2,
    'DAILY': 3,
    'HOURLY': 4,
    'MINUTELY': 5,
    'SECONDLY': 6
}
param_dict_order = {
    'byyearday': 1,
    'bymonth': 1,
    'bymonthday': 2,
    'byweekno': 2,
    'byweekday': 3,
    'byhour': 4,
    'byminute': 5,
    'bysecond': 6
}


class EventManager(models.Manager):
    def get_for_object(self, content_object, distinction='', inherit=True):
        return EventRelation.objects.get_events_for_object(content_object, distinction, inherit)


class Event(with_metaclass(ModelBase, *get_model_bases('Event'))):
    '''
    This model stores meta data for a date.  You can relate this data to many
    other models.
    '''
    start = models.DateTimeField(_("start"), db_index=True)
    end = models.DateTimeField(_("end"), null=True, blank=True,
                               help_text=_("The end time must be later than the start time.")
                               )
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    creator = models.ForeignKey(
        DjangoUser,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
        related_name='user')

    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)
    rule = models.ForeignKey(
        Rule,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("rule"),
        help_text=_("Select '----' for a one time only event."))
    end_recurring_period = models.DateTimeField(_("end recurring period"), null=True, blank=True, db_index=True,
                                                help_text=_("This date is ignored for one time only events."))
    calendar = models.ForeignKey(
        Calendar,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("calendar"))

    color_event = models.CharField(_("Color event"), blank=True, max_length=10)

    by_week_day = models.CharField(_("By week day"), blank=True, max_length=26, default="")
    objects = EventManager()

    all_day = models.BooleanField(default=True)

    class Meta(object):
        verbose_name = _('event')
        verbose_name_plural = _('events')
        app_label = 'schedule'
        index_together = (
            ('start', 'end'),
        )

    def __str__(self):
        return ugettext('%(title)s: %(start)s - %(end)s') % {
            'title': self.title,
            'start': date(self.start, django_settings.DATE_FORMAT),
            'end': date(self.end, django_settings.DATE_FORMAT),
        }

    @property
    def seconds(self):
        return (self.end - self.start).total_seconds()

    @property
    def minutes(self):
        return float(self.seconds) / 60

    @property
    def hours(self):
        return float(self.seconds) / 3600

    def get_absolute_url(self):
        return reverse('event', args=[self.id])

    def get_occurrences(self, start, end, clear_prefetch=True):

        if clear_prefetch:
            persisted_occurrences = self.occurrence_set.select_related(None).all()
        else:
            persisted_occurrences = self.occurrence_set.all()
        occ_replacer = OccurrenceReplacer(persisted_occurrences)
        occurrences = self._get_occurrence_list(start, end)
        final_occurrences = []
        for occ in occurrences:
            # replace occurrences with their persisted counterparts
            if occ_replacer.has_occurrence(occ):
                p_occ = occ_replacer.get_occurrence(occ)
                # ...but only if they are within this period
                if p_occ.start < end and p_occ.end >= start:
                    final_occurrences.append(p_occ)
            else:
                final_occurrences.append(occ)
        # then add persisted occurrences which originated outside of this period but now
        # fall within it
        final_occurrences += occ_replacer.get_additional_occurrences(start, end)
        return final_occurrences

    def get_rrule_object(self, tzinfo):
        from dateutil.rrule import WEEKLY, MO, TU, WE, TH, FR, SA, SU
        if self.rule is None:
            return
        params = self._event_params()
        frequency = self.rule.rrule_frequency()
        if timezone.is_naive(self.start):
            dtstart = self.start
        else:
            dtstart = tzinfo.normalize(self.start).replace(tzinfo=None)

        if self.end_recurring_period is None:
            until = None
        elif timezone.is_naive(self.end_recurring_period):
            until = self.end_recurring_period
        else:
            until = tzinfo.normalize(
                self.end_recurring_period.astimezone(tzinfo)).replace(tzinfo=None)

        if frequency == WEEKLY:
            list_week_day = []
            for day in self.by_week_day.split(','):
                if day in ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]:
                    list_week_day.append(eval(day))

            if list_week_day:
                params["byweekday"] = tuple(list_week_day)

            return rrule.rrule(
                frequency,
                dtstart=dtstart,
                until=until,
                **params,
            )

        return rrule.rrule(frequency, dtstart=dtstart, until=until, **params)

    def _create_occurrence(self, start, end=None):
        if end is None:
            end = start + (self.end - self.start)

        return Occurrence(event=self, start=start, end=end, original_start=start, original_end=end, all_day=self.all_day)

    def get_occurrence(self, date):
        use_naive = timezone.is_naive(date)
        tzinfo = timezone.utc
        if timezone.is_naive(date):
            date = timezone.make_aware(date, timezone.utc)
        if date.tzinfo:
            tzinfo = date.tzinfo
        rule = self.get_rrule_object(tzinfo)
        if rule:
            next_occurrence = rule.after(tzinfo.normalize(date).replace(tzinfo=None), inc=True)
            next_occurrence = tzinfo.localize(next_occurrence)
        else:
            next_occurrence = self.start
        if next_occurrence == date:
            try:
                return Occurrence.objects.get(event=self, original_start=date)
            except Occurrence.DoesNotExist:
                if use_naive:
                    next_occurrence = timezone.make_naive(next_occurrence, tzinfo)
                return self._create_occurrence(next_occurrence)

    def _get_occurrence_list(self, start, end):
        """
        Returns a list of occurrences that fall completely or partially inside
        the timespan defined by start (inclusive) and end (exclusive)
        """
        if self.rule is not None:
            duration = self.end - self.start
            use_naive = timezone.is_naive(start)

            # Use the timezone from the start date
            tzinfo = timezone.utc
            if start.tzinfo:
                tzinfo = start.tzinfo

            # Limit timespan to recurring period
            occurrences = []
            if self.end_recurring_period and self.end_recurring_period < end:
                end = self.end_recurring_period

            start_rule = self.get_rrule_object(tzinfo)
            start = start.replace(tzinfo=None)
            if timezone.is_aware(end):
                end = tzinfo.normalize(end).replace(tzinfo=None)

            o_starts = []

            # Occurrences that start before the timespan but ends inside or after timespan
            closest_start = start_rule.before(start, inc=False)
            if closest_start is not None and closest_start + duration > start:
                o_starts.append(closest_start)

            # Occurrences starts that happen inside timespan (end-inclusive)
            occs = start_rule.between(start, end, inc=True)
            # The occurrence that start on the end of the timespan is potentially
            # included above, lets remove if thats the case.
            if len(occs) > 0:
                if occs[-1] == end:
                    occs.pop()
            # Add the occurrences found inside timespan
            o_starts.extend(occs)

            # Create the Occurrence objects for the found start dates
            for o_start in o_starts:
                o_start = tzinfo.localize(o_start)
                if use_naive:
                    o_start = timezone.make_naive(o_start, tzinfo)
                o_end = o_start + duration
                occurrence = self._create_occurrence(o_start, o_end)
                if occurrence not in occurrences:
                    occurrences.append(occurrence)
            return occurrences
        else:
            # check if event is in the period
            if self.start < end and self.end > start:
                return [self._create_occurrence(self.start)]
            else:
                return []

    def _occurrences_after_generator(self, after=None):
        """
        returns a generator that produces unpresisted occurrences after the
        datetime ``after``. (Optionally) This generator will return up to
        ``max_occurrences`` occurrences or has reached ``self.end_recurring_period``, whichever is smallest.
        """

        tzinfo = timezone.utc
        if after is None:
            after = timezone.now()
        elif not timezone.is_naive(after):
            tzinfo = after.tzinfo
        rule = self.get_rrule_object(tzinfo)
        if rule is None:
            if self.end > after:
                yield self._create_occurrence(self.start, self.end)
            return
        date_iter = iter(rule)
        difference = self.end - self.start
        loop_counter = 0
        for o_start in date_iter:
            o_start = tzinfo.localize(o_start)
            o_end = o_start + difference
            if o_end > after:
                yield self._create_occurrence(o_start, o_end)

            loop_counter += 1

    def occurrences_after(self, after=None, max_occurrences=None):
        """
        returns a generator that produces occurrences after the datetime
        ``after``.  Includes all of the persisted Occurrences. (Optionally) This generator will return up to
        ``max_occurrences`` occurrences or has reached ``self.end_recurring_period``, whichever is smallest.
        """
        if after is None:
            after = timezone.now()
        occ_replacer = OccurrenceReplacer(self.occurrence_set.all())
        generator = self._occurrences_after_generator(after)
        trickies = list(self.occurrence_set.filter(original_start__lte=after, start__gte=after).order_by('start'))
        for index, nxt in enumerate(generator):
            if max_occurrences and index > max_occurrences - 1:
                break
            if (len(trickies) > 0 and (nxt is None or nxt.start > trickies[0].start)):
                yield trickies.pop(0)
            yield occ_replacer.get_occurrence(nxt)

    @property
    def event_start_params(self):
        start = self.start
        params = {
            'byyearday': start.timetuple().tm_yday,
            'bymonth': start.month,
            'bymonthday': start.day,
            'byweekno': start.isocalendar()[1],
            'byweekday': start.weekday(),
            'byhour': start.hour,
            'byminute': start.minute,
            'bysecond': start.second
        }
        return params

    @property
    def event_rule_params(self):
        return self.rule.get_params()

    def _event_params(self):
        freq_order = freq_dict_order[self.rule.frequency]
        rule_params = self.event_rule_params
        start_params = self.event_start_params
        event_params = {}

        if len(rule_params) == 0:
            return event_params

        for param in rule_params:
            # start date influences rule params
            if (param in param_dict_order and param_dict_order[param] > freq_order and
                    param in start_params):
                sp = start_params[param]
                if sp == rule_params[param] or (
                        hasattr(rule_params[param], '__iter__') and
                        sp in rule_params[param]):
                    event_params[param] = [sp]
                else:
                    event_params[param] = rule_params[param]
            else:
                event_params[param] = rule_params[param]

        return event_params

    @property
    def event_params(self):
        event_params = self._event_params()
        start = self.effective_start
        if not start:
            empty = True
        elif self.end_recurring_period and start > self.end_recurring_period:
            empty = True
        return event_params, empty

    @property
    def effective_start(self):
        if self.pk and self.end_recurring_period:
            occ_generator = self._occurrences_after_generator(self.start)
            try:
                return next(occ_generator).start
            except StopIteration:
                pass
        elif self.pk:
            return self.start
        return None

    @property
    def effective_end(self):
        if self.pk and self.end_recurring_period:
            params, empty = self.event_params
            if empty or not self.effective_start:
                return None
            elif self.end_recurring_period:
                occ = None
                occ_generator = self._occurrences_after_generator(self.start)
                for occ in occ_generator:
                    pass
                return occ.end
        elif self.pk:
            return datetime.max
        return None


class EventRelationManager(models.Manager):

    def get_events_for_object(self, content_object, distinction='', inherit=True):

        ct = ContentType.objects.get_for_model(type(content_object))
        if distinction:
            dist_q = Q(eventrelation__distinction=distinction)
            cal_dist_q = Q(calendar__calendarrelation__distinction=distinction)
        else:
            dist_q = Q()
            cal_dist_q = Q()
        if inherit:
            inherit_q = Q(
                cal_dist_q,
                calendar__calendarrelation__object_id=content_object.id,
                calendar__calendarrelation__content_type=ct,
                calendar__calendarrelation__inheritable=True,
            )
        else:
            inherit_q = Q()
        event_q = Q(dist_q, eventrelation__object_id=content_object.id, eventrelation__content_type=ct)
        return Event.objects.filter(inherit_q | event_q)

    def create_relation(self, event, content_object, distinction=''):
        """
        Creates a relation between event and content_object.
        See EventRelation for help on distinction.
        """
        return EventRelation.objects.create(
            event=event,
            distinction=distinction,
            content_object=content_object)


class EventRelation(with_metaclass(ModelBase, *get_model_bases('EventRelation'))):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("event"))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()
    content_object = fields.GenericForeignKey('content_type', 'object_id')
    distinction = models.CharField(_("distinction"), max_length=20)

    objects = EventRelationManager()

    class Meta(object):
        verbose_name = _("event relation")
        verbose_name_plural = _("event relations")
        app_label = 'schedule'

    def __str__(self):
        return '%s(%s)-%s' % (self.event.title, self.distinction, self.content_object)


class Occurrence(with_metaclass(ModelBase, *get_model_bases('Occurrence'))):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name=_("event"))
    all_day = models.BooleanField(default=True)

    title = models.CharField(_("title"), max_length=255, blank=True)
    description = models.TextField(_("description"), blank=True)
    start = models.DateTimeField(_("start"), db_index=True)
    end = models.DateTimeField(_("end"), db_index=True, null=True)
    cancelled = models.BooleanField(_("cancelled"), default=False)
    original_start = models.DateTimeField(_("original start"))
    original_end = models.DateTimeField(_("original end"))
    created_on = models.DateTimeField(_("created on"), auto_now_add=True)
    updated_on = models.DateTimeField(_("updated on"), auto_now=True)
    color_event = models.CharField(_("Color event"), blank=True, max_length=10)

    class Meta(object):
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")
        app_label = 'schedule'
        index_together = (
            ('start', 'end'),
        )

    def __init__(self, *args, **kwargs):
        super(Occurrence, self).__init__(*args, **kwargs)
        if not self.title and self.event_id:
            self.title = self.event.title
        if not self.description and self.event_id:
            self.description = self.event.description

    def moved(self):
        return self.original_start != self.start or self.original_end != self.end

    moved = property(moved)

    def move(self, new_start, new_end):
        self.start = new_start
        self.end = new_end
        self.save()

    def cancel(self):
        self.cancelled = True
        self.save()

    def uncancel(self):
        self.cancelled = False
        self.save()

    @property
    def seconds(self):
        return (self.end - self.start).total_seconds()

    @property
    def minutes(self):
        return float(self.seconds) / 60

    @property
    def hours(self):
        return float(self.seconds) / 3600

    def get_absolute_url(self):
        if self.pk is not None:
            return reverse('occurrence', kwargs={'occurrence_id': self.pk,
                                                 'event_id': self.event.id})
        return reverse('occurrence_by_date', kwargs={
            'event_id': self.event.id,
            'year': self.start.year,
            'month': self.start.month,
            'day': self.start.day,
            'hour': self.start.hour,
            'minute': self.start.minute,
            'second': self.start.second,
        })

    def get_cancel_url(self):
        if self.pk is not None:
            return reverse('cancel_occurrence', kwargs={'occurrence_id': self.pk,
                                                        'event_id': self.event.id})
        return reverse('cancel_occurrence_by_date', kwargs={
            'event_id': self.event.id,
            'year': self.start.year,
            'month': self.start.month,
            'day': self.start.day,
            'hour': self.start.hour,
            'minute': self.start.minute,
            'second': self.start.second,
        })

    def get_edit_url(self):
        if self.pk is not None:
            return reverse('edit_occurrence', kwargs={'occurrence_id': self.pk,
                                                      'event_id': self.event.id})
        return reverse('edit_occurrence_by_date', kwargs={
            'event_id': self.event.id,
            'year': self.start.year,
            'month': self.start.month,
            'day': self.start.day,
            'hour': self.start.hour,
            'minute': self.start.minute,
            'second': self.start.second,
        })

    def __str__(self):
        return ugettext("%(start)s to %(end)s") % {
            'start': date(self.start, django_settings.DATE_FORMAT),
            'end': date(self.end, django_settings.DATE_FORMAT)
        }

    def __lt__(self, other):
        return self.end < other.end

    def __eq__(self, other):
        return (isinstance(other, Occurrence) and
                self.original_start == other.original_start and
                self.original_end == other.original_end)
