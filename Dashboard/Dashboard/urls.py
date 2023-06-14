from django.contrib import admin
from django.urls import path,include
from .views import login,signout,signup


urlpatterns = [
    path("admin/", admin.site.urls),
    path('Playlog/',include('Playlog.urls')),
    path('', login, name='login'),
    path('logout/',signout,name='signout'),
    path('signup/',signup,name='signup'),

]
