from django.urls import path
from . import views

urlpatterns = [
    path('', views.StoreListView.as_view()),
    path('nearby/', views.NearbyStoresView.as_view()),
    path('states/', views.StatesListView.as_view()),
]
