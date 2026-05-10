from django.urls import path
from . import views

urlpatterns = [
    path('', views.ItemListView.as_view()),
    path('<int:pk>/', views.ItemDetailView.as_view()),
    path('<int:pk>/upload-image/', views.ItemImageUploadView.as_view()),
]
