from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.urls import reverse
from django.utils import timezone
from datetime import date, datetime
import json
import os
import random
from uuid import uuid4
import csv

from .ai_suggestions import seed_suggestions_all_months
from .models import Category, Transaction, Budget, Goal, ChatMessage, AISuggestion
from .forms import (
    LoginForm,
    RegisterForm,
    AdminUserCreationForm,
    AdminUserUpdateForm,
    CategoryForm,
    TransactionForm,
    BulkTransactionForm,
    BudgetForm,
    GoalForm,
    ProfileForm,
    ProfilePasswordForm,
)


# ─────────────────────────────── Auth ────────────────────────────────

def index(request):
    if request.user.is_authenticated:
        return redirect('/admin/' if request.user.is_staff else 'dashboard')
    return redirect('login')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/admin/' if request.user.is_staff else 'dashboard')
    if request.method == 'POST':
        email = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('/admin/' if user.is_staff else 'dashboard')
        messages.error(request, 'Email hoặc mật khẩu không đúng.')
    form = LoginForm(request)
    return render(request, 'finance/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Chào mừng {user.first_name} đến với FinSmart!')
            _seed_suggestions(user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'finance/register.html', {'form': form})


# ─────────────────────────────── Dashboard ───────────────────────────

@login_required
@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('/admin/')

    now = date.today()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))

    txs = Transaction.objects.filter(user=request.user, date__month=month, date__year=year)
    total_income = int(txs.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0)
    total_expense = int(txs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0)
    balance = total_income - total_expense
    savings_rate = round((balance / total_income) * 100) if total_income > 0 else 0

    # Category breakdown for expense pie chart
    cat_breakdown = (
        txs.filter(type='expense')
        .values('category__name', 'category__color')
        .annotate(total=Sum('amount'))
        .order_by('-total')[:6]
    )
    chart_labels = [x['category__name'] or 'Khác' for x in cat_breakdown]
    chart_data = [int(x['total']) for x in cat_breakdown]
    chart_colors = [x['category__color'] or '#6B7280' for x in cat_breakdown]

    # Monthly trend (6 months) - Dựa trên tháng/năm được chọn
    trend_labels, trend_income, trend_expense = [], [], []
    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        month_txs = Transaction.objects.filter(user=request.user, date__month=m, date__year=y)
        inc = int(month_txs.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0)
        exp = int(month_txs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0)
        trend_labels.append(f'T{m}/{str(y)[2:]}')
        trend_income.append(inc)
        trend_expense.append(exp)

    # Budgets with status
    budgets = Budget.objects.filter(user=request.user, month=month, year=year)
    budget_alerts = [b for b in budgets if b.status in ('warning', 'exceeded')]

    # Recent transactions
    recent_txs = Transaction.objects.filter(user=request.user).select_related('category')[:5]

    # Goals
    goals_qs = Goal.objects.filter(user=request.user)[:4]

    # AI Suggestions - Dựa vào dữ liệu tháng được chọn
    ai_suggestions = AISuggestion.objects.filter(
        user=request.user,
        created_at__month=month,
        created_at__year=year
    ).order_by('-created_at')[:3]
    
    if not ai_suggestions:
        # Tạo suggestions cho tháng được chọn
        _seed_suggestions_for_month(request.user, month, year)
        ai_suggestions = AISuggestion.objects.filter(
            user=request.user,
            created_at__month=month,
            created_at__year=year
        ).order_by('-created_at')[:3]

    return render(request, 'finance/dashboard.html', {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'savings_rate': savings_rate,
        'month': month,
        'year': year,
        'chart_labels': json.dumps(chart_labels, ensure_ascii=False),
        'chart_data': json.dumps(chart_data),
        'chart_colors': json.dumps(chart_colors),
        'trend_labels': json.dumps(trend_labels),
        'trend_income': json.dumps(trend_income),
        'trend_expense': json.dumps(trend_expense),
        'budget_alerts': budget_alerts,
        'recent_txs': recent_txs,
        'goals': goals_qs,
        'ai_suggestions': ai_suggestions,
        'tx_count': txs.count(),
    })


@login_required
def admin_users(request):
    from django.core.paginator import Paginator
    
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('dashboard')

    page = request.GET.get('page', 1)
    
    admins_qs = User.objects.filter(is_staff=True).order_by('-is_superuser', 'first_name', 'last_name', 'username')
    users_qs = User.objects.filter(is_staff=False).order_by('first_name', 'last_name', 'username')
    
    # Phân trang: 20 người dùng mỗi trang
    paginator_admins = Paginator(admins_qs, 20)
    paginator_users = Paginator(users_qs, 20)
    
    admins_page = paginator_admins.get_page(page)
    users_page = paginator_users.get_page(page)
    
    return render(request, 'finance/admin_users.html', {
        'admin_accounts': admins_page,
        'user_accounts': users_page,
        'paginator_admins': paginator_admins,
        'paginator_users': paginator_users,
    })


@login_required
def admin_user_add(request):
    if not request.user.is_staff:
        messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Đã tạo tài khoản cho {user.get_full_name() or user.email}.')
            return redirect('admin_users')
    else:
        form = AdminUserCreationForm()

    return render(request, 'finance/admin_user_form.html', {
        'form': form,
        'title': 'Thêm người dùng',
    })


# ─────────────────────────────── Transactions ────────────────────────

@login_required
def admin_user_edit(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Báº¡n khĂ´ng cĂ³ quyá»n thá»±c hiá»‡n thao tĂ¡c nĂ y.')
        return redirect('dashboard')

    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            updated_user = form.save()
            messages.success(request, f'ÄĂ£ cáº­p nháº­t tĂ i khoáº£n {updated_user.get_full_name() or updated_user.email}.')
            return redirect('admin_users')
    else:
        form = AdminUserUpdateForm(instance=user_obj)

    return render(request, 'finance/admin_user_form.html', {
        'form': form,
        'title': 'Cáº­p nháº­t ngÆ°á»i dĂ¹ng',
        'editing_user': user_obj,
    })


@login_required
def admin_user_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Báº¡n khĂ´ng cĂ³ quyá»n thá»±c hiá»‡n thao tĂ¡c nĂ y.')
        return redirect('dashboard')

    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        messages.error(request, 'Báº¡n khĂ´ng thá»ƒ tá»± xĂ³a chĂ­nh mĂ¬nh.')
        return redirect('admin_users')

    if request.method == 'POST':
        display_name = user_obj.get_full_name() or user_obj.email or user_obj.username
        user_obj.delete()
        messages.success(request, f'ÄĂ£ xĂ³a tĂ i khoáº£n {display_name}.')
    return redirect('admin_users')


@login_required
def transactions(request):
    from django.core.paginator import Paginator
    
    now = date.today()
    month = request.GET.get('month', now.month)
    year = request.GET.get('year', now.year)
    tx_type = request.GET.get('type', '')
    category_id = request.GET.get('category', '')
    page = request.GET.get('page', 1)

    qs = Transaction.objects.filter(user=request.user).select_related('category').order_by('-date')
    if month and year:
        qs = qs.filter(date__month=month, date__year=year)
    if tx_type:
        qs = qs.filter(type=tx_type)
    if category_id:
        qs = qs.filter(category_id=category_id)

    total_income = int(qs.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0)
    total_expense = int(qs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0)

    # Phân trang: 20 giao dịch mỗi trang
    paginator = Paginator(qs, 20)
    transactions_page = paginator.get_page(page)

    categories = Category.objects.filter(Q(is_default=True) | Q(user=request.user))
    months = [(i, f'Tháng {i}') for i in range(1, 13)]
    years = list(range(2023, now.year + 2))

    return render(request, 'finance/transactions.html', {
        'transactions': transactions_page,
        'total_income': total_income,
        'total_expense': total_expense,
        'categories': categories,
        'months': months,
        'years': years,
        'sel_month': int(month),
        'sel_year': int(year),
        'sel_type': tx_type,
        'sel_category': category_id,
        'paginator': paginator,
    })


@login_required
def transaction_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.user = request.user
            tx.save()
            messages.success(request, 'Đã thêm giao dịch thành công!')
            return redirect('transactions')
    else:
        form = TransactionForm(user=request.user, initial={'date': date.today()})
    return render(request, 'finance/transaction_form.html', {
        'form': form, 
        'title': 'Thêm giao dịch',
    })


@login_required
def transaction_bulk_import(request):
    """Nhập hàng loạt giao dịch"""
    if request.method == 'POST':
        form = BulkTransactionForm(request.POST, user=request.user)
        if form.is_valid():
            created_count = form.save()
            messages.success(request, f'✅ Đã nhập thành công {created_count} giao dịch!')
            
            # Tự động tạo suggestions cho tất cả tháng
            _seed_suggestions(request.user)
            
            return redirect('transactions')
    else:
        form = BulkTransactionForm(user=request.user)
    
    return render(request, 'finance/transaction_bulk_import.html', {
        'form': form,
        'title': 'Nhập hàng loạt giao dịch'
    })


@login_required
def transaction_edit(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=tx, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật giao dịch!')
            return redirect('transactions')
    else:
        form = TransactionForm(instance=tx, user=request.user)
    return render(request, 'finance/transaction_form.html', {'form': form, 'title': 'Sửa giao dịch'})


@login_required
def transaction_delete(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        tx.delete()
        messages.success(request, 'Đã xóa giao dịch!')
    return redirect('transactions')


# ─────────────────────────────── Export Reports ──────────────────────

@login_required
def export_transactions_csv(request):
    """Xuất giao dịch ra CSV"""
    now = date.today()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))
    tx_type = request.GET.get('type', '')
    category_id = request.GET.get('category', '')
    
    # Lấy dữ liệu giao dịch
    qs = Transaction.objects.filter(user=request.user).select_related('category').order_by('-date')
    if month and year:
        qs = qs.filter(date__month=month, date__year=year)
    if tx_type:
        qs = qs.filter(type=tx_type)
    if category_id:
        qs = qs.filter(category_id=category_id)
    
    # Tạo CSV response
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="giao_dich_{month}_{year}.csv"'
    
    # Thêm BOM cho UTF-8
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow(['Ngày', 'Mô Tả', 'Danh Mục', 'Loại', 'Số Tiền'])
    
    for tx in qs:
        writer.writerow([
            tx.date.strftime('%d/%m/%Y'),
            tx.description,
            tx.category.name if tx.category else 'Không có',
            tx.get_type_display(),
            f"{tx.amount:,}đ"
        ])
    
    return response




# ─────────────────────────────── Categories ──────────────────────────

@login_required
def categories(request):
    tab = request.GET.get('tab', 'user')  # 'user' hoặc 'default'
    
    default_cats = Category.objects.filter(is_default=True).order_by('name')
    user_cats = Category.objects.filter(user=request.user, is_default=False).order_by('name')
    
    return render(request, 'finance/categories.html', {
        'default_cats': default_cats,
        'user_cats': user_cats,
        'tab': tab,
    })


@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request, 'Đã thêm danh mục!')
            return redirect('categories')
    else:
        form = CategoryForm()
    return render(request, 'finance/category_form.html', {'form': form, 'title': 'Thêm danh mục'})


@login_required
def category_edit(request, pk):
    # Cho phép sửa category của user hoặc default category
    cat = get_object_or_404(Category, pk=pk)
    
    # Kiểm tra quyền: Chỉ cho phép sửa nếu là category của user hoặc là default category
    if cat.user and cat.user != request.user:
        messages.error(request, 'Bạn không có quyền sửa danh mục này!')
        return redirect('categories')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật danh mục!')
            return redirect('categories')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'finance/category_form.html', {'form': form, 'title': 'Sửa danh mục'})


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    # Cho phép xóa danh mục riêng hoặc danh mục mặc định (superuser)
    if not cat.is_default and cat.user != request.user:
        messages.error(request, 'Bạn không có quyền xóa danh mục này!')
        return redirect('categories')
    if request.method == 'POST':
        name = cat.name
        cat.delete()
        messages.success(request, f'Đã xóa danh mục "{name}"!')
    return redirect('categories')


# ─────────────────────────────── Budgets ─────────────────────────────

@login_required
def budgets(request):
    from django.core.paginator import Paginator
    
    now = date.today()
    month = int(request.GET.get('month', now.month))
    year = int(request.GET.get('year', now.year))
    page = request.GET.get('page', 1)
    
    budgets_qs = Budget.objects.filter(user=request.user, month=month, year=year).select_related('category')
    
    # Thêm thông tin liên kết và phân tích
    budgets_with_analysis = []
    for budget in budgets_qs:
        variance_pct = budget.budget_variance_percentage
        budget_data = {
            'budget': budget,
            'remaining_budget': budget.remaining_budget,
            'remaining_budget_current_month': budget.remaining_budget_current_month,
            'daily_budget_remaining': budget.daily_budget_remaining,
            'overspend_by_category': budget.overspend_by_category,
            'previous_month_budget': budget.previous_month_budget,
            'budget_variance': budget.budget_variance,
            'budget_variance_percentage': variance_pct,
            'budget_variance_abs': abs(variance_pct) if variance_pct else None,
            'is_budget_reasonable': budget.is_budget_reasonable,
        }
        budgets_with_analysis.append(budget_data)
    
    # Phân trang: 15 ngân sách mỗi trang
    paginator = Paginator(budgets_with_analysis, 15)
    budgets_page = paginator.get_page(page)
    
    months = [(i, f'Tháng {i}') for i in range(1, 13)]
    years = list(range(2023, now.year + 2))
    return render(request, 'finance/budgets.html', {
        'budgets': budgets_page,
        'month': month,
        'year': year,
        'months': months,
        'years': years,
        'paginator': paginator,
    })


@login_required
def budget_add(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            b = form.save(commit=False)
            b.user = request.user
            b.save()
            messages.success(request, 'Đã tạo ngân sách!')
            return redirect('budgets')
    else:
        now = date.today()
        form = BudgetForm(user=request.user, initial={'month': now.month, 'year': now.year})
    return render(request, 'finance/budget_form.html', {'form': form, 'title': 'Thêm ngân sách'})


@login_required
def budget_edit(request, pk):
    b = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=b, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật ngân sách!')
            return redirect('budgets')
    else:
        form = BudgetForm(instance=b, user=request.user)
    return render(request, 'finance/budget_form.html', {'form': form, 'title': 'Sửa ngân sách'})


@login_required
def budget_delete(request, pk):
    b = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        b.delete()
        messages.success(request, 'Đã xóa ngân sách!')
        return redirect('budgets')
    return render(request, 'finance/budget_confirm_delete.html', {'object': b})


# ─────────────────────────────── Goals ───────────────────────────────

@login_required
@login_required
def goals(request):
    from django.core.paginator import Paginator
    from django.db.models import Sum
    from datetime import date, timedelta
    
    page = request.GET.get('page', 1)
    goals_qs = Goal.objects.filter(user=request.user)
    today = date.today()
    
    # Tính tổng số dư từ tất cả các tháng TRƯỚC tháng hiện tại
    # Lấy tất cả giao dịch từ các tháng trước
    total_remaining_all_months = 0
    
    # Lấy tất cả giao dịch của user
    all_transactions = Transaction.objects.filter(user=request.user)
    
    # Nhóm giao dịch theo tháng/năm
    months_data = {}
    for tx in all_transactions:
        month_key = (tx.date.year, tx.date.month)
        if month_key not in months_data:
            months_data[month_key] = {'income': 0, 'expense': 0}
        
        if tx.type == 'income':
            months_data[month_key]['income'] += int(tx.amount)
        else:
            months_data[month_key]['expense'] += int(tx.amount)
    
    # Tính tổng dư từ các tháng TRƯỚC tháng hiện tại
    for (year, month), data in months_data.items():
        # Chỉ tính các tháng TRƯỚC tháng hiện tại
        if year < today.year or (year == today.year and month < today.month):
            month_remaining = data['income'] - data['expense']
            total_remaining_all_months += max(month_remaining, 0)
    
    # Thêm thông tin liên kết và phân tích
    goals_with_analysis = []
    for goal in goals_qs:
        goal_data = {
            'goal': goal,
            'monthly_savings_from_budget': goal.monthly_savings_from_budget,
            'on_track_for_deadline': goal.on_track_for_deadline,
            'required_savings_rate': goal.required_savings_rate,
            'is_achievable': goal.is_achievable,
            'auto_calculate_current_amount': goal.auto_calculate_current_amount,
        }
        goals_with_analysis.append(goal_data)
    
    # Phân trang: 15 mục tiêu mỗi trang
    paginator = Paginator(goals_with_analysis, 15)
    goals_page = paginator.get_page(page)
    
    return render(request, 'finance/goals.html', {
        'goals': goals_page,
        'paginator': paginator,
        'total_remaining_all_months': total_remaining_all_months,
    })


@login_required
def goal_add(request):
    if request.method == 'POST':
        form = GoalForm(request.POST, user=request.user)
        if form.is_valid():
            g = form.save(commit=False)
            g.user = request.user
            g.save()
            messages.success(request, 'Đã tạo mục tiêu tiết kiệm!')
            return redirect('goals')
    else:
        form = GoalForm(user=request.user)
    return render(request, 'finance/goal_form.html', {
        'form': form, 
        'title': 'Thêm mục tiêu'
    })


@login_required
@login_required
def goal_edit(request, pk):
    g = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=g, user=request.user)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.save()
            messages.success(request, 'Đã cập nhật mục tiêu!')
            return redirect('goals')
    else:
        form = GoalForm(instance=g, user=request.user)
    return render(request, 'finance/goal_form.html', {
        'form': form, 
        'title': 'Sửa mục tiêu',
        'goal': g
    })


@login_required
def goal_deposit(request, pk):
    """Nạp tiền tiết kiệm vào Goal"""
    from django.db.models import Sum
    from datetime import date
    
    g = get_object_or_404(Goal, pk=pk, user=request.user)
    today = date.today()
    
    if request.method == 'POST':
        amount = int(request.POST.get('amount', 0))
        
        if amount <= 0:
            messages.error(request, 'Số tiền phải lớn hơn 0!')
            return redirect('goals')
        
        # Tính tổng số dư từ tất cả các tháng TRƯỚC tháng hiện tại
        all_transactions = Transaction.objects.filter(user=request.user)
        
        # Nhóm giao dịch theo tháng/năm
        months_data = {}
        for tx in all_transactions:
            month_key = (tx.date.year, tx.date.month)
            if month_key not in months_data:
                months_data[month_key] = {'income': 0, 'expense': 0}
            
            if tx.type == 'income':
                months_data[month_key]['income'] += int(tx.amount)
            else:
                months_data[month_key]['expense'] += int(tx.amount)
        
        # Tính tổng dư từ các tháng TRƯỚC tháng hiện tại
        total_remaining = 0
        for (year, month), data in months_data.items():
            # Chỉ tính các tháng TRƯỚC tháng hiện tại
            if year < today.year or (year == today.year and month < today.month):
                month_remaining = data['income'] - data['expense']
                total_remaining += max(month_remaining, 0)
        
        # Tính số tiền còn thiếu để đạt mục tiêu
        remaining_to_goal = max(int(g.target_amount) - int(g.current_amount), 0)
        
        # Số tiền nạp tối đa = min(số tiền còn thiếu, tổng số dư hiện có)
        max_deposit = min(remaining_to_goal, total_remaining)
        
        if amount > max_deposit:
            if remaining_to_goal < total_remaining:
                messages.error(request, f'Số tiền nạp vượt quá số tiền còn thiếu ({remaining_to_goal:,}đ)! Bạn chỉ cần nạp tối đa {max_deposit:,}đ để đạt mục tiêu.')
            else:
                messages.error(request, f'Số tiền nạp vượt quá tổng số dư hiện có ({total_remaining:,}đ)!')
            return redirect('goals')
        
        if amount > total_remaining:
            messages.error(request, f'Số tiền nạp vượt quá tổng số dư hiện có ({total_remaining:,}đ)!')
            return redirect('goals')
        
        # Nạp tiền vào Goal
        g.current_amount = int(g.current_amount) + amount
        g.save()
        
        # Tạo giao dịch chi tiêu để trừ từ tổng số dư (bắt đầu từ tháng cũ nhất)
        remaining_to_deduct = amount
        
        # Sắp xếp các tháng từ cũ nhất đến mới nhất
        sorted_months = sorted(months_data.keys())
        
        for (year, month) in sorted_months:
            if remaining_to_deduct <= 0:
                break
            
            # Chỉ trừ từ các tháng TRƯỚC tháng hiện tại
            if year < today.year or (year == today.year and month < today.month):
                data = months_data[(year, month)]
                month_remaining = max(data['income'] - data['expense'], 0)
                
                if month_remaining > 0:
                    # Trừ từ tháng này
                    deduct_amount = min(remaining_to_deduct, month_remaining)
                    
                    # Tạo giao dịch chi tiêu để trừ từ tổng số dư
                    # Lấy danh mục "Nạp tiền tiết kiệm" hoặc tạo mới
                    category, _ = Category.objects.get_or_create(
                        user=request.user,
                        name='Nạp tiền tiết kiệm',
                        defaults={'type': 'expense', 'icon': '💰'}
                    )
                    
                    # Tạo giao dịch chi tiêu
                    Transaction.objects.create(
                        user=request.user,
                        type='expense',
                        amount=deduct_amount,
                        description=f'Nạp tiền vào mục tiêu "{g.name}"',
                        category=category,
                        date=date(year, month, 1)  # Ngày đầu tháng
                    )
                    
                    remaining_to_deduct -= deduct_amount
        
        messages.success(request, f'Đã nạp {amount:,}đ vào mục tiêu "{g.name}"!')
        return redirect('goals')
    
    # Tính tổng số dư (chỉ các tháng TRƯỚC tháng hiện tại)
    all_transactions = Transaction.objects.filter(user=request.user)
    
    # Nhóm giao dịch theo tháng/năm
    months_data = {}
    for tx in all_transactions:
        month_key = (tx.date.year, tx.date.month)
        if month_key not in months_data:
            months_data[month_key] = {'income': 0, 'expense': 0}
        
        if tx.type == 'income':
            months_data[month_key]['income'] += int(tx.amount)
        else:
            months_data[month_key]['expense'] += int(tx.amount)
    
    # Tính tổng dư từ các tháng TRƯỚC tháng hiện tại
    total_remaining = 0
    for (year, month), data in months_data.items():
        # Chỉ tính các tháng TRƯỚC tháng hiện tại
        if year < today.year or (year == today.year and month < today.month):
            month_remaining = data['income'] - data['expense']
            total_remaining += max(month_remaining, 0)
    
    # Tính số tiền còn thiếu để đạt mục tiêu
    remaining_to_goal = max(int(g.target_amount) - int(g.current_amount), 0)
    
    # Số tiền nạp tối đa = min(số tiền còn thiếu, tổng số dư hiện có)
    max_deposit = min(remaining_to_goal, total_remaining)
    
    return render(request, 'finance/goal_deposit.html', {
        'goal': g,
        'total_remaining': total_remaining,
        'max_deposit': max_deposit,
        'remaining_to_goal': remaining_to_goal,
    })


@login_required
def goal_delete(request, pk):
    from datetime import date
    
    g = get_object_or_404(Goal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal_name = g.name
        current_amount = int(g.current_amount)
        
        # Hoàn lại số tiền bằng cách xóa các giao dịch chi tiêu đã nạp
        if current_amount > 0:
            # Lấy danh mục "Nạp tiền tiết kiệm" (chi tiêu)
            expense_category = Category.objects.filter(
                user=request.user,
                name='Nạp tiền tiết kiệm',
                type='expense'
            ).first()
            
            if expense_category:
                # Dùng description chính xác để tránh xóa nhầm
                exact_description = f'Nạp tiền vào mục tiêu "{goal_name}"'
                
                # Tìm tất cả giao dịch liên quan
                related_transactions = Transaction.objects.filter(
                    user=request.user,
                    type='expense',
                    category=expense_category,
                    description=exact_description
                )
                
                # Debug: Kiểm tra số lượng giao dịch tìm thấy
                count = related_transactions.count()
                total_amount = sum(int(tx.amount) for tx in related_transactions)
                
                # Xóa các giao dịch
                deleted_count = related_transactions.delete()[0]
                
                if deleted_count > 0:
                    messages.info(request, f'Đã xóa {deleted_count} giao dịch nạp tiền (tổng {total_amount:,}đ).')
                else:
                    # Không tìm thấy giao dịch nào
                    messages.warning(request, f'Không tìm thấy giao dịch nạp tiền để hoàn lại. Có thể giao dịch đã bị xóa thủ công.')
            else:
                messages.warning(request, f'Không tìm thấy danh mục "Nạp tiền tiết kiệm". Không thể hoàn lại tiền.')
        
        g.delete()
        
        if current_amount > 0:
            messages.success(request, f'Đã xóa mục tiêu "{goal_name}"!')
        else:
            messages.success(request, f'Đã xóa mục tiêu "{goal_name}"!')
        
        return redirect('goals')
    return render(request, 'finance/goal_confirm_delete.html', {'object': g})


# ─────────────────────────────── AI ──────────────────────────────────

@login_required
def ai_page(request):
    # Debug: Check what months have data
    from django.db.models import Count
    months_with_data = Transaction.objects.filter(user=request.user).extra(
        select={'month': 'MONTH(date)', 'year': 'YEAR(date)'}
    ).values('year', 'month').annotate(count=Count('id')).order_by('-year', '-month')
    
    # Get all suggestions for this user
    all_suggestions = AISuggestion.objects.filter(user=request.user).order_by('-created_at')
    
    # If no suggestions, generate them
    if not all_suggestions.exists():
        _seed_suggestions(request.user)
        all_suggestions = AISuggestion.objects.filter(user=request.user).order_by('-created_at')
    
    # Select 3 random suggestions each time
    suggestions_list = list(all_suggestions)
    if len(suggestions_list) > 3:
        suggestions = random.sample(suggestions_list, 3)
    else:
        suggestions = suggestions_list

    requested_session = request.GET.get('session', '').strip()
    start_new_chat = request.GET.get('new') in {'1', 'true', 'yes'}

    history_items = []
    session_map = {}
    for msg in ChatMessage.objects.filter(user=request.user).order_by('-created_at'):
        session_key = (msg.session_key or 'default').strip() or 'default'
        item = session_map.get(session_key)
        if item is None:
            item = {
                'session_key': session_key,
                'preview': msg.content,
                'created_at': msg.created_at,
            }
            session_map[session_key] = item
            history_items.append(item)
        if msg.role == 'user':
            item['preview'] = msg.content

    valid_sessions = {item['session_key'] for item in history_items}
    if start_new_chat:
        active_session = ''
    elif requested_session in valid_sessions:
        active_session = requested_session
    elif history_items:
        active_session = history_items[0]['session_key']
    else:
        active_session = ''

    for item in history_items:
        item['is_active'] = item['session_key'] == active_session

    messages_qs = ChatMessage.objects.filter(
        user=request.user,
        session_key=active_session,
    ).order_by('created_at') if active_session else ChatMessage.objects.none()
    last_updated = messages_qs.last().created_at if active_session and messages_qs.exists() else None

    return render(request, 'finance/ai.html', {
        'suggestions': suggestions,
        'chat_messages': messages_qs,
        'chat_history_menu': history_items[:30],
        'active_session': active_session,
        'last_updated': last_updated,
        'months_with_data': months_with_data,  # Debug info
    })


@login_required
def ai_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Tin nhắn trống'}, status=400)

    session_key = (data.get('session_key') or '').strip()[:40]
    if not session_key:
        session_key = f"chat-{timezone.now():%Y%m%d%H%M%S}-{uuid4().hex[:8]}"

    user_msg = ChatMessage.objects.create(
        user=request.user,
        session_key=session_key,
        role='user',
        content=user_message,
    )

    now = date.today()
    
    # Lấy dữ liệu tháng hiện tại
    current_month_txs = Transaction.objects.filter(user=request.user, date__month=now.month, date__year=now.year)
    current_income = int(current_month_txs.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0)
    current_expense = int(current_month_txs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0)

    current_cat_summary = {}
    for tx in current_month_txs.filter(type='expense').select_related('category'):
        cat = tx.category.name if tx.category else 'Khác'
        current_cat_summary[cat] = current_cat_summary.get(cat, 0) + int(tx.amount)

    # Lấy dữ liệu tất cả các tháng có giao dịch
    all_months_data = []
    all_txs = Transaction.objects.filter(user=request.user).values_list('date', flat=True).distinct()
    
    if all_txs:
        months_set = set()
        for tx_date in all_txs:
            months_set.add((tx_date.year, tx_date.month))
        
        # Sắp xếp theo thời gian (mới nhất trước)
        months_list = sorted(months_set, reverse=True)
        
        # Lấy dữ liệu 6 tháng gần nhất
        for year, month in months_list[:6]:
            month_txs = Transaction.objects.filter(user=request.user, date__month=month, date__year=year)
            month_income = int(month_txs.filter(type='income').aggregate(s=Sum('amount'))['s'] or 0)
            month_expense = int(month_txs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or 0)
            
            month_cat_summary = {}
            for tx in month_txs.filter(type='expense').select_related('category'):
                cat = tx.category.name if tx.category else 'Khác'
                month_cat_summary[cat] = month_cat_summary.get(cat, 0) + int(tx.amount)
            
            cat_str = ', '.join([f"{k}: {v:,}đ" for k, v in month_cat_summary.items()]) or 'Chưa có'
            
            all_months_data.append(f"Tháng {month}/{year}: Thu {month_income:,}đ, Chi {month_expense:,}đ, Số dư {month_income - month_expense:,}đ. Chi tiêu: {cat_str}")

    goals_list = ', '.join([f"{g.name} ({int(g.current_amount):,}/{int(g.target_amount):,}đ)" for g in Goal.objects.filter(user=request.user)]) or 'Chưa có'
    current_cat_str = ', '.join([f"{k}: {v:,}đ" for k, v in current_cat_summary.items()]) or 'Chưa có'

    # Context bao gồm cả tháng hiện tại và các tháng trước
    months_context = '\n'.join(all_months_data) if all_months_data else 'Chưa có dữ liệu các tháng trước'
    
    context = f"""Dữ liệu tài chính:

THÁNG HIỆN TẠI ({now.month}/{now.year}):
- Tổng thu: {current_income:,}đ
- Tổng chi: {current_expense:,}đ
- Số dư: {current_income - current_expense:,}đ
- Chi theo danh mục: {current_cat_str}

CÁC THÁNG TRƯỚC (6 tháng gần nhất):
{months_context}

MỤC TIÊU TIẾT KIỆM:
{goals_list}"""

    history = list(
        ChatMessage.objects.filter(user=request.user, session_key=session_key)
        .exclude(pk=user_msg.pk)
        .order_by('-created_at')[:10]
    )
    history.reverse()

    try:
        import groq
        client = groq.Groq(api_key=os.environ.get('GROQ_API_KEY', ''))
        msgs = [{
            'role': 'system',
            'content': (
                'Bạn là trợ lý tài chính cá nhân thông minh cho người Việt Nam. '
                'Chỉ tư vấn về tài chính cá nhân. Trả lời ngắn gọn, thân thiện bằng tiếng Việt.\n'
                f'{context}'
            )
        }]
        for m in history[-8:]:
            msgs.append({'role': m.role, 'content': m.content})
        msgs.append({'role': 'user', 'content': user_message})

        completion = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=msgs,
            max_tokens=512,
        )
        reply = completion.choices[0].message.content
    except Exception:
        reply = 'Xin lỗi, không thể kết nối AI lúc này. Vui lòng thử lại sau.'

    assistant_msg = ChatMessage.objects.create(
        user=request.user,
        session_key=session_key,
        role='assistant',
        content=reply,
    )
    return JsonResponse({
        'reply': reply,
        'id': assistant_msg.id,
        'assistant_time': timezone.localtime(assistant_msg.created_at).strftime('%d/%m/%Y %H:%M'),
        'user_id': user_msg.id,
        'user_time': timezone.localtime(user_msg.created_at).strftime('%d/%m/%Y %H:%M'),
        'session_key': session_key,
        'updated_at': timezone.localtime(assistant_msg.created_at).strftime('%d/%m/%Y %H:%M'),
    })


@login_required
def ai_refresh_suggestions(request):
    if request.method == 'POST':
        _seed_suggestions(request.user)
        messages.success(request, 'Đã làm mới gợi ý thông minh!')
    return redirect('ai')


@login_required
def ai_clear_chat(request):
    if request.method == 'POST':
        messages.success(request, 'Đã bắt đầu cuộc trò chuyện mới.')
    return redirect(f"{reverse('ai')}?new=1")


@login_required
def ai_delete_session(request):
    """Xóa một session chat cụ thể"""
    if request.method == 'POST':
        session_key = request.POST.get('session_key', '').strip()
        if session_key:
            # Xóa tất cả messages của session này
            deleted_count = ChatMessage.objects.filter(
                user=request.user,
                session_key=session_key
            ).delete()[0]
            
            if deleted_count > 0:
                messages.success(request, f'Đã xóa lịch sử chat ({deleted_count} tin nhắn).')
            else:
                messages.warning(request, 'Không tìm thấy lịch sử chat để xóa.')
        else:
            messages.error(request, 'Session không hợp lệ.')
    
    return redirect('ai')


@login_required
def refresh_dashboard_suggestions(request):
    if request.method == 'POST':
        _seed_suggestions(request.user)
        messages.success(request, 'Đã làm mới gợi ý thông minh!')
    return redirect('dashboard')


# ─────────────────────────────── Profile ─────────────────────────────

@login_required
def profile(request):
    profile_form = ProfileForm(instance=request.user)
    password_form = ProfilePasswordForm(user=request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'profile')
        if form_type == 'password':
            password_form = ProfilePasswordForm(request.POST, user=request.user)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Đã đổi mật khẩu thành công!')
                return redirect('profile')
        else:
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Đã cập nhật hồ sơ!')
                return redirect('profile')
        return render(request, 'finance/profile.html', {
            'form': profile_form,
            'password_form': password_form,
        })

    return render(request, 'finance/profile.html', {
        'form': profile_form,
        'password_form': password_form,
    })


# ─────────────────────────────── Helpers ─────────────────────────────

def _seed_suggestions(user):
    """Generate AI suggestions for all months with data"""
    seed_suggestions_all_months(user)


def _seed_suggestions_for_month(user, month, year):
    """Generate AI suggestions for a specific month"""
    from .ai_suggestions import seed_ai_suggestions_for_month
    seed_ai_suggestions_for_month(user, month, year)


# ─────────────────────────────── Video Demo ────────────────────────────────

from django.http import HttpResponse

def video_demo(request):
    """Video demo page: embedded MP4 player + download link."""
    html = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FinSmart - Demo Video</title>
  <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{background:#0f172a;color:#fff;font-family:'Be Vietnam Pro',sans-serif;min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:24px}
    .logo-box{width:56px;height:56px;background:#0d9488;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:800;margin-bottom:16px}
    h1{font-size:2rem;font-weight:800;margin-bottom:6px}
    .subtitle{color:#94e4d4;margin-bottom:28px;font-size:1rem}
    .video-wrap{width:100%;max-width:960px;border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);border:1px solid rgba(255,255,255,0.08)}
    video{width:100%;display:block;background:#000}
    .actions{margin-top:20px;display:flex;gap:14px;flex-wrap:wrap;justify-content:center}
    .btn{display:inline-flex;align-items:center;gap:8px;padding:12px 24px;border-radius:10px;font-weight:600;font-size:0.95rem;text-decoration:none;border:none;cursor:pointer;transition:all .2s}
    .btn-primary{background:#0d9488;color:#fff}
    .btn-primary:hover{background:#0f766e}
    .btn-outline{background:transparent;color:#94e4d4;border:1.5px solid #0d9488}
    .btn-outline:hover{background:#0d948820}
    .info{margin-top:24px;color:#64748b;font-size:0.85rem;text-align:center}
    .badge{display:inline-block;padding:3px 10px;border-radius:6px;background:#1e293b;color:#94e4d4;font-size:0.8rem;margin:3px;border:1px solid #0d948850}
  </style>
</head>
<body>
  <div class="logo-box">F</div>
  <h1>FinSmart — Demo Video</h1>
  <p class="subtitle">Quan ly tai chinh thong minh cho sinh vien</p>

  <div class="video-wrap" style="position:relative">
    <video id="vid" controls muted playsinline loop style="width:100%;display:block;background:#000">
      <source src="/static/finsmart_demo.mp4" type="video/mp4">
    </video>
    <div id="overlay" onclick="playNow()" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,0.45);cursor:pointer;border-radius:0">
      <div style="width:72px;height:72px;background:#0d9488;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 12px rgba(13,148,136,.25)">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="white"><path d="M8 5v14l11-7z"/></svg>
      </div>
    </div>
  </div>

  <div class="actions">
    <a href="/static/finsmart_demo.mp4" download="finsmart_demo.mp4" class="btn btn-primary">
      &#11123; Tai xuong MP4 (0.6 MB)
    </a>
    <a href="/" class="btn btn-outline">
      &#8592; Ve trang chu
    </a>
  </div>

  <script>
    var vid = document.getElementById('vid');
    var overlay = document.getElementById('overlay');
    function playNow() {
      overlay.style.display = 'none';
      vid.play();
    }
    // try autoplay on load
    window.addEventListener('load', function() {
      vid.play().then(function() {
        overlay.style.display = 'none';
      }).catch(function() {
        overlay.style.display = 'flex'; // show play button if blocked
      });
    });
    vid.addEventListener('play', function() { overlay.style.display = 'none'; });
    vid.addEventListener('pause', function() { if(vid.ended) overlay.style.display='flex'; });
  </script>

  <div class="info">
    <p style="margin-bottom:8px">Noi dung demo:</p>
    <span class="badge">Dang nhap</span>
    <span class="badge">Dang ky</span>
    <span class="badge">Dashboard</span>
    <span class="badge">Giao dich</span>
    <span class="badge">Ngan sach</span>
    <span class="badge">Muc tieu</span>
    <span class="badge">AI Tu van</span>
    <span class="badge">Danh muc</span>
    <span class="badge">Ho so</span>
    <span class="badge">Django Admin</span>
  </div>
</body>
</html>"""
    return HttpResponse(html, content_type='text/html; charset=utf-8')
