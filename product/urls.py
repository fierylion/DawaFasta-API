from django.urls import path
from . import views
urlpatterns = [
    path('', views.Home),
    path(r'api/v1/register/company', views.company_register),
    path(r'api/v1/login/company', views.company_login),
    path(r'api/v1/company/<str:compID>', views.single_company),
    path(r'api/v1/company/<str:compID>/medicine/<str:medID>', views.company_medicine),
    path(r'api/v1/company/<str:compID>/medicine/<str:medID>/sales', views.company_sales),
    #user apis
    path(r'api/v1/register/user', views.user_register),
    path(r'api/v1/login/user', views.user_login),
    path(r'api/v1/user/<str:userID>', views.single_user),
    path(r'api/v1/user/<str:userID>/purchase', views.user_purchase),
    path(r'api/v1/user/<str:userID>/purchase/history', views.user_purchase_history),
]
