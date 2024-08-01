from . import views

from django.urls import path


urlpatterns = [
    path('', views.home, name="home"),
    path('home', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('about', views.about, name="aboutus"),
    path('menu', views.menu, name="menu"),
    path('vehicle_details', views.vehicle_details, name="vehicle_details"),
    path('owner_details/<str:signed_vid>/', views.owner_details, name="owner_details"),
    path('add_ons/<str:signed_vid>/', views.add_ons, name="add_ons"),
    path('proposal_form_submitted/<str:signed_vid>/', views.proposal_form_submitted, name='proposal_form_submitted'),
    path('track_policy/<str:signed_vid>/', views.track_policy, name='track_policy'),
    path('details_to_track_policy', views.details_to_track_policy, name='details_to_track_policy'),
    path('details_to_make_payment', views.details_to_make_payment, name='details_to_make_payment'),
    path('premium_breakup/<str:signed_pid>/', views.premium_breakup, name='premium_breakup'),
    path('payment_done/<str:signed_pid>/', views.payment_done, name='payment_done'),
    path('details_to_renew_policy', views.details_to_renew_policy, name='details_to_renew_policy'),
    path('file_for_claim', views.file_for_claim, name='file_for_claim'),
    path('claim_submitted/<str:signed_vid>/', views.claim_submitted, name='claim_submitted'),
    path('track_claim/<str:signed_vid>/', views.track_claim, name='track_claim'),
    path('details_to_track_claim', views.details_to_track_claim, name='details_to_track_claim'),
]
