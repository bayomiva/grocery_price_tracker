from django.urls import path
from . import views

urlpatterns = [
    path('', views.ScraperMetaView.as_view()),
    path('jobs/', views.ScrapingJobListCreateView.as_view()),
    path('jobs/<int:pk>/', views.ScrapingJobDetailView.as_view()),
    path('jobs/<int:pk>/import/', views.ImportResultsView.as_view()),
]
