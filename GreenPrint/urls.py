from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from password_reset import views as pwviews
from payplanner.views import signup, billender

urlpatterns = [
    url('^register/', signup, name="reg"),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^payplanner/', include('payplanner.urls')),
    url(r'^billender/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', billender, name='billender'),
    url(r'', include('payplanner.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^recover/(?P<signature>.+)/$', pwviews.recover_done, name='password_reset_sent'),
    url(r'^recover/$', pwviews.recover, name='password_reset_recover'),
    url(r'^reset/done/$', auth_views.login, name='password_reset_done'),
    url(r'^reset/(?P<token>[\w:-]+)/$', pwviews.reset, name='password_reset_reset'),
]


