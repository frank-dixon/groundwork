from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.GroundworkLoginView.as_view(), name='login'),
    path('logout/', views.GroundworkLogoutView.as_view(), name='logout'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('layouts/', views.layout_list, name='layout_list'),
    path('layouts/new/', views.layout_create, name='layout_create'),
    path('layouts/<int:pk>/', views.layout_detail, name='layout_detail'),
    path('layouts/<int:pk>/edit/', views.layout_edit, name='layout_edit'),
    path('layouts/<int:pk>/delete/', views.layout_delete, name='layout_delete'),
    path('layouts/<int:layout_pk>/beds/new/', views.bed_create, name='bed_create'),
    path('layouts/<int:pk>/suggest/', views.layout_suggest, name='layout_suggest'),
    path('beds/<int:pk>/delete/', views.bed_delete, name='bed_delete'),
    path('beds/<int:bed_pk>/plants/add/', views.placement_add, name='placement_add'),
    path('placements/<int:pk>/delete/', views.placement_delete, name='placement_delete'),
    path('plants/', views.plant_list, name='plant_list'),
    path('plants/<slug:slug>/', views.plant_detail, name='plant_detail'),
    path('pro/', views.pro_stub, name='pro'),
]
