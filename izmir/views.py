from django.shortcuts import render
from django.conf import settings

from rest_framework.versioning import URLPathVersioning
from rest_framework.views import APIView
from rest_framework.response import Response

import re

from . import models
from . import serializers

FORMAT = None

if settings.DEBUG:
    pass
else:
    FORMAT="json"

class Versions(URLPathVersioning):
    class v1(URLPathVersioning):
        default_version = "1.0"
        allowed_versions = ["1.0"]


# Create your views here.
class StopView:
    """
    Listing stops.
    """
    class v1(APIView):
        """
        Version: 1.x
        """
        versioning_class = Versions.v1
        model = models.Stop
        serializer = serializers.StopSerializer

        def get(self, request, format=FORMAT):
            """
            q:int|str - Query. If int, return particular stop having code, else return particular stops containing label.
            """
            q = request.GET.get("q")
            is_code = False

            if q and re.search("^[0-9]+$", q):
                is_code = True

            if is_code:
                q = int(q)
                try:
                    obj = self.model.objects.get(code=q)
                except self.model.DoesNotExist:
                    return Response(status=204)
                serializer = self.serializer(obj)
                return Response(serializer.data)
            else:
                if not q:
                    return Response(status=400)
                objs = self.model.objects.filter(label__icontains=q)
                if not objs.exists():
                    return Response(status=204)
                serializer = self.serializer(objs, many=True)
                return Response(serializer.data)


class RouteView:
    class v1(APIView):
        """
        Version: 1.x
        """

        versioning_class = Versions.v1
        models = models.Route
        serializer = serializers.RouteSerializer

        def get(self, request, format=FORMAT):
            """
            q:int|str - Query. If int, return particular route having code, else return particular routes containing label.
            """
            q = request.GET.get("q")
            is_code = False

            if q and re.search("^[0-9]+$", q):
                is_code = True

            if is_code:
                q = int(q)
                try:
                    obj = self.models.objects.get(code=q)
                except self.model.DoesNotExist:
                    return Response(status=204)
                serializer = self.serializer(obj)
                return Response(serializer.data)
            else:
                if not q:
                    return Response(status=400)
                objs = self.model.objects.filter(terminals__icontains=[q])
                if not objs.exists():
                    return Response(status=204)
                serializer = self.serializer(objs, many=True)
                return Response(serializer.data)