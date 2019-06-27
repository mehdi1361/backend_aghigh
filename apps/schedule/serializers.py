from rest_framework import serializers
from apps.schedule.models.events import Event, Occurrence
from apps.schedule.models.annual import AnnualEvents


class AnnualEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnualEvents
        fields = ("title",)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class OccurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occurrence
        fields = '__all__'
