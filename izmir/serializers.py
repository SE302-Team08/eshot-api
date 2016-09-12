from rest_framework import serializers
from . import models

class StopSerializer(serializers.ModelSerializer):
    """
    Always base version.
    No reduction will be applied.
    """

    class Meta:
        model = models.Stop
        fields = (
            "code",
            "label",
            "coor"
        )

class RouteSerializer(serializers.ModelSerializer):
    """
    Always base version.
    No reduction will be applied.
    """

    class Meta:
        model = models.Route
        fields = (
            "code",
            "terminals",
            "stops_forwards",
            "stops_backwards",
            "departure_times_forwards",
            "departure_times_backwards"
        )

class RemainingSerializer:
    class v1(serializers.Serializer):
        """
        Remaining stops.
        Version: 1.x
        """
        code = serializers.IntegerField()
        routes = serializers.ListField(
            child=serializers.ListField(
                child=serializers.IntegerField()
            )
        )

class RouteSearchSerializer:
    class v1(serializers.ModelSerializer):
        """
        Searching Routes
        Version: 1.x
        """

        class Meta:
            model = models.Route
            fields = ["code", "terminals"]

class StopSearchSerializer:
    class v1(serializers.ModelSerializer):
        """
        Searching Stops
        Version: 1.x
        """

        class Meta:
            model = models.Stop
            fields = ["code", "label"]

class ListAnnouncementsSerializer:
    class v1(serializers.ModelSerializer):
        """
        All Announcements
        Version: 1.x
        """

        class Meta:
            model = models.Announcement
            fields = ["pk", "title"]

class AnnouncementSerializer:
    class v1(serializers.ModelSerializer):
        """
        Announcement
        Version: 1.x
        """

        class Meta:
            model = models.Announcement
            fields = ["title", "content", "is_eshot"]