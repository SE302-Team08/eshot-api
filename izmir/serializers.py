from rest_framework import serializers

class StopSerializer(serializers.Serializer):
    """
    Always base version.
    No reduction will be applied.
    """
    code = serializers.IntegerField()
    routes = serializers.ListField(
        child=serializers.IntegerField()
    )
    coor = serializers.ListField(
        child=serializers.IntegerField()
    )

class StopListSerializer(serializers.Serializer):
    """
    A serializer to list search queries for stops.

    Always base version.
    No reduction will be applied.
    """
    stops = serializers.ListField(
        child=serializers.IntegerField()
    )

class RouteSerializer(serializers.Serializer):
    """
    Always base version.
    No reduction will be applied.
    """

    code = serializers.IntegerField()
    stops = serializers.ListField(
        child=serializers.IntegerField()
    )

class RouteListSerializer(serializers.Serializer):
    """
    A serializer to list search queries for buses.

    Always base version.
    No reduction will be applied.
    """
    routes = serializers.ListField(
        child=serializers.IntegerField()
    )

class RemainingSerializer:
    class v1(serializers.Serializer):
        """
        Remaining stops.
        Version: 1.x
        """
        code = serializers.IntegerField()
        routes = serializers.DictField(
            child=serializers.IntegerField()
        )