from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormMixin, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import *
from .forms import *
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.core import serializers

class Index(FormMixin, ListView):
    model = Car
    template_name = 'index.html'
    context_object_name = 'cars'
    form_class = FactoryNumber
    success_url = 'index'

    def get_queryset(self):
        return []

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.get_form()
        if form.is_valid():
            # print(form.cleaned_data.get("factory_number"))
            self.object_list = Car.objects.filter(factory_number=form.cleaned_data['factory_number'])
            # self.object_list = [list(i.values()) for i in list(Car.objects.filter(factory_number=form.cleaned_data['factory_number']).values())]
        else:
            self.object_list = []

        return self.render_to_response(self.get_context_data(object_list=self.object_list, form=form))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #Для вывода информации из справочников по клику на значение
        context['technique_model'] = Technique_model.objects.all()
        context['engine_model'] = Engine_model.objects.all()
        context['transmission_model'] = Transmission_model.objects.all()
        context['drive_axle_model'] = Drive_axle_model.objects.all()
        context['steerable_axle_model'] = Steerable_axle_model.objects.all()
        return context


class Info(PermissionRequiredMixin, ListView):
    permission_required = 'services.view_car'
    model = Car
    template_name = 'info.html'
    context_object_name = 'cars'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        order_by = self.request.GET.get('order_by', 'date_of_shipment_from_the_factory')
        if order_by in ['technique_model', 'engine_model', 'transmission_model', 'drive_axle_model',
                        'steerable_axle_model', 'service_company']:
            order_by = order_by+"__name"
        if order_by in ['client']:
            order_by = "client__username"

        context['te'] = self.request.GET.get('te', '---')
        context['en'] = self.request.GET.get('en', '---')
        context['tr'] = self.request.GET.get('tr', '---')
        context['da'] = self.request.GET.get('da', '---')
        context['sa'] = self.request.GET.get('sa', '---')

        qs = qs_filter = Car.objects.all()
        if context['te'] != "---":
            filter = Technique_model.objects.get(name=context['te']).id
            qs = qs.filter(technique_model=filter)
        if context['en'] != "---":
            filter = Engine_model.objects.get(name=context['en'])
            qs = qs.filter(engine_model=filter)
        if context['tr'] != "---":
            filter = Transmission_model.objects.get(name=context['tr']).id
            qs = qs.filter(transmission_model=filter)
        if context['da'] != "---":
            filter = Drive_axle_model.objects.get(name=context['da']).id
            qs = qs.filter(drive_axle_model=filter)
        if context['sa'] != "---":
            filter = Steerable_axle_model.objects.get(name=context['sa']).id
            qs = qs.filter(steerable_axle_model=filter)
        filter_list = ['technique_model', 'engine_model', 'transmission_model', 'drive_axle_model', 'steerable_axle_model']
        if self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
            context['cars'] = qs.order_by(order_by)
            for filter in filter_list:
                context[filter] = set(qs_filter.values_list(filter+'__name', flat=True))
        elif self.request.user.groups.filter(name='service').exists():
            context['cars'] = qs.filter(service_company__user=self.request.user.id).order_by(order_by)
            for filter in filter_list:
                context[filter] = set(qs_filter.filter(service_company__user=self.request.user.id).values_list(filter+'__name', flat=True))
        elif self.request.user.groups.filter(name='client').exists():
            context['cars'] = qs.filter(client=self.request.user.id).order_by(order_by)
            for filter in filter_list:
                context[filter] = set(qs_filter.filter(client=self.request.user.id).values_list(filter+'__name', flat=True))
        else:
            context['cars'] = []
        return context


class InfoItem(PermissionRequiredMixin, DetailView):
    permission_required = 'services.view_car'
    model = Car
    template_name = 'car_item.html'
    context_object_name = 'car'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #Для вывода информации из справочников по клику на значение
        context['technique_model'] = Technique_model.objects.all()
        context['engine_model'] = Engine_model.objects.all()
        context['transmission_model'] = Transmission_model.objects.all()
        context['drive_axle_model'] = Drive_axle_model.objects.all()
        context['steerable_axle_model'] = Steerable_axle_model.objects.all()
        context['service_company'] = Service_company.objects.all()
        return context


class CreateCar(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_car'
    model = Car
    template_name = 'create_car.html'
    form_class = CreateCarForm
    success_url = '/info'


class EditCar(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_car'
    model = Car
    template_name = 'update.html'
    form_class = CreateCarForm
    success_url = '/info'


class DeleteCar(PermissionRequiredMixin, DeleteView):
    permission_required = 'services.delete_car'
    model = Car
    template_name = 'delete.html'
    success_url = '/info'


class MaintenanceList(PermissionRequiredMixin, ListView):
    permission_required = 'services.view_maintenance'
    model = Maintenance
    template_name = 'maintenance.html'
    context_object_name = 'maintenances'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # Очищаем переменные session при получении параметра "clear"
        if self.request.GET.get('clear'):
            self.request.session.pop('order_by2', None)
            self.request.session.pop('tm', None) #вид ТО
            self.request.session.pop('cr', None) #зав.номер машины
            self.request.session.pop('sc', None) #сервисная компания для таблицы «ТО»

        # Перезаписываем order_by2 в session при получении url параметра "order_by" или maintenance_date
        if self.request.GET.get('order_by'): self.request.session['order_by2'] = self.request.GET.get('order_by')
        if not 'order_by2' in self.request.session: self.request.session['order_by2'] = 'maintenance_date'
        # Добавляем "__name" к переменной order_by для связанных объектов
        order_by = self.request.session['order_by2']
        if order_by in ['type_maintenance', 'car', 'service_company']: order_by = order_by+"__name"

        # Перезаписываем в session переменные для фильтрации при получении их параметра через url
        # Отправляем значение фильтра в шаблон для отображения в SELECT
        if self.request.GET.get('tm'): self.request.session['tm'] = self.request.GET.get('tm')
        context['tm'] = self.request.session['tm'] if "tm" in self.request.session else '---'
        if self.request.GET.get('cr'): self.request.session['cr'] = self.request.GET.get('cr')
        context['cr'] = self.request.session['cr'] if "cr" in self.request.session else '---'
        if self.request.GET.get('sc'): self.request.session['sc'] = self.request.GET.get('sc')
        context['sc'] = self.request.session['sc'] if "sc" in self.request.session else '---'

        # Готовим наборы объектов перед фильтрацией и для списка значений фильтра
        qs = qs_filter = Maintenance.objects.all()
        # фильтрация объектов
        if "tm" in self.request.session:
            filter = Type_maintenance.objects.get(name=self.request.session['tm']).id
            qs = qs.filter(type_maintenance=filter)
        if "cr" in self.request.session:
            filter = Car.objects.get(factory_number=self.request.session['cr'])
            qs = qs.filter(car=filter)
        if "sc" in self.request.session:
            filter = Service_company.objects.get(name=self.request.session['sc']).id
            qs = qs.filter(service_company=filter)

        if self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
            # Формируем список значений для select фильтров из доступного для клиента диапазона записей
            context['type_maintenance'] = set(qs_filter.values_list('type_maintenance__name', flat=True))
            context['car'] = set(qs_filter.values_list('car__factory_number', flat=True))
            context['service_company'] = set(qs_filter.values_list('service_company__name', flat=True))
            context['maintenances'] = qs.order_by(order_by)
        elif self.request.user.groups.filter(name='service').exists():
            context['type_maintenance'] = set(qs_filter.filter(service_company__user=self.request.user).values_list('type_maintenance__name', flat=True))
            context['car'] = set(qs_filter.filter(service_company__user=self.request.user).values_list('car__factory_number', flat=True))
            context['service_company'] = set(qs_filter.filter(service_company__user=self.request.user).values_list('service_company__name', flat=True))
            context['maintenances'] = qs.filter(service_company__user=self.request.user).order_by(order_by)
        elif self.request.user.groups.filter(name='client').exists():
            context['type_maintenance'] = set(qs_filter.filter(car__client=self.request.user).values_list('type_maintenance__name', flat=True))
            context['car'] = set(qs_filter.filter(car__client=self.request.user).values_list('car__factory_number', flat=True))
            context['service_company'] = set(qs_filter.filter(car__client=self.request.user).values_list('service_company__name', flat=True))
            context['maintenances'] = qs.filter(car__client=self.request.user).order_by(order_by)
        else:
            context['maintenances'] = []
        return context


class CreateMaintenances(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_maintenance'
    model = Maintenance
    template_name = 'create_maintenance.html'
    form_class = CreateMaintenancesForm
    success_url = '/maintenance'
    context_object_name = 'cars'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        id = self.request.GET.get('id', '')
        if id == '':
            context['select_car'] = "---------"
        else:
            context['select_car'] = Car.objects.get(id=id)

        if self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
            context['cars'] = Car.objects.all()
        else:
            print('self.request.user = ', self.request.user)
            if self.request.user.groups.filter(name='client').exists():
                context['cars'] = Car.objects.filter(client=self.request.user)
            else:
                context['cars'] = Car.objects.filter(service_company__user=self.request.user)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        id = self.request.GET.get('id', '')
        if id == '':
            kwargs['initial'] = {'service_company': ""}
        else:
            service_company = Car.objects.get(id=id).service_company_id
            kwargs['initial'] = {'service_company': service_company, 'car': id}
        return kwargs


class MaintenanceItem(PermissionRequiredMixin, DetailView):
    permission_required = 'services.view_maintenance'
    model = Maintenance
    template_name = 'maintenance_item.html'
    context_object_name = 'maintenance'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #Для вывода информации из справочников по клику на значение
        context['type_maintenance'] = Type_maintenance.objects.all()
        context['service_company'] = Service_company.objects.all()
        return context


class MaintenanceEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_maintenance'
    model = Maintenance
    template_name = 'update.html'
    form_class = UpdateMaintenancesForm
    success_url = '/maintenance'


class MaintenanceDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'services.delete_maintenance'
    model = Maintenance
    template_name = 'delete.html'
    success_url = '/maintenance'


class ComplaintsList(PermissionRequiredMixin, ListView):
    permission_required = 'services.view_complaints'
    model = Complaints
    template_name = 'complaints.html'
    context_object_name = 'complaints'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        # Очищаем переменные session при получении параметра "clear"
        if self.request.GET.get('clear'):
            self.request.session.pop('order_by3', None)
            self.request.session.pop('fn', None) #Узел отказа
            self.request.session.pop('rm', None) #Способ восстановления
            self.request.session.pop('sc3', None) #сервисная компания

        # Перезаписываем order_by3 в session при получении url параметра "order_by" или date_of_refusal
        if self.request.GET.get('order_by'): self.request.session['order_by3'] = self.request.GET.get('order_by')
        if not 'order_by3' in self.request.session: self.request.session['order_by3'] = 'date_of_refusal'
        # Добавляем "__name" к переменной order_by для связанных объектов
        order_by = self.request.session['order_by3']
        if order_by in ['recovery_method', 'service_company']: order_by = order_by + "__name"

        # Перезаписываем в session переменные для фильтрации при получении их параметра через url
        # Отправляем значение фильтра в шаблон для отображения в SELECT
        if self.request.GET.get('fn'): self.request.session['fn'] = self.request.GET.get('fn')
        context['fn'] = self.request.session['fn'] if "fn" in self.request.session else '---'
        if self.request.GET.get('rm'): self.request.session['rm'] = self.request.GET.get('rm')
        context['rm'] = self.request.session['rm'] if "rm" in self.request.session else '---'
        if self.request.GET.get('sc'): self.request.session['sc3'] = self.request.GET.get('sc')
        context['sc'] = self.request.session['sc3'] if "sc3" in self.request.session else '---'

        # Готовим наборы объектов перед фильтрацией и для списка значений фильтра
        qs = qs_filter = Complaints.objects.all()
        # фильтрация объектов
        if "fn" in self.request.session:
            qs = qs.filter(failure_node=self.request.session['fn'])
        if "rm" in self.request.session:
            filter = Recovery_method.objects.get(name=self.request.session['rm'])
            qs = qs.filter(recovery_method=filter)
        if "sc3" in self.request.session:
            filter = Service_company.objects.get(name=self.request.session['sc3']).id
            qs = qs.filter(service_company=filter)

        if self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
            # Формируем список значений для select фильтров из доступного для клиента диапазона записей
            context['failure_node'] = set(qs_filter.values_list('failure_node', flat=True))
            context['recovery_method'] = set(qs_filter.values_list('recovery_method__name', flat=True))
            context['service_company'] = set(qs_filter.values_list('service_company__name', flat=True))
            context['complaints'] = qs.order_by(order_by)
        elif self.request.user.groups.filter(name='service').exists():
            context['failure_node'] = set(qs_filter.filter(service_company__user=self.request.user).values_list('failure_node', flat=True))
            context['recovery_method'] = set(qs_filter.filter(service_company__user=self.request.user).values_list('recovery_method__name', flat=True))
            context['service_company'] = set(qs_filter.filter(service_company__user=self.request.user).values_list('service_company__name', flat=True))
            context['complaints'] = qs.filter(service_company__user=self.request.user).order_by(order_by)
        elif self.request.user.groups.filter(name='client').exists():
            context['failure_node'] = set(qs_filter.filter(car__client=self.request.user).values_list('failure_node', flat=True))
            context['recovery_method'] = set(qs_filter.filter(car__client=self.request.user).values_list('recovery_method__name', flat=True))
            context['service_company'] = set(qs_filter.filter(car__client=self.request.user).values_list('service_company__name', flat=True))
            context['complaints'] = qs.filter(car__client=self.request.user.id).order_by(order_by)
        else:
            context['complaints'] = []
        return context


class CreateComplaints(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_complaints'
    model = Complaints
    template_name = 'create_complaints.html'
    form_class = CreateComplaintsForm
    success_url = '/complaints'
    context_object_name = 'cars'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        id = self.request.GET.get('id', '')
        if id == '':
            context['select_car'] = "---------"
        else:
            context['select_car'] = Car.objects.get(id=id)

        if self.request.user.groups.filter(name='admin').exists() or self.request.user.groups.filter(name='manager').exists():
            context['cars'] = Car.objects.all()
        else:
            context['cars'] = Car.objects.filter(service_company__user=self.request.user)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        id = self.request.GET.get('id', '')
        if id == '':
            kwargs['initial'] = {'service_company': ""}
        else:
            service_company = Car.objects.get(id=id).service_company_id
            kwargs['initial'] = {'service_company': service_company, 'car': id}
        return kwargs


class ComplaintsItem(PermissionRequiredMixin, DetailView):
    permission_required = 'services.view_complaints'
    model = Complaints
    template_name = 'complaints_item.html'
    context_object_name = 'complaints'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #Для вывода информации из справочников по клику на значение
        context['description_failure'] = Description_failure.objects.all()
        context['recovery_method'] = Recovery_method.objects.all()
        context['service_company'] = Service_company.objects.all()
        return context

class ComplaintsEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_complaints'
    model = Complaints
    template_name = 'update.html'
    form_class = UpdateComplaintsForm
    success_url = '/complaints'


class ComplaintsDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'services.delete_complaints'
    model = Complaints
    template_name = 'delete.html'
    success_url = '/complaints'


def reference_book(request):
    return render(request, 'reference_book.html')


class ReferenceBookList(PermissionRequiredMixin, TemplateView):
    permission_required = ('services.view_technique_model', 'services.view_engine_model', 'services.view_transmission_model',
                           'services.view_drive_axle_model', 'services.view_steerable_axle_model',
                           'services.view_service_company', 'services.view_type_maintenance',
                           'services.view_description_failure', 'services.view_recovery_method')
    template_name = 'reference_book_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        if pk == 1:
            context['name'] = "Модель техники"
            context['list'] = Technique_model.objects.all()
        elif pk == 2:
            context['name'] = "Модель двигателя"
            context['list'] = Engine_model.objects.all()
        elif pk == 3:
            context['name'] = "Модель трансмиссии"
            context['list'] = Transmission_model.objects.all()
        elif pk == 4:
            context['name'] = "Модель ведущего моста"
            context['list'] = Drive_axle_model.objects.all()
        elif pk == 5:
            context['name'] = "Модель управляемого моста"
            context['list'] = Steerable_axle_model.objects.all()
        elif pk == 6:
            context['name'] = "Сервисная организация"
            context['list'] = Service_company.objects.all()
        elif pk == 7:
            context['name'] = "Вид ТО"
            context['list'] = Type_maintenance.objects.all()
        elif pk == 8:
            context['name'] = "Характер отказа"
            context['list'] = Description_failure.objects.all()
        elif pk == 9:
            context['name'] = "Способ восстановления"
            context['list'] = Recovery_method.objects.all()
        return context


class TechniqueModeCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_technique_model'
    model = Technique_model
    template_name = 'update.html'
    form_class = UpdateTechniqueModelForm
    success_url = '../'


class TechniqueModelEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_technique_model'
    model = Technique_model
    template_name = 'update.html'
    form_class = UpdateTechniqueModelForm
    success_url = '../../'


class EngineModelCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_engine_model'
    model = Engine_model
    template_name = 'update.html'
    form_class = UpdateEngineModelForm
    success_url = '../'


class EngineModelEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_engine_model'
    model = Engine_model
    template_name = 'update.html'
    form_class = UpdateEngineModelForm
    success_url = '../../'


class TransmissionModelCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_transmission_model'
    model = Transmission_model
    template_name = 'update.html'
    form_class = UpdateTransmissionModelForm
    success_url = '../'


class TransmissionModelEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_transmission_model'
    model = Transmission_model
    template_name = 'update.html'
    form_class = UpdateTransmissionModelForm
    success_url = '../../'


class DriveAxleModelCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_drive_axle_model'
    model = Drive_axle_model
    template_name = 'update.html'
    form_class = UpdateDriveAxleModelForm
    success_url = '../'


class DriveAxleModelEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_drive_axle_model'
    model = Drive_axle_model
    template_name = 'update.html'
    form_class = UpdateDriveAxleModelForm
    success_url = '../../'


class SteerableAxleModelCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_steerable_axle_model'
    model = Steerable_axle_model
    template_name = 'update.html'
    form_class = UpdateSteerableAxleModelForm
    success_url = '../'


class SteerableAxleModelEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_steerable_axle_model'
    model = Steerable_axle_model
    template_name = 'update.html'
    form_class = UpdateSteerableAxleModelForm
    success_url = '../../'


class ServiceCompanyCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_service_company'
    model = Service_company
    template_name = 'update.html'
    form_class = CreateServiceCompanyForm
    success_url = '../'


class ServiceCompanyEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_service_company'
    model = Service_company
    template_name = 'update.html'
    form_class = UpdateServiceCompanyForm
    success_url = '../../'

    def form_valid(self, form):
        form.save()
        # Перезаписываем имя сервисной компании в Аккаунте
        name = form.cleaned_data.get("name")
        first_name = form.cleaned_data.get("user")
        id = User.objects.get(first_name=first_name).id
        user = User.objects.get(id=id)
        user.first_name = name
        user.save()
        return super().form_valid(form)


class TypeMaintenanceCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_type_maintenance'
    model = Type_maintenance
    template_name = 'update.html'
    form_class = UpdateTypeMaintenanceForm
    success_url = '../'


class TypeMaintenanceEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_type_maintenance'
    model = Type_maintenance
    template_name = 'update.html'
    form_class = UpdateTypeMaintenanceForm
    success_url = '../../'


class DescriptionFailureCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_description_failure'
    model = Description_failure
    template_name = 'update.html'
    form_class = UpdateDescriptionFailureForm
    success_url = '../'


class DescriptionFailureEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_description_failure'
    model = Description_failure
    template_name = 'update.html'
    form_class = UpdateDescriptionFailureForm
    success_url = '../../'


class RecoveryMethodCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'services.add_recovery_method'
    model = Recovery_method
    template_name = 'update.html'
    form_class = UpdateRecoveryMethodForm
    success_url = '../'


class RecoveryMethodEdit(PermissionRequiredMixin, UpdateView):
    permission_required = 'services.change_recovery_method'
    model = Recovery_method
    template_name = 'update.html'
    form_class = UpdateRecoveryMethodForm
    success_url = '../../'

