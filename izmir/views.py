from django.shortcuts import render

from rest_framework.versioning import URLPathVersioning
from rest_framework.views import APIView

from . import models
from . import serializers

class Versioning(URLPathVersioning):
    default_version = "1.0"
    allowed_versions = ["1.0"]


# Create your views here.
