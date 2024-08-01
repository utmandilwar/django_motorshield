from . import views

from django.urls import path, include

from rest_framework import routers

from MotorInsuranceCompany.API.views import *

router = routers.DefaultRouter()
router.register('vehicle', VehicleViewSet, basename='vehicleView')
router.register('vehicle-owner', OwnerViewSet, basename='ownerView')
router.register('policy-details', PolicyViewSet, basename='policyView')
router.register('claims', ClaimViewSet, basename='claimView')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('', include(router.urls)),
]