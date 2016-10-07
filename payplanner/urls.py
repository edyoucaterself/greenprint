#urls.py
# Created On: 9/5/2016
# Created By: Matt Agresta
#-----------------------------------------------------------#
#Set up Environment
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^config$', views.config, name='config'),
    url(r'^config/(?P<item_id>[0-9]+)/$',views.edit, name='edit'),
    url(r'settings$', views.account_mgmt, name='manage'),
    url(r'settings/(?P<page>[\w-]+)$', views.categories, name='set')
]
