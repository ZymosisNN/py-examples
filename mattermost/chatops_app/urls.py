from . import views
from django.conf.urls import url

urlpatterns = [
    url('commands_imt_us/$', views.SlackView.as_view()),
    url('commands_imt_eu/$', views.SlackView.as_view()),
    url('commands_lm/$', views.SlackView.as_view()),
    url('commands_mgr/$', views.SlackView.as_view()),
    url('commands/modals/$', views.SlackView.as_view()),
    url('status/$', views.status),
]

