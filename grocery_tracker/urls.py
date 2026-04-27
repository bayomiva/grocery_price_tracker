from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import login_page, register_page
from prices.views import index_page, submit_price_page, compare_prices_page, admin_dashboard_page, DashboardSummaryView

urlpatterns = [
    path('admin/', admin.site.urls),

    # HTML pages
    path('', index_page, name='index'),
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path('submit-price/', submit_price_page, name='submit_price'),
    path('compare-prices/', compare_prices_page, name='compare_prices'),
    path('admin-dashboard/', admin_dashboard_page, name='admin_dashboard'),

    # REST API
    path('api/accounts/', include('accounts.urls')),
    path('api/stores/', include('stores.urls')),
    path('api/items/', include('items.urls')),
    path('api/prices/', include('prices.urls')),
    path('api/dashboard/', DashboardSummaryView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
