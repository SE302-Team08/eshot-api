from django.conf.urls import url
from . import views

urlpatterns = []

# v: 1
urlpatterns += [
    # v1
    url(r"^v1/stop/$", views.StopView.v1.as_view()),
    url(r"^v1/route/$", views.RouteView.v1.as_view()),
    url(r"^v1/remaining/(?P<code>[0-9]+)/$", views.RemainingView.v1.as_view()),
]