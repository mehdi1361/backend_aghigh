import heapq

from functools import wraps
from annoying.functions import get_object_or_None
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.utils import timezone
from django.utils.module_loading import import_string

from apps.schedule.settings import (
    CALENDAR_VIEW_PERM, CHECK_CALENDAR_PERM_FUNC, CHECK_EVENT_PERM_FUNC,
    CHECK_OCCURRENCE_PERM_FUNC,
)


class EventListManager(object):
    """
    This class is responsible for doing functions on a list of events. It is
    used to when one has a list of events and wants to access the occurrences
    from these events in as a group
    """

    def __init__(self, events):
        self.events = events

    def occurrences_after(self, after=None):
        """
        It is often useful to know what the next occurrence is given a list of
        events.  This function produces a generator that yields the
        the most recent occurrence after the date ``after`` from any of the
        events in ``self.events``
        """
        from apps.schedule.models import Occurrence

        if after is None:
            after = timezone.now()
        occ_replacer = OccurrenceReplacer(
            Occurrence.objects.filter(event__in=self.events))
        generators = [event._occurrences_after_generator(after) for event in self.events]
        occurrences = []

        for generator in generators:
            try:
                heapq.heappush(occurrences, (next(generator), generator))
            except StopIteration:
                pass

        while occurrences:
            generator = occurrences[0][1]

            try:
                next_occurence = heapq.heapreplace(occurrences, (next(generator), generator))[0]
            except StopIteration:
                next_occurence = heapq.heappop(occurrences)[0]
            yield occ_replacer.get_occurrence(next_occurence)


class OccurrenceReplacer(object):
    """
    When getting a list of occurrences, the last thing that needs to be done
    before passing it forward is to make sure all of the occurrences that
    have been stored in the datebase replace, in the list you are returning,
    the generated ones that are equivalent.  This class makes this easier.
    """

    def __init__(self, persisted_occurrences):
        lookup = [((occ.event.id, occ.original_start, occ.original_end), occ) for
                  occ in persisted_occurrences]
        self.lookup = dict(lookup)

    def get_occurrence(self, occ):
        """
        Return a persisted occurrences matching the occ and remove it from lookup since it
        has already been matched
        """
        return self.lookup.pop(
            (occ.event.id, occ.original_start, occ.original_end),
            occ)

    def has_occurrence(self, occ):
        try:
            return (occ.event.id, occ.original_start, occ.original_end) in self.lookup
        except TypeError:
            if not self.lookup:
                return False
            else:
                raise TypeError('A problem with checking if a persisted occurence exists has occured!')

    def get_additional_occurrences(self, start, end):
        """
        Return persisted occurrences which are now in the period
        """
        return [occ for _, occ in list(self.lookup.items()) if (occ.start < end and occ.end >= start and not occ.cancelled)]


def get_occurrence(request, *args, **kwargs):
    from apps.schedule.models import Occurrence
    occurrence = None
    if 'occurrence_id' in kwargs:
        occurrence = get_object_or_None(Occurrence, id=kwargs['occurrence_id'])
    elif request.GET:
        occurrence = get_object_or_None(
            Occurrence,
            id=request.GET.get('occurrence_id'))
    elif request.POST:
        occurrence = get_object_or_None(
            Occurrence,
            id=request.POST.get('occurrence_id'))
    return occurrence


def get_event(occurrence, request, *args, **kwargs):
    from apps.schedule.models import Event
    event = None
    if occurrence:
        event = occurrence.event
    elif 'event_id' in kwargs:
        event = get_object_or_None(Event, id=kwargs['event_id'])
    elif request.GET:
        event = get_object_or_None(
            Event,
            id=request.GET.get('event_id'))
    elif request.POST:
        event = get_object_or_None(
            Event,
            id=request.POST.get('event_id'))
    return event


def get_calendar(event, request, *args, **kwargs):
    from apps.schedule.models import Calendar
    calendar = None
    if event:
        calendar = event.calendar
    elif 'calendar_slug' in kwargs:
        calendar = get_object_or_None(Calendar, slug=kwargs['calendar_slug'])
    elif request.GET:
        calendar = get_object_or_None(
            Calendar,
            slug=request.GET.get('calendar_slug'))
    elif request.POST:
        calendar = get_object_or_None(
            Calendar,
            slug=request.POST.get('calendar_slug'))
    return calendar


def get_objects(request, *args, **kwargs):
    occurrence = get_occurrence(request, *args, **kwargs)
    event = get_event(occurrence, request, *args, **kwargs)
    calendar = get_calendar(event, request, *args, **kwargs)
    return occurrence, event, calendar


def check_occurrence_permissions(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        user = request.user
        if not user:
            return HttpResponseRedirect(settings.LOGIN_URL)
        occurrence, event, calendar = get_objects(request, *args, **kwargs)
        if calendar and event:
            allowed = (CHECK_EVENT_PERM_FUNC(event, user) and
                       CHECK_CALENDAR_PERM_FUNC(calendar, user) and
                       CHECK_OCCURRENCE_PERM_FUNC(occurrence, user))
            if not allowed:
                return HttpResponseRedirect(settings.LOGIN_URL)
            # all checks passed
            return function(request, *args, **kwargs)
        return HttpResponseNotFound('<h1>Page not found</h1>')
    return decorator


def check_event_permissions(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        user = request.user
        if not user:
            return HttpResponseRedirect(settings.LOGIN_URL)
        occurrence, event, calendar = get_objects(request, *args, **kwargs)
        if calendar:
            allowed = (CHECK_EVENT_PERM_FUNC(event, user) and
                       CHECK_CALENDAR_PERM_FUNC(calendar, user))
            if not allowed:
                return HttpResponseRedirect(settings.LOGIN_URL)
            # all checks passed
            return function(request, *args, **kwargs)
        return HttpResponseNotFound('<h1>Page not found</h1>')
    return decorator


def check_calendar_permissions(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if CALENDAR_VIEW_PERM:
            user = request.user
            if not user:
                return HttpResponseRedirect(settings.LOGIN_URL)
            occurrence, event, calendar = get_objects(request, *args, **kwargs)
            if calendar:
                allowed = CHECK_CALENDAR_PERM_FUNC(calendar, user)
                if not allowed:
                    return HttpResponseRedirect(settings.LOGIN_URL)
                # all checks passed
                return function(request, *args, **kwargs)
            return HttpResponseNotFound('<h1>Page not found</h1>')
        return function(request, *args, **kwargs)
    return decorator


def coerce_date_dict(date_dict):
    """
    given a dictionary (presumed to be from request.GET) it returns a tuple
    that represents a date. It will return from year down to seconds until one
    is not found.  ie if year, month, and seconds are in the dictionary, only
    year and month will be returned, the rest will be returned as min. If none
    of the parts are found return an empty tuple.
    """
    keys = ['year', 'month', 'day', 'hour', 'minute', 'second']
    ret_val = {
        'year': 1,
        'month': 1,
        'day': 1,
        'hour': 0,
        'minute': 0,
        'second': 0}
    modified = False
    for key in keys:
        try:
            ret_val[key] = int(date_dict[key])
            modified = True
        except KeyError:
            break
    return modified and ret_val or {}


def get_model_bases(model_class_name):
    from django.db.models import Model
    base_classes = getattr(settings, 'SCHEDULER_BASE_CLASSES', {})

    if isinstance(base_classes, dict):
        base_class_names = base_classes.get(model_class_name, [])
    else:
        base_class_names = base_classes

    if base_class_names:
        return [import_string(x) for x in base_class_names]
    else:
        return [Model]


def get_admin_model_fields(model_class_name):
    admin_fields = getattr(settings, 'SCHEDULER_ADMIN_FIELDS', {})
    if isinstance(admin_fields, dict):
        model_fields = admin_fields.get(model_class_name, [])
    else:
        model_fields = admin_fields
    if model_fields:
        return model_fields
    else:
        return []
