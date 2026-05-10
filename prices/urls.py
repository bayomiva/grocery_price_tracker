from django.urls import path
from . import views

urlpatterns = [
    path('', views.PriceListCreateView.as_view()),
    path('compare/', views.ComparePricesView.as_view()),
    path('stats/', views.PriceStatsView.as_view()),
    path('recent/', views.RecentPricesView.as_view()),
    path('my-submissions/', views.MySubmissionsView.as_view()),
    path('leaderboard/', views.LeaderboardView.as_view()),
    # Admin
    path('pending/', views.PendingPricesView.as_view()),
    path('admin-all/', views.AdminAllSubmissionsView.as_view()),
    path('admin-stats/', views.AdminStatsView.as_view()),
    path('<int:pk>/', views.PriceAdminDetailView.as_view()),
    path('<int:pk>/approve/', views.PriceApproveView.as_view()),
    path('<int:pk>/reject/', views.PriceRejectView.as_view()),
]
