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