from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, F
from django.db import models
from .models import (
    CategoryMaster, CurrencyMaster, AITrainingData, AIPromptConfig,
    AIConversationMonitor, BudgetAlertThreshold, UserAnalytics,
    Transaction, Goal, Budget, User
)
from datetime import date, timedelta


@staff_member_required
def dashboard_view(request):
    """Main admin dashboard"""
    # Get statistics
    today = date.today()
    
    # User stats
    total_users = User.objects.filter(is_staff=False).count()
    new_users_today = User.objects.filter(is_staff=False, date_joined__date=today).count()
    
    # Transaction stats
    total_transactions = Transaction.objects.count()
    transactions_today = Transaction.objects.filter(created_at__date=today).count()
    
    # Financial stats
    total_income = Transaction.objects.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Goals and Budgets
    total_goals = Goal.objects.count()
    total_budgets = Budget.objects.count()
    
    context = {
        'title': 'Bảng Điều Khiển',
        'total_users': total_users,
        'new_users_today': new_users_today,
        'total_transactions': total_transactions,
        'transactions_today': transactions_today,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_goals': total_goals,
        'total_budgets': total_budgets,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def backbone_view(request):
    """Quản lý Hệ thống & Danh mục (Backbone)"""
    categories = CategoryMaster.objects.all()
    currencies = CurrencyMaster.objects.all()
    
    context = {
        'title': 'Quản lý Hệ thống & Danh mục',
        'categories': categories,
        'currencies': currencies,
        'total_categories': categories.count(),
        'active_categories': categories.filter(is_active=True).count(),
        'total_currencies': currencies.count(),
        'active_currencies': currencies.filter(is_active=True).count(),
    }
    
    return render(request, 'admin/backbone.html', context)


@staff_member_required
def ai_operations_view(request):
    """Quản lý AI & Tri thức (AI Operations)"""
    training_data = AITrainingData.objects.all()
    prompt_configs = AIPromptConfig.objects.all()
    conversation_monitor = AIConversationMonitor.objects.all()
    
    context = {
        'title': 'Quản lý AI & Tri thức',
        'training_data': training_data,
        'prompt_configs': prompt_configs,
        'conversation_monitor': conversation_monitor,
        'total_training_data': training_data.count(),
        'active_training_data': training_data.filter(is_active=True).count(),
        'total_prompts': prompt_configs.count(),
        'active_prompts': prompt_configs.filter(is_active=True).count(),
        'total_questions': conversation_monitor.count(),
        'flagged_questions': conversation_monitor.filter(is_flagged=True).count(),
    }
    
    return render(request, 'admin/ai_operations.html', context)


@staff_member_required
def analytics_view(request):
    """Quản lý Ngân sách & Mục tiêu (Analytics)"""
    alert_thresholds = BudgetAlertThreshold.objects.all()
    analytics = UserAnalytics.objects.all().order_by('-date')[:30]
    
    context = {
        'title': 'Quản lý Ngân sách & Mục tiêu',
        'alert_thresholds': alert_thresholds,
        'analytics': analytics,
        'total_thresholds': alert_thresholds.count(),
        'active_thresholds': alert_thresholds.filter(is_active=True).count(),
    }
    
    return render(request, 'admin/analytics.html', context)


@staff_member_required
def system_report_view(request):
    """UC12: Báo cáo hệ thống - Thống kê tổng hợp hoạt động"""
    from datetime import date, timedelta
    
    today = date.today()
    last_30_days = today - timedelta(days=30)
    
    # UC10: Thống kê người dùng
    total_users = User.objects.filter(is_staff=False).count()
    active_users = User.objects.filter(is_staff=False, is_active=True).count()
    new_users_30days = User.objects.filter(is_staff=False, date_joined__gte=last_30_days).count()
    
    # Thống kê giao dịch
    total_transactions = Transaction.objects.count()
    transactions_30days = Transaction.objects.filter(date__gte=last_30_days).count()
    total_income = Transaction.objects.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # UC11: Thống kê danh mục
    total_categories = CategoryMaster.objects.count() if CategoryMaster.objects.exists() else 0
    active_categories = CategoryMaster.objects.filter(is_active=True).count() if CategoryMaster.objects.exists() else 0
    user_categories = Transaction.objects.values('category__name').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Thống kê ngân sách và mục tiêu
    total_budgets = Budget.objects.count()
    total_goals = Goal.objects.count()
    completed_goals = Goal.objects.filter(current_amount__gte=models.F('target_amount')).count()
    
    context = {
        'title': 'Báo Cáo Hệ Thống',
        # UC10: Người dùng
        'total_users': total_users,
        'active_users': active_users,
        'new_users_30days': new_users_30days,
        'inactive_users': total_users - active_users,
        # Giao dịch
        'total_transactions': total_transactions,
        'transactions_30days': transactions_30days,
        'total_income': int(total_income),
        'total_expense': int(total_expense),
        'net_balance': int(total_income - total_expense),
        # UC11: Danh mục
        'total_categories': total_categories,
        'active_categories': active_categories,
        'user_categories': user_categories,
        # Ngân sách & Mục tiêu
        'total_budgets': total_budgets,
        'total_goals': total_goals,
        'completed_goals': completed_goals,
        'goal_completion_rate': round((completed_goals / total_goals * 100) if total_goals > 0 else 0, 1),
    }
    
    return render(request, 'admin/system_report.html', context)
