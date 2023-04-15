from django.shortcuts import HttpResponse
import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth.hashers import check_password
from django.forms import model_to_dict
from .models import Medicine, Company, Medicine_Company, Patient, Purchase
from rest_framework import serializers
from .errors import validation_error_decorator
from copy import copy
import uuid
import json
import yaml
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.conf import settings
from .errors import customJSONEncoder
#serializers
from .serializers import (
    MedicineSerializer, 
    CompanySerializer, 
    MedicineCompanySerializer, 
    PatientSerializer, 
    PurchaseSerializer,
)


def Home(request):
    # raise serializers.ValidationError
    return HttpResponse('<h1>Hello How are you</h1> <br/> <hr/> <b><h1><a target="_blank" href="/api/docs" styles="color:blue;">Read DawaFasta API docs</a></h1></b><br/> <hr/> <b><h1><a target="_blank" href="https://job-api-01.onrender.com/api/docs2" styles="color:blue;">If the above url fails use this one</a></h1></b> <br/> <hr/> <b><h1><a target="_blank" href="https://github.com/fierylion/DawaFasta-API" styles="color:pink;">View the Github Repo, Dont forget to give it a star</a></h1></b>')


#external functions used in someplaces on views
def is_uuid(s, id=''):
    try:
        uuid.UUID(s)
        return s
    except:
        raise serializers.ValidationError(
            {'id': id, 'det': s}
        )
def remove_password(dict, attr):
    dict = copy(dict)
    del dict[attr]
    return dict

#user Authorization
@api_view(['POST', 'GET'])
@validation_error_decorator
def user_register(request):
    if request.method=='POST':
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save()
            # Create token
            token = jwt.encode({"user": True,'user_id': str(patient.id), 'user_name': patient.name }, settings.JWT_SECRET, algorithm='HS256')
            data = copy(serializer.data)
            data.pop('password')
            return Response({'data': data, 'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method=='GET':
        return Response({'mes': 'Register Patient'}, status = status.HTTP_200_OK)

#user login
@api_view(['POST', 'GET'])
@validation_error_decorator
def user_login(request):
    if request.method =='POST':
        user_name = request.data.get('username')
        password =request.data.get('password')
        if user_name and password:
            try:
                patient = Patient.objects.get(username = user_name)   
                #check for password
                if(not check_password(password, patient.password)):
                    raise Exception
            except Patient.DoesNotExist:
                return Response({'err': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Create token
            token = jwt.encode({"user": True,'user_id': str(patient.id), 'user_name': patient.username}, settings.JWT_SECRET, algorithm='HS256')
            
            serialized_patient = dict(PatientSerializer(patient).data)
            
            serialized_patient.pop('password')  # remove password on the response

            return Response({'data': serialized_patient, 'token': token}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 'Missing credentials'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method=='GET':
        return Response({'mes': 'Login User'}, status = status.HTTP_200_OK)

#single user
@api_view(['GET'])
@validation_error_decorator
def single_user(request, userID):
    amount = request.GET.get('amount', None) #for pagination purpose
    search = request.GET.get('search', None) # for search purpose
    results = []
    # only ten result are maximum unless specified
    userID = request.userID
    try:
        user = Patient.objects.get(id=userID)
    except Patient.DoesNotExist:
        return Response({'err': 'User not found'}, status=401)
    if search:
         results = Medicine_Company.objects.filter(medicine_id__name__icontains = search, quantity__gte=1)[slice(0, 10)]
    if amount:
        medicines = Medicine_Company.objects.filter(quantity__gte=1)[slice(0,int(amount))] if(not search) else results
        data = {'Medicines': [ {"company": remove_password(model_to_dict(mc.company_id), "password"),"quantity":mc.quantity, "price":mc.price, "medicine":model_to_dict(mc.medicine_id)} for mc in medicines], 'User':{
            'username': user.username,
            'name': user.name,
            'birthdate': user.birth_date
        } }
        return Response(data, status= status.HTTP_200_OK)
    elif(not amount):
        medicines = Medicine_Company.objects.filter(quantity__gte=1)[slice(0, 10)] if(not search) else results
        data = {'Medicines': [ {"company": remove_password(model_to_dict(mc.company_id), "password"),"quantity":mc.quantity, "price":mc.price, "medicine":model_to_dict(mc.medicine_id)} for mc in medicines], 'User':{
            'username': user.username,
            'name': user.name,
            'birthdate': user.birth_date
        }}
        return Response(data, status= status.HTTP_200_OK)
#user purchase
@api_view(['GET'])
@validation_error_decorator
def user_purchase(request, userID):
    if(request.method == 'GET'):
        med_id = request.GET.get('medicine')
        comp_id = request.GET.get('company')
        amount = request.GET.get('amount') #specify items to purchased
        number = 1 # default amount to purchase is 1 item
        if amount:
            number = int(amount)
        if med_id and comp_id:
            medicine = Medicine_Company.objects.filter(company_id_id=is_uuid(comp_id, 'Company ID'), medicine_id_id = is_uuid(med_id, 'Medicine ID'))[0]
            if(not medicine):
                raise serializers.ValidationError(
                    'Medicine doesnt exists for the named company'
                )
            serializer = PurchaseSerializer(data = {
                "medicine_id": medicine.medicine_id.id,
                "company_id": medicine.company_id.id,
                "patient_id": userID,
                "number": number,
                "price_paid": medicine.price,
                "status": "pending"
            })
            if serializer.is_valid():
                purchase = serializer.save()
                med = Medicine_Company.objects.get(medicine_id = purchase.medicine_id, company_id = purchase.company_id)
                if(med.quantity<number):
                    return Response({'err': 'Insufficient Quantity'})
                med.quantity-=number
                med.save()
                return Response(
                    {
                    'company': purchase.company_id.name,
                    'medicine': purchase.medicine_id.name,
                    'client': purchase.patient_id.name,
                    'amount': purchase.number, 
                    'status': purchase.status
                    },
                    status= status.HTTP_200_OK
                )
            
            else:
                return Response({"err": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise serializers.ValidationError(
                    'Please provide, Either the company or medicine ids'
                )
@api_view(['GET'])
@validation_error_decorator
def user_purchase_history(request, userID):
    purchases = Purchase.objects.filter(patient_id = is_uuid(userID, 'User ID'))
    return Response(
        {'data': [
        {
        "id": purchase.id,
            "company": purchase.company_id.name,
            "customer_name": purchase.patient_id.name,
            "amount": purchase.number,
            "time": purchase.purchase_time, 
            "status": purchase.status
        } for purchase in purchases
        ]}, 
        status = status.HTTP_200_OK
    )


@api_view(['GET'])
@validation_error_decorator
def company_sales(request, compID, medID):
    # modify sales
    is_uuid(compID, 'Company ID')
    is_uuid(medID, 'Medicine ID')
    sale = request.GET.get('sale')
    sale_id= ''
    if sale:
        sale_id = is_uuid(sale, "Sale ID")
    stat = request.GET.get('status')
    if(sale_id and stat):
        if len(stat)>=10:
            return Response({'err': 'long status'})
        try:
            sale = Purchase.objects.get(id=sale_id, company_id = compID, medicine_id = medID)
            sale.status = stat
            sale.save()
            return Response({'msg': 'success'})
        except Purchase.DoesNotExist:
            return Response({'err': f'The sale with the id {sale_id} does not exist'})
    else:
        sales = Purchase.objects.filter(company_id=compID, medicine_id=medID)
        data = [{
            "id": purchase.id,
            "company": purchase.company_id.name,
            "customer_name": purchase.patient_id.name,
            "amount": purchase.number,
            "time": purchase.purchase_time,
            "status": purchase.status
        } for purchase in sales]
        return Response({'data': data}, status=status.HTTP_200_OK)



#Company Authorization
@api_view(['POST', 'GET'])
@validation_error_decorator
def company_register(request):
    if request.method=='POST':
        
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            
            # Create token
            token = jwt.encode({"user": False,'company_id': str(company.id), 'company_name': company.name }, settings.JWT_SECRET, algorithm='HS256')
            data = copy(serializer.data)
            data.pop('password')
            # Return response
            return Response({'data': data, 'token': token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method=='GET':
        return Response({'mes': 'Register Company'}, status = status.HTTP_200_OK)
    

@api_view(['POST', 'GET'])
@validation_error_decorator
def company_login(request):
    if request.method =='POST':
        name = request.data.get('name')
        password =request.data.get('password')
        if name and password:
            try:
                company = Company.objects.get(name=name)   
                if(not check_password(password, company.password)):
                    raise Company.DoesNotExist
            except Company.DoesNotExist:
                return Response({'err': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Create token
            token = jwt.encode({"user": False,'company_id': str(company.id), 'company_name': company.name}, settings.JWT_SECRET, algorithm='HS256')
            
            serialized_company = dict(CompanySerializer(company).data)
            
            serialized_company.pop('password')

            return Response({'data': serialized_company, 'token': token}, status=status.HTTP_200_OK)
        else:
            return Response({'err': 'Missing credentials'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method=='GET':
        return Response({'mes': 'Login Company'}, status = status.HTTP_200_OK)


#Company Queries For Registered companies
@api_view(['GET', 'POST'])
@validation_error_decorator
def single_company(request, compID):
    is_uuid(compID, 'Company ID')
    if(request.method=='GET'):
        search = request.GET.get('search', None)
        if search:
            medicines = Medicine_Company.objects.filter(medicine_id__name__icontains = search, company_id_id=compID)
            data = {'Company':remove_password(model_to_dict(Company.objects.get(id=compID)), 'password') , 'Medicines': [ model_to_dict(mc.medicine_id) for mc in medicines]}
            return Response(data, status= status.HTTP_200_OK)
        else:
            medicines = Medicine_Company.objects.filter(company_id_id=compID)
            data = {'Company': remove_password(model_to_dict(Company.objects.get(id=compID)), 'password'), 'Medicines': [ model_to_dict(mc.medicine_id) for mc in medicines]}
            return Response(data, status= status.HTTP_200_OK)
    elif(request.method=='POST'):
        #update the medicine
        medicine = request.data.get('medicine')
        otherInfo = request.data.get('info') 
        """
        Edge case: if a company is deleted and user send a request with a valid token this part might crash
        """
       # company = Company.objects.get(id=compID)
        if medicine and otherInfo:
            #check if the medicine already exist
            medicine_exists = Medicine.objects.filter(name=medicine.get('name'), manufacturerName=medicine.get('manufacturerName'))

            if len(medicine_exists)==0:

                # Medicine was created, create a new MedicineCompany object
                medicineSer = MedicineSerializer(data=medicine)
                if medicineSer.is_valid():
                    med = medicineSer.save()
                    medComp = {'company_id': compID, 'medicine_id': med.id}
                    medComp.update(otherInfo)
                    medCompSerializer = MedicineCompanySerializer(data=medComp)
                    print(medicineSer.data)
                    if medCompSerializer.is_valid():
                        medCompSerializer.save()
                        return Response({'medicine': medicineSer.data, 'infos': medCompSerializer.data}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'err': medCompSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'err': medicineSer.errors}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                medComp = {'company_id': compID, 'medicine_id': medicine_exists[0].id}
                medComp.update(otherInfo)
                medCompSerializer = MedicineCompanySerializer(data=medComp)
                if medCompSerializer.is_valid():
                    medCompSerializer.save()
                    mc = Medicine.objects.get(id=medicine_exists[0].id)
                    mc.owners+=1
                    mc.save()
                    return Response({'medicine': model_to_dict(medicine_exists[0]), 'infos': medCompSerializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'err': medCompSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'err':'provide the medicine to add and other infos'}, status = status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)
    
   

#Handle individual medicines
@api_view(['DELETE', 'PATCH', 'GET'])
@validation_error_decorator
def company_medicine(request,compID,medID ):
    is_uuid(compID, 'Company ID')
    is_uuid(medID, 'Medicine ID')
    if(request.method =='GET'):
        try:
            medicine = get_object_or_404(Medicine_Company, company_id=Company.objects.get(id=compID), medicine_id =Medicine.objects.get(id=medID) )
            return Response({'medicine': model_to_dict(medicine.medicine_id)}, status=status.HTTP_200_OK)

        except Http404:
            return Response({'mes': 'Medicine not found'}, status=status.HTTP_404_NOT_FOUND)
            
    if(request.method == 'PATCH'):
        try:
            medicine = get_object_or_404(Medicine_Company, company_id=Company.objects.get(id=compID), medicine_id =Medicine.objects.get(id=medID) )
            serializer = MedicineCompanySerializer(medicine, data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_202_ACCEPTED )
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Http404:
            return Response({'mes': f'Medicine with id= {medID} not found'}, status = status.HTTP_400_BAD_REQUEST)
    if(request.method=='DELETE'):
        try:
            medicine = get_object_or_404(Medicine_Company, company_id=Company.objects.get(id=compID), medicine_id =Medicine.objects.get(id=medID) )
            medic = Medicine.objects.get(id = medicine.medicine_id.id)
            medic.owners-=1
            if(medic.owners ==0):
                medic.delete()
            medicine.delete()
            serializer = MedicineCompanySerializer(medicine)
            return Response({'mes': 'Medicine was deleted successfully', 'med': serializer.data })
        except Http404:
            return Response({'mes': f'Medicine with id= {medID} not found'}, status = status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
            return Response({'Mes': 'Company Doesnt Exist'})

    
         

def yaml_to_html(request):
    if hasattr(settings, 'SWAGGER_YAML_FILE'):
        file = open(settings.SWAGGER_YAML_FILE)
        spec = yaml.load(file.read(), Loader=yaml.SafeLoader)
        return render(request, template_name="swagger_base.html", context={'data': json.dumps(spec, default=customJSONEncoder)})
    else:
        raise ImproperlyConfigured('You should define SWAGGER_YAML_FILE in your settings')

    








# #Company
# @api_view(['POST'])
# def create_company(request):
#     #name, description
#     serializer = CompanySerializer(request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)

# @api_view(['PATCH', 'DELETE', 'GET'])
# def single_company(request, compID):
#     if request.method== 'GET':
#         company_data = Company.objects.get(id = compID)
#         company_data.nHits = 1
#         serializer = CompanySerializer(company_data, many='True')
#         return Response(serializer.data)
#     if request.method == 'DELETE':
#         try:
#             company = get_object_or_404(Company, id=compID)
#             company.delete()
#             return Response({'mes': 'Company was deleted successfully', 'comp': company})
#         except Http404:
#             return Response({'mes': f'Company with id= {compID} not found'}, status = status.HTTP_404_NOT_FOUND)
#     if request.method == 'PATCH':
#         try:
#             company = get_object_or_404(Company, id=compID)
#             serializer = CompanySerializer(Company, data = request.data, partial = True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
#         except Http404:
#             return Response({'mes': f'Company with id= {compID} not found'}, status = status.HTTP_404_NOT_FOUND)