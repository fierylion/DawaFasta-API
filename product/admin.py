from django.contrib import admin
from .models import Medicine, Patient, Purchase, Medicine_Company, Company
# Register your models here.
admin.site.register(Medicine)
admin.site.register(Company)
admin.site.register(Patient)
admin.site.register(Purchase)
admin.site.register(Medicine_Company)