from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('staff/users/', views.admin_users, name='admin_users'),
    path('staff/users/add/', views.admin_user_add, name='admin_user_add'),
    path('staff/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('staff/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),

    path('transactions/', views.transactions, name='transactions'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/bulk-import/', views.transaction_bulk_import, name='transaction_bulk_import'),
    path('transactions/export/csv/', views.export_transactions_csv, name='export_transactions_csv'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),

    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('budgets/', views.budgets, name='budgets'),
    path('budgets/add/', views.budget_add, name='budget_add'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('budgets/<int:pk>/delete/', views.budget_delete, name='budget_delete'),

    path('goals/', views.goals, name='goals'),
    path('goals/add/', views.goal_add, name='goal_add'),
    path('goals/<int:pk>/edit/', views.goal_edit, name='goal_edit'),
    path('goals/<int:pk>/deposit/', views.goal_deposit, name='goal_deposit'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),

    path('ai/', views.ai_page, name='ai'),
    path('ai/chat/', views.ai_chat, name='ai_chat'),
    path('ai/refresh/', views.ai_refresh_suggestions, name='ai_refresh'),
    path('ai/clear/', views.ai_clear_chat, name='ai_clear_chat'),
    path('ai/delete-session/', views.ai_delete_session, name='ai_delete_session'),
    path('dashboard/refresh-suggestions/', views.refresh_dashboard_suggestions, name='refresh_suggestions'),

    path('profile/', views.profile, name='profile'),

    path('video/', views.video_demo, name='video_demo'),
]

