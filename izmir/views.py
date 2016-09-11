from django.shortcuts import render
from django.conf import settings

from rest_framework.versioning import URLPathVersioning
from rest_framework.views import APIView
from rest_framework.response import Response

import re, redis, json, logging, requests
from bs4 import BeautifulSoup
from random import choice

from . import models
from . import serializers

logger = logging.getLogger(__name__)

FORMAT = None

if settings.DEBUG:
    pass
else:
    FORMAT="json"

class Versions:
    class v1(URLPathVersioning):
        default_version = "1.0"
        allowed_versions = ["1.0"]


# Create your views here.
class APIStatusView:
    class v1(APIView):
        """
        Responding API status.
        """

        versioning_class = Versions.v1

        def get(self, request, format=FORMAT):
            data = {
                "is_api_available": "available",
                "version": "v1",
                "expiration": settings.API_EXPIRES["v1"],
                "messages": []
            }

            res = requests.get("http://www.eshot.gov.tr/tr/OtobusumNerede/290")

            data["is_eshot_available"] = "available" if res.status_code == 200 else "unavailable"

            return Response(data)

class StopView:
    """
    Listing stops.
    """
    class v1(APIView):
        """
        Listing Stops

        PATH
        code - Getting ID or searching at labels.
        """
        versioning_class = Versions.v1
        model = models.Stop
        serializer = serializers.StopSerializer

        def get(self, request, code, format=FORMAT):
            """
            code:int - Query. If int, return particular stop having code, else return particular stops containing label.
            """

            # q = request.GET.get("q")
            # Now changed to path. Name is the same.
            # To be removed in v0.2

            q = code

            try:
                q = int(q)
            except ValueError:
                raise Response(status=400)

            try:
                obj = self.model.objects.get(code=q)
            except self.model.DoesNotExist:
                return Response(status=204)

            serializer = self.serializer(obj)
            return Response(serializer.data)

class RouteView:
    class v1(APIView):
        """
        Listing Routes/Buses

        PATH
        code:int - Getting ID or searching at terminal labels.
        """

        versioning_class = Versions.v1
        model = models.Route
        serializer = serializers.RouteSerializer

        def get(self, request, code, format=FORMAT):
            """
            code:int - Query. If int, return particular route having code, else return particular routes containing label.
            """

            # look@StopView.v1
            q = code
            q = int(q)

            try:
                obj = self.model.objects.get(code=q)
            except self.model.DoesNotExist:
                return Response(status=204)

            serializer = self.serializer(obj)
            return Response(serializer.data)

class RemainingView:
    class v1(APIView):
        """
        Remaining Stops at A Stop

        PATH
        code:int - Stop ID

        GET
        r:int = 0 - Route goes forward or comes back?
        """

        versioning_class=Versions.v1
        model = models.Stop
        serializer = serializers.RemainingSerializer.v1

        def get(self, request, code, format=FORMAT):
            """
            code:int - Code of stop.
            r:int - 0 or 1. Forwards or backwards.
            """

            # Initial Run
            try:
                code = int(code)
            except ValueError:
                return Response(status=400)

            towards = request.GET.get("r")

            if towards is None: towards = 0

            try:
                towards = int(towards)
            except ValueError:
                return Response(status=400)

            if towards > 1 or towards < 0:
                return Response(status=400)

            # Getting Stop and First Route
            stop = self.model.objects.get(code=code)

            try:
                if towards == 0:
                    route = models.Route.objects.filter(stops_forwards__contains=[stop.code])[0]
                else:
                    route = models.Route.objects.filter(stops_backwards__contains=[stop.code])[0]
            except IndexError:
                return Response(status=404)

            ram = redis.StrictRedis(decode_responses=True)

            if ram.exists(str(stop.code)+"_"+str(towards)):
                # If on Redis
                info_str = ram.get(str(stop.code)+"_"+str(towards))
                if info_str == "[]":
                    return Response(status=204)
                r_list = json.loads(info_str)
                serializer = self.serializer(data={
                    "code": stop.code,
                    "routes": r_list
                })

                if serializer.is_valid():
                    return Response(serializer.data)

            # If not on Redis
            res = requests.post(
                "http://www.eshot.gov.tr/tr/OtobusumNerede/290",
                data={
                    "hatId": str(route.code),
                    "durakId": str(stop.code),
                    "hatYon": str(towards)
                },
                headers={
                    "Connection": "keep-alive",
                    "Cache-Contol": "max-age=0",
                    "Origin": "http://www.eshot.gov.tr",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": choice(settings.USER_AGENTS),
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Referer": "http://www.eshot.gov.tr/tr/OtobusumNerede/290",
                    "Accept-Encoding": "gzip, deflate, lzma",
                    "Accept-Language": "en-US,en;q=0.8",
                    "Cookie": "AspxAutoDetectCookieSupport=1; ASP.NET_SessionId=ur114gdsk4mg2l3fy5lqvga5"
                }
            )

            if res.status_code != 200:
                return Response(status=res.status_code)

            if "Üzgünüz, bir hata oluştu." in res.text:
                return Response(status=204)

            soup = BeautifulSoup(res.content, "html.parser")

            rem_elms = soup.find_all("div", {"class": "where-is-bus-prop"})

            r_list = list()  # Adding Routes

            for elm in rem_elms:
                r_id = int(
                    re.findall("HAT: ([0-9]+)", elm.getText())[0] # i.e. HAT: 285 EVKA 1 - KONAK
                ) # Route ID
                rem = int(
                    re.findall("([0-9]+)", elm.find("strong").getText())[0] # i.e. 1 drk
                ) # Remaining
                r_list.append([r_id, rem])

            if len(r_list) == 0:
                ram.setex(str(stop.code) + "_" + str(towards), settings.POLITE_REQ_LIMIT, json.dumps(r_list))  # Expires in 90 Seconds
                return Response(status=204)

            serializer = self.serializer(data={
                "code": stop.code,
                "routes": r_list
            })

            if serializer.is_valid():
                ram.setex(str(stop.code)+"_"+str(towards), settings.POLITE_REQ_LIMIT, json.dumps(r_list)) # Expires in 90 Seconds
                return Response(serializer.data)

class StopSearchView:
    class v1(APIView):
        versioning_class = Versions.v1
        model = models.Stop
        serializer = serializers.StopSearchSerializer.v1

        def get(self, request, format=FORMAT):
            """
            Searching Stops

            GET
            q:str - Query String
            """

            q = request.GET.get("q")

            if q is None:
                return Response(status=400)

            stops = self.model.objects.filter(label__icontains=q)

            if len(stops) == 0:
                return Response(status=204)

            serializer = self.serializer(stops, many=True)

            return Response(serializer.data)

class RouteSearchView:
    class v1(APIView):
        versioning_class = Versions.v1
        model = models.Route
        serializer = serializers.RouteSearchSerializer.v1

        def get(self, request, format=FORMAT):
            """
            Searching Routes

            GET
            q:str - Query String
            """

            q = request.GET.get("q")

            if q is None:
                return Response(status=400)

            routes = self.model.objects.filter(terminals__icontains=q)

            if len(routes) == 0:
                return Response(status=204)

            serializer = self.serializer(routes, many=True)

            return Response(serializer.data)