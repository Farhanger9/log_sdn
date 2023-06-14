from django.contrib import admin
from django.urls import path
from .views import import_csv,PlaylogList,search,date_range_view,get_data,get_all

urlpatterns = [
    path('import_csv', import_csv, name='import_csv'),
    path('PlaylogList', PlaylogList, name='PlaylogList'),
    path('search', search ,name='search'),
    path('date-range/', date_range_view, name='date_range_view'),
path('get_data', get_data, name='get_data'),
path('get_all', get_all, name='get_all'),

]
