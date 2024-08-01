from django.urls import path, include

from MotorInsuranceCompany.API.views import *

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('add-vehicle/', VehicleCreateView.as_view(), name='add-vehicle'),
    path('vehicles/<int:pk>/', VehicleDetailView.as_view(), name='vehicle-detail'),
    # path('add-owner/', OwnerCreateView.as_view(), name='add-owner'),
    path('add-policy/', PolicyCreateView.as_view(), name='add-policy'),
    path('policies/<str:vehicle_number>/', PolicyDetailView.as_view(), name='policy-detail'),
    path('policies/<int:pk>/update/', PolicyUpdateView.as_view(), name='policy-update'),
    path('send-policy-on-email/', SendPolicyOnEmailView.as_view(), name='send-policy-on-email'),
    path('add-claim/', ClaimCreateView.as_view(), name='add-claim'),
    path('claims/<str:vehicle_number>/', ClaimDetailView.as_view(), name='claim-detail')
]