#!/usr/bin/env python
"""Tạo dữ liệu test để kiểm tra các liên kết"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finsmart.settings')
django.setup()

from finance.models import Goal, Budget, Transaction, Category
from django.contrib.auth.models import User
from datetime import date

print("=" * 60)
print("TẠO DỮ LIỆU TEST")
print("=" * 60)

# Lấy hoặc tạo user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
print(f"\n✅ User: {user.username} ({'tạo mới' if created else 'đã tồn tại'})")

# Tạo categories
cat_expense, _ = Category.objects.get_or_create(
    name='Ăn uống',
    type='expense',
    user=user,
    defaults={'color': '#FF6B6B', 'icon': '🍔'}
)
print(f"✅ Category: {cat_expense.name}")

cat_savings, _ = Category.objects.get_or_create(
    name='Tiết kiệm',
    type='income',
    user=user,
    defaults={'color': '#51CF66', 'icon': '💰'}
)
print(f"✅ Category: {cat_savings.name}")

# Tạo budget
budget, created = Budget.objects.get_or_create(
    user=user,
    month=4,
    year=2026,
    category=cat_expense,
    defaults={'amount': 2000000}
)
print(f"\n✅ Budget: {budget} ({'tạo mới' if created else 'đã tồn tại'})")

# Tạo goal liên kết với budget
goal, created = Goal.objects.get_or_create(
    user=user,
    name='Tiết kiệm 10 triệu',
    defaults={
        'target_amount': 10000000,
        'deadline': date(2026, 10, 12),
        'linked_budget': budget,
        'icon': '🎯'
    }
)
print(f"✅ Goal: {goal.name} ({'tạo mới' if created else 'đã tồn tại'})")
print(f"   - linked_budget: {goal.linked_budget}")

# Tạo giao dịch chi tiêu
tx_expense, created = Transaction.objects.get_or_create(
    user=user,
    description='Ăn trưa',
    date=date.today(),
    defaults={
        'type': 'expense',
        'amount': 150000,
        'category': cat_expense
    }
)
print(f"\n✅ Transaction (chi tiêu): {tx_expense.description} - {tx_expense.amount:,}đ ({'tạo mới' if created else 'đã tồn tại'})")

# Tạo giao dịch tiết kiệm
tx_savings, created = Transaction.objects.get_or_create(
    user=user,
    description='Tiết kiệm tháng 4',
    date=date.today(),
    defaults={
        'type': 'income',
        'amount': 1500000,
        'category': cat_savings
    }
)
print(f"✅ Transaction (tiết kiệm): {tx_savings.description} - {tx_savings.amount:,}đ ({'tạo mới' if created else 'đã tồn tại'})")

# Test các tính năng
print("\n" + "=" * 60)
print("TEST CÁC TÍNH NĂNG")
print("=" * 60)

# Refresh từ database
goal.refresh_from_db()
budget.refresh_from_db()

print(f"\n📊 BUDGET ANALYSIS:")
print(f"   - Ngân sách: {budget.amount:,}đ")
print(f"   - Chi tiêu: {budget.spent:,}đ")
print(f"   - Còn lại: {budget.remaining_budget:,}đ")
print(f"   - Mỗi ngày: {budget.daily_budget_remaining:,}đ")
print(f"   - Trạng thái: {budget.status_display}")
print(f"   - % sử dụng: {budget.percentage}%")

print(f"\n🎯 GOAL ANALYSIS:")
print(f"   - Mục tiêu: {goal.target_amount:,}đ")
print(f"   - Tiến độ: {goal.current_amount:,}đ ({goal.percentage}%)")
print(f"   - Deadline: {goal.deadline}")
print(f"   - Tiết kiệm cần/tháng: {goal.monthly_required:,}đ")
print(f"   - Tiết kiệm từ budget: {goal.monthly_savings_from_budget:,}đ")
print(f"   - Đạt tiến độ: {'✅ Có' if goal.on_track_for_deadline else '❌ Không'}")
print(f"   - Tỷ lệ tiết kiệm cần: {goal.required_savings_rate}%")
print(f"   - Khả thi: {'✅ Có' if goal.is_achievable else '❌ Không'}")

print("\n" + "=" * 60)
print("✅ TẠO DỮ LIỆU TEST HOÀN THÀNH!")
print("=" * 60)
