from django.views.generic import ListView, DetailView

__author__ = 'tejas'


from django.conf.urls import patterns, url

from rtr import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'login/$', views.login, name='login'),
    url(r'profsettings/$', views.prof_settings, name='prof_settings'),
    url(r'profsettings/start/$', views.prof_start_display, name='prof_start_display'),
    url(r'profDisplay/$', views.prof_display, name='prof_display'),
    url(r'profDisplay/statisticsGet/$', views.get_stats, name='get_stats'),
    url(r'profDisplay/questions/$', views.get_stats, name='get_questions'),
    url(r'audience_view/$', views.audience_display, name='audience_display'),
    url(r'audience_view/audienceResponse$', views.updateStats, name='audience_response'),
    url(r'audience_view/audienceQuestion$', views.ask_question, name='audience_question'),
    url(r'endsession/$', views.end_session, name='end_session'),
)

