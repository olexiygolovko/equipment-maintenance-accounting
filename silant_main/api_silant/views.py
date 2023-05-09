from rest_framework import generics
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView
from services.models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse
from .serializers import CarSerializer, MaintenanceSerializer, ComplaintSerializer


@method_decorator(login_required, name='dispatch')
class CarList(generics.ListCreateAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


@method_decorator(login_required, name='dispatch')
class CarDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Car.objects.all()
    serializer_class = CarSerializer


@method_decorator(login_required, name='dispatch')
class MaintenanceList(generics.ListCreateAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer


@method_decorator(login_required, name='dispatch')
class MaintenanceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer


@method_decorator(login_required, name='dispatch')
class ComplaintList(generics.ListCreateAPIView):
    queryset = Complaints.objects.all()
    serializer_class = ComplaintSerializer


@method_decorator(login_required, name='dispatch')
class ComplaintDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Complaints.objects.all()
    serializer_class = ComplaintSerializer


@method_decorator(login_required, name='dispatch')
class APIList(ListView):
    template_name = 'api_list.html'
    queryset = [
        {
            'name': 'API - Машина',
            'url': reverse_lazy('car-list')
        },
        {
            'name': 'API - ТО',
            'url': reverse_lazy('maintenance-list')
        },
        {
            'name': 'API - Рекламации',
            'url': reverse_lazy('complaint-list')
        },
    ]

