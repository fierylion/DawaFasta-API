from rest_framework import serializers

from .models import Medicine, Company, Medicine_Company, Patient, Purchase

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Company
        fields = '__all__'

    

class MedicineCompanySerializer(serializers.ModelSerializer):
    # Medicine = MedicineSerializer(many=True, source='medicine_id')
    class Meta:
        model = Medicine_Company
        fields = '__all__'
    def validate(self, attr):
        company_id = attr.get('company_id')
        medicine_id = attr.get('medicine_id')
        if(Medicine_Company.objects.filter(company_id=company_id, medicine_id = medicine_id).exists()):
            raise serializers.ValidationError(
                'The medicine in the company already exist'
            )
        return attr


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'
# class GetMedicinesSerializer(serializers.Serialize):
#     company = CompanySerializer()
#     medicines = serializers.SerializerMethodField()

#     def get_medicines(self, obj):
#         medicines = obj.medicines.all()
#         serialized_medicines = []
#         for medicine in medicines:
#             serializer = MedicineSerializer(medicine)
#             if serializer.is_valid():
#                 serialized_medicines.append(serializer.data)
#         return serialized_medicines

#     class Meta:
#         model = Medicine_Company
#         fields = ('company', 'medicines', 'field1', 'field2') # replace 'field1' and 'field2' with the actual field names