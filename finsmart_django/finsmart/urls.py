from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from finance.admin_views import (
    dashboard_view, backbone_view, ai_operations_view, analytics_view, system_report_view
)

urlpatterns = [
    # Custom admin views (PHẢI ĐẶT TRƯỚC admin.site.urls)
    path('admin/dashboard/', dashboard_view, name='dashboard'),
    path('admin/backbone/', backbone_view, name='backbone'),
    path('admin/ai-operations/', ai_operations_view, name='ai_operations'),
    path('admin/analytics/', analytics_view, name='analytics'),
    path('admin/system-report/', system_report_view, name='system_report'),
    
    # Django admin (ĐẶT SAU các custom views)
    path('admin/', admin.site.urls),
    
    # Finance app URLs
    path('', include('finance.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
