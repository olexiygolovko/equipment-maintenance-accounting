from django.urls import path
from .views import CarList, CarDetail, MaintenanceList, MaintenanceDetail, ComplaintList, ComplaintDetail, APIList


urlpatterns = [
    path('cars/', CarList.as_view(), name='car-list'),
    path('cars/<int:pk>/', CarDetail.as_view(), name='car-detail'),
    path('maintenance/', MaintenanceList.as_view(), name='maintenance-list'),
    path('maintenance/<int:pk>/', MaintenanceDetail.as_view(), name='maintenance-detail'),
    path('complaints/', ComplaintList.as_view(), name='complaint-list'),
    path('complaints/<int:pk>/', ComplaintDetail.as_view(), name='complaint-detail'),
    path('', APIList.as_view(), name='api-list'),
]
