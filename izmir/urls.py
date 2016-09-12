from django.conf.urls import url
from . import views

urlpatterns = []

# v: 1
urlpatterns += [
    # v1
    url(r"^v1/$", views.APIStatusView.v1.as_view()),
    url(r"^v1/stop/(?P<code>[0-9]+)/$", views.StopView.v1.as_view()),
    url(r"^v1/route/(?P<code>[0-9]+)/$", views.RouteView.v1.as_view()),
    url(r"^v1/remaining/(?P<code>[0-9]+)/$", views.RemainingView.v1.as_view()),
    url(r"^v1/search/stops/$", views.StopSearchView.v1.as_view()),
    url(r"^v1/search/routes/$", views.RouteSearchView.v1.as_view()),
    url(r"^v1/announcements/$", views.ListAnnouncementsView.v1.as_view()),
    url(r"^v1/announcements/(?P<pk>[0-9]+)/$", views.AnnouncementView.v1.as_view())
]