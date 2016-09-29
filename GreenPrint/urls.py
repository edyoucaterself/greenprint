from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
#from django.contrib.auth.forms import UserCreationForm
#from payplanner.forms import UserCreateForm as UserCreationForm
from payplanner.views import signup
urlpatterns = [
    url('^register/', signup, name="reg"),
    url('^password_reset/', include('password_reset.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^payplanner/', include('payplanner.urls')),
    url(r'', include('payplanner.urls')),
    url(r'^admin/', include(admin.site.urls)),
]


