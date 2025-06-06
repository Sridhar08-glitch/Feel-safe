from django.urls import path
from .views import RoomView
from .import views
from .views import get_notification, notifications_view,get_approved_crimes

urlpatterns = [
    path("<str:room_name>/<str:username>/", RoomView, name="room"),
    path('sos/',views.trigger_sos,name="trigger_sos"),
    path('notifications/', notifications_view, name='notifications'),
    path('get-notification/<int:notification_id>/', get_notification, name='get_notification'),
    path('report_crime/', views.report_crime, name='report_crime'),
    path('reportcrime/',views.viewreportcrime,name='reportcrime'),
    path('api/get_approved_crimes/', get_approved_crimes, name='approved_crimes'),
    path('danger/',views.show_danger,name='danger'),

    path('map/', views.map_view, name='police_station'),
    path('get_nearby_police_stations/', views.get_nearby_police_stations, name='get_nearby_police_stations'),
    path('safe-map/', views.safemap_view, name='safe_places'),
    path('get_nearby_safe_places/', views.get_nearby_safe_places, name='get_nearby_safe_places'),
]