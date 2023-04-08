from django.db import models
from django.core.validators import RegexValidator
from datetime import datetime
import uuid
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
# Create your models here.

class Medicine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=30, blank=False, null=False, verbose_name='Medicine Name', error_messages={
        'blank': 'Medicine field is blank',
        'null': 'Medicine field cant be null'
    }
    )

    #Medicine content
    content = models.JSONField()
    expiryDate = models.DateField()
    manufactureDate = models.DateField()
    manufacturerName = models.CharField(max_length=30, blank=False, null=False, verbose_name='Manufacturer Name', error_messages={
        'blank': 'Manufacturer name field is blank',
        'null': 'Manufacturer name cant be null'
    })
    owners = models.IntegerField(default=1)
    isSolid = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        if self.expiryDate < self.manufactureDate:
            raise serializers.ValidationError(
                {'err': 'Expiry Date cannot be greater than Manufacture date'}
            )
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return 'Medicine Table'

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=30, blank=False, null=False, verbose_name='Company Name', error_messages={
        'blank': 'Medicine field is blank',
        'null': 'Medicine field cant be null'
    }, unique=True)
    #logo = models.ImageField(upload_to='companyProfile')
    password = models.CharField(max_length=100)
    description = models.TextField(default='')
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'Company: {self.name}'

class Medicine_Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    company_id= models.ForeignKey(Company, on_delete=models.CASCADE)
    medicine_id= models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()
    createdAt = models.DateTimeField(default=datetime.now())
    def __str__(self) -> str:
        return f'{self.company_id.name} - {self.medicine_id.name}'
class Patient(models.Model):
    id= models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=30, blank=False, null=False, verbose_name='Patient Name', error_messages={
        'blank': 'Name is blank',
        'null': 'Name cant be null'
    })
    birth_date = models.DateField()
    username = models.CharField(max_length=30,unique=True, verbose_name='Patient Username', error_messages={
        'blank': 'Username cant blank',
        'null': 'Username cant be null'
    })
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    #profile = models.ImageField(upload_to='patientProfile')
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)
    def __str__(self) -> str:
        return f'Patient : {self.name}'

class Purchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medicine_id = models.ForeignKey(
        Medicine, on_delete=models.CASCADE
    )
    company_id = models.ForeignKey(
        Company, on_delete=models.CASCADE
    )
    number = models.IntegerField(verbose_name='Number of Items Purchased')
    price_paid = models.FloatField()
    status = models.CharField(max_length= 10)
    purchase_time = models.DateTimeField(default=datetime.now())
    def __str__(self) -> str:
        return f'{self.medicine_id.name} - {self.company_id.name} - {self.patient_id.name} '






