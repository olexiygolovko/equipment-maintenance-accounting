from django.db import models
from django.contrib.auth.models import User


class CustomUser(User):
    class Meta:
        proxy = True

    def __str__(self):
        return self.first_name


class Technique_model(models.Model):
    name = models.TextField(unique=True, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Model of machines' 
        verbose_name_plural = 'Models of machines'


class Engine_model(models.Model):
    name = models.TextField(unique=True, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Engine model'
        verbose_name_plural = 'Engine models'


class Transmission_model(models.Model):
    name = models.TextField(unique=True, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Transmission model'
        verbose_name_plural = 'Transmission models'


class Drive_axle_model(models.Model):
    name = models.TextField(unique=True, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Drive axle model'
        verbose_name_plural = 'Drive axle models'


class Steerable_axle_model(models.Model):
    name = models.TextField(unique=True, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Steering axle model'
        verbose_name_plural = 'Steering axle models'


class Service_company(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='Username')
    name = models.TextField(unique=True, verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Service company'
        verbose_name_plural = 'Service companies'


class Car(models.Model):
    factory_number = models.TextField(max_length=17, unique=True, db_index=True, verbose_name='Factory number')
    technique_model = models.ForeignKey(Technique_model, on_delete=models.CASCADE, db_index=True, verbose_name='Vehicle model')
    engine_model = models.ForeignKey(Engine_model, on_delete=models.CASCADE, db_index=True, verbose_name='Engine model')
    engine_number = models.TextField(max_length=17, verbose_name='Engine number')
    transmission_model = models.ForeignKey(Transmission_model, on_delete=models.CASCADE, db_index=True, verbose_name='Transmission model')
    transmission_number = models.TextField(max_length=50, verbose_name='Transmission number')
    drive_axle_model = models.ForeignKey(Drive_axle_model, on_delete=models.CASCADE, db_index=True, verbose_name='Drive axle model')
    drive_axle_number = models.TextField(max_length=50, verbose_name='Drive axle number')
    steerable_axle_model = models.ForeignKey(Steerable_axle_model, on_delete=models.CASCADE, db_index=True, verbose_name='Steering axle model')
    steerable_axle_number = models.TextField(max_length=50, verbose_name='Steering axle number')
    supply_contract = models.TextField(max_length=50, blank=True, verbose_name='Delivery agreement No., date.')
    date_of_shipment_from_the_factory = models.DateField(db_index=True, verbose_name='Дата отгрузки с завода')
    consignee = models.TextField(max_length=50, blank=True, verbose_name='Consignee')
    delivery_address = models.TextField(max_length=300, blank=True, verbose_name='Delivery (operation) address')
    equipment = models.TextField(blank=True, verbose_name='Equipment (additional options)')
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Client')
    service_company = models.ForeignKey(Service_company, null=True, on_delete=models.CASCADE, blank=True, verbose_name='Service organization')

    def __str__(self):
        return f'{self.factory_number}'

    class Meta:
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'
        ordering = ['date_of_shipment_from_the_factory']


class Type_maintenance(models.Model):
    name = models.TextField(verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Type TO'
        verbose_name_plural = 'Types TO'


class Maintenance(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Car')
    service_company = models.ForeignKey(Service_company, on_delete=models.CASCADE, verbose_name='Service organization')
    type_maintenance = models.ForeignKey(Type_maintenance, on_delete=models.CASCADE, verbose_name='Type TO')
    maintenance_date = models.DateField(verbose_name='Maintenance date')
    operating_time = models.IntegerField(verbose_name='Earning moto/hours')
    order = models.TextField(max_length=50, verbose_name='Work order number')
    order_date = models.DateField(verbose_name='Work order date')

    def __str__(self):
        return f'{self.car, self.type_maintenance}'

    class Meta:
        verbose_name = 'ТО'
        verbose_name_plural = 'ТО'
        ordering = ['maintenance_date']



class Description_failure(models.Model):
    name = models.TextField(verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Nature of failure'
        verbose_name_plural = 'Nature of failures'


class Recovery_method(models.Model):
    name = models.TextField(verbose_name='Title')
    description = models.TextField(blank=True, verbose_name='Description')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Recovery method'
        verbose_name_plural = 'Recovery methods'


class Complaints(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Car')
    service_company = models.ForeignKey(Service_company, on_delete=models.CASCADE, verbose_name='Service organization')
    date_of_refusal = models.DateField(verbose_name='Date of refusal')
    operating_time = models.IntegerField(verbose_name='Operating hours m/hour')
    failure_node = models.TextField(verbose_name='Failure node')
    description_failure = models.ForeignKey(Description_failure, on_delete=models.CASCADE, verbose_name='Nature of failure')
    recovery_method = models.ForeignKey(Recovery_method, on_delete=models.CASCADE, verbose_name='Recovery method')
    parts_used = models.TextField(blank=True, verbose_name='Spare parts used')
    date_of_restoration = models.DateField(verbose_name='Restore date')
    equipment_downtime = models.TextField(verbose_name='Equipment downtime')

    def __str__(self):
        return f'{self.car, self.failure_node}'

    class Meta:
        verbose_name = 'Complaints'
        verbose_name_plural = 'Complaints'
        ordering = ['date_of_refusal']
