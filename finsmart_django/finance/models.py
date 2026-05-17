from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Category(models.Model):
    TYPE_CHOICES = [('income', 'Thu nhập'), ('expense', 'Chi tiêu')]

    name = models.CharField(max_length=100, verbose_name='Tên danh mục')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Loại')
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name='Icon')
    color = models.CharField(max_length=20, blank=True, null=True, verbose_name='Màu sắc')
    is_default = models.BooleanField(default=False, verbose_name='Mặc định')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Người dùng')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def type_display(self):
        return 'Thu nhập' if self.type == 'income' else 'Chi tiêu'


class Transaction(models.Model):
    TYPE_CHOICES = [('income', 'Thu nhập'), ('expense', 'Chi tiêu')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người dùng')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Loại')
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='Số tiền')
    description = models.CharField(max_length=255, verbose_name='Mô tả')
    note = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
    date = models.DateField(verbose_name='Ngày')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Danh mục')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Giao dịch'
        verbose_name_plural = 'Giao dịch'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description} - {self.amount:,}đ"

    @property
    def amount_display(self):
        return f"{int(self.amount):,}đ"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người dùng')
    month = models.IntegerField(verbose_name='Tháng')
    year = models.IntegerField(verbose_name='Năm')
    amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='Ngân sách')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Danh mục')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ngân sách'
        verbose_name_plural = 'Ngân sách'
        ordering = ['-year', '-month']

    def __str__(self):
        cat = self.category.name if self.category else 'Tổng'
        return f"Ngân sách {cat} tháng {self.month}/{self.year}"

    def get_spent(self):
        qs = Transaction.objects.filter(
            user=self.user, type='expense',
            date__month=self.month, date__year=self.year
        )
        if self.category:
            qs = qs.filter(category=self.category)
        from django.db.models import Sum
        result = qs.aggregate(total=Sum('amount'))['total']
        return int(result or 0)

    @property
    def spent(self):
        return self.get_spent()

    @property
    def percentage(self):
        amt = int(self.amount)
        sp = self.spent
        return min(int((sp / amt) * 100), 100) if amt > 0 else 0

    @property
    def status(self):
        pct = self.percentage
        if pct >= 100:
            return 'exceeded'
        elif pct >= 80:
            return 'warning'
        return 'safe'

    @property
    def status_display(self):
        s = self.status
        if s == 'exceeded':
            return 'Đã vượt'
        elif s == 'warning':
            return 'Sắp vượt'
        return 'An toàn'

    @property
    def status_color(self):
        s = self.status
        if s == 'exceeded':
            return 'danger'
        elif s == 'warning':
            return 'warning'
        return 'success'

    @property
    def remaining_budget(self):
        """Còn lại bao nhiêu tiền trong ngân sách (bao gồm dư từ các tháng trước)"""
        # Dư của tháng hiện tại
        current_remaining = max(int(self.amount) - self.spent, 0)
        
        # Cộng dư từ tất cả các tháng trước
        previous_remaining = 0
        
        # Lấy tất cả budget của các tháng trước (cùng danh mục)
        previous_budgets = Budget.objects.filter(
            user=self.user,
            category=self.category
        ).exclude(pk=self.pk)  # Loại trừ budget hiện tại
        
        # Chỉ lấy các tháng trước tháng hiện tại
        for budget in previous_budgets:
            # Tính ngày của budget
            if budget.year < self.year or (budget.year == self.year and budget.month < self.month):
                budget_remaining = max(int(budget.amount) - budget.spent, 0)
                previous_remaining += budget_remaining
        
        return current_remaining + previous_remaining

    @property
    def remaining_budget_current_month(self):
        """Còn lại bao nhiêu tiền trong ngân sách (chỉ tháng này, không tích lũy)"""
        return max(int(self.amount) - self.spent, 0)

    @property
    def daily_budget_remaining(self):
        """Ngân sách còn lại mỗi ngày"""
        from datetime import date
        from calendar import monthrange
        
        today = date.today()
        
        # Tính ngày cuối cùng của tháng
        last_day_of_month = monthrange(today.year, today.month)[1]
        last_date = date(today.year, today.month, last_day_of_month)
        
        # Số ngày còn lại (không tính ngày hôm nay)
        days_left = (last_date - today).days
        
        if days_left <= 0:
            return 0
        
        # Chia đều ngân sách còn lại cho số ngày còn lại
        return self.remaining_budget_current_month // days_left

    @property
    def overspend_by_category(self):
        """Danh mục nào vượt ngân sách"""
        if self.category:
            return []
        
        categories = Category.objects.filter(
            type='expense', 
            user=self.user
        )
        result = []
        for cat in categories:
            cat_budget = Budget.objects.filter(
                user=self.user,
                month=self.month,
                year=self.year,
                category=cat
            ).first()
            if cat_budget and cat_budget.status == 'exceeded':
                result.append({
                    'category': cat.name,
                    'budget': int(cat_budget.amount),
                    'spent': cat_budget.spent,
                    'overspend': cat_budget.spent - int(cat_budget.amount)
                })
        return sorted(result, key=lambda x: x['overspend'], reverse=True)

    @property
    def previous_month_budget(self):
        """Lấy ngân sách tháng trước (so với tháng hiện tại của budget này)"""
        if self.month == 1:
            prev_month, prev_year = 12, self.year - 1
        else:
            prev_month, prev_year = self.month - 1, self.year
        
        return Budget.objects.filter(
            user=self.user,
            month=prev_month,
            year=prev_year,
            category=self.category
        ).first()

    @property
    def budget_variance(self):
        """Chênh lệch ngân sách so với tháng trước (tiền tệ)"""
        prev = self.previous_month_budget
        if not prev:
            return None
        return int(self.amount) - int(prev.amount)

    @property
    def budget_variance_percentage(self):
        """Phần trăm thay đổi ngân sách so với tháng trước"""
        prev = self.previous_month_budget
        if not prev or int(prev.amount) == 0:
            return None
        variance = self.budget_variance
        if variance is None:
            return None
        percentage = round((variance / int(prev.amount)) * 100, 1)
        return percentage

    @property
    def budget_variance_display(self):
        """Hiển thị thay đổi ngân sách (tăng/giảm %)"""
        variance_pct = self.budget_variance_percentage
        if variance_pct is None:
            return "Không có dữ liệu tháng trước"
        
        if variance_pct > 0:
            return f"📈 Tăng {variance_pct}%"
        elif variance_pct < 0:
            return f"📉 Giảm {abs(variance_pct)}%"
        else:
            return "➡️ Không thay đổi"

    @property
    def is_budget_reasonable(self):
        """Ngân sách có hợp lý không (so với chi tiêu thực tế tháng trước)"""
        prev = self.previous_month_budget
        if not prev:
            return None
        prev_spent = prev.spent
        current_budget = int(self.amount)
        # Nếu ngân sách hiện tại < 80% chi tiêu tháng trước, cảnh báo
        if current_budget < prev_spent * 0.8:
            return False
        return True

    @property
    def spending_comparison(self):
        """So sánh chi tiêu tháng này với tháng trước"""
        prev = self.previous_month_budget
        if not prev:
            return None
        
        current_spent = self.spent
        prev_spent = prev.spent
        
        if prev_spent == 0:
            if current_spent > 0:
                return {"change": "Tăng", "amount": current_spent, "percentage": 100}
            else:
                return {"change": "Không thay đổi", "amount": 0, "percentage": 0}
        
        difference = current_spent - prev_spent
        percentage = round((difference / prev_spent) * 100, 1)
        
        if difference > 0:
            return {"change": "Tăng", "amount": difference, "percentage": percentage}
        elif difference < 0:
            return {"change": "Giảm", "amount": abs(difference), "percentage": abs(percentage)}
        else:
            return {"change": "Không thay đổi", "amount": 0, "percentage": 0}


class Goal(models.Model):
    CIRCLE_CIRCUMFERENCE = 251.2

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người dùng')
    name = models.CharField(max_length=200, verbose_name='Tên mục tiêu')
    target_amount = models.DecimalField(max_digits=15, decimal_places=0, verbose_name='Số tiền mục tiêu')
    current_amount = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='Số tiền hiện tại')
    deadline = models.DateField(null=True, blank=True, verbose_name='Hạn chót')
    icon = models.CharField(max_length=50, default='🎯', blank=True, verbose_name='Icon')
    linked_budget = models.ForeignKey('Budget', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Ngân sách liên kết')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mục tiêu tiết kiệm'
        verbose_name_plural = 'Mục tiêu tiết kiệm'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def percentage(self):
        target = int(self.target_amount)
        current = int(self.current_amount)
        return min(int((current / target) * 100), 100) if target > 0 else 0

    @property
    def remaining(self):
        return max(int(self.target_amount) - int(self.current_amount), 0)

    @property
    def monthly_required(self):
        if not self.deadline:
            return None
        from datetime import date
        today = date.today()
        
        # Tính số ngày còn lại
        days_left = (self.deadline - today).days
        
        if days_left <= 0:
            # Đã quá hạn, trả về số tiền còn lại (cần nạp ngay)
            return self.remaining
        
        # Ước tính 30 ngày = 1 tháng
        months_left = days_left / 30.0
        
        # Tính tiền cần tiết kiệm mỗi tháng
        return int(self.remaining / months_left)

    @property
    def circle_progress(self):
        # Convert 0..100 percent to SVG arc length so 100% fills the ring.
        return round((self.CIRCLE_CIRCUMFERENCE * self.percentage) / 100, 1)

    @property
    def circle_offset(self):
        # SVG progress rings render reliably with a fixed dash length and dynamic offset.
        return round(self.CIRCLE_CIRCUMFERENCE * (1 - (self.percentage / 100)), 1)

    @property
    def monthly_savings_from_budget(self):
        """Tính tiết kiệm hàng tháng từ ngân sách liên kết"""
        if not self.linked_budget:
            return 0
        budget_amount = int(self.linked_budget.amount)
        spent = self.linked_budget.spent
        return max(budget_amount - spent, 0)

    @property
    def monthly_savings_from_transactions(self):
        """Tính tiết kiệm hàng tháng từ giao dịch thực tế (Thu nhập - Chi tiêu)"""
        from datetime import date, timedelta
        from django.db.models import Sum
        
        if not self.deadline:
            return 0
        
        today = date.today()
        months = (self.deadline.year - today.year) * 12 + (self.deadline.month - today.month)
        
        if months <= 0:
            return 0
        
        # Tính tiết kiệm từ tháng tạo goal đến hôm nay
        income = Transaction.objects.filter(
            user=self.user,
            type='income',
            date__gte=self.created_at.date()
        ).aggregate(s=Sum('amount'))['s'] or 0
        
        expense = Transaction.objects.filter(
            user=self.user,
            type='expense',
            date__gte=self.created_at.date()
        ).aggregate(s=Sum('amount'))['s'] or 0
        
        total_savings = int(income) - int(expense)
        
        # Tính trung bình tiết kiệm mỗi tháng
        months_passed = (today.year - self.created_at.year) * 12 + (today.month - self.created_at.month)
        months_passed = max(months_passed, 1)  # Ít nhất 1 tháng
        
        return int(total_savings / months_passed)

    @property
    def monthly_savings_actual(self):
        """Tính tiết kiệm thực tế mỗi tháng từ giao dịch"""
        from datetime import date, timedelta
        from django.db.models import Sum
        
        if not self.deadline:
            return 0
        
        today = date.today()
        months = (self.deadline.year - today.year) * 12 + (self.deadline.month - today.month)
        
        if months <= 0:
            return 0
        
        # Tính tiết kiệm từ tháng tạo goal đến hôm nay
        income = Transaction.objects.filter(
            user=self.user,
            type='income',
            date__gte=self.created_at.date()
        ).aggregate(s=Sum('amount'))['s'] or 0
        
        expense = Transaction.objects.filter(
            user=self.user,
            type='expense',
            date__gte=self.created_at.date()
        ).aggregate(s=Sum('amount'))['s'] or 0
        
        total_savings = int(income) - int(expense)
        
        # Tính trung bình tiết kiệm mỗi tháng
        months_passed = (today.year - self.created_at.year) * 12 + (today.month - self.created_at.month)
        months_passed = max(months_passed, 1)  # Ít nhất 1 tháng
        
        return int(total_savings / months_passed)

    @property
    def on_track_for_deadline(self):
        """Kiểm tra có đạt mục tiêu đúng hạn không"""
        if not self.deadline or not self.monthly_required:
            return None
        
        # Dùng monthly_savings_actual thay vì monthly_savings_from_budget
        monthly_actual = self.monthly_savings_actual
        return monthly_actual >= self.monthly_required

    @property
    def required_savings_rate(self):
        """Tỷ lệ tiết kiệm cần thiết để đạt mục tiêu"""
        if not self.deadline or not self.monthly_required:
            return None
        
        from datetime import date, timedelta
        from django.db.models import Sum
        today = date.today()
        three_months_ago = today - timedelta(days=90)
        
        income = Transaction.objects.filter(
            user=self.user,
            type='income',
            date__gte=three_months_ago
        ).aggregate(s=Sum('amount'))['s'] or 0
        
        avg_monthly_income = int(income) / 3 if income > 0 else 1
        
        if avg_monthly_income == 0:
            return None
        
        return round((self.monthly_required / avg_monthly_income) * 100, 1)

    @property
    def is_achievable(self):
        """Mục tiêu có đạt được không (dựa trên tỷ lệ tiết kiệm)"""
        required_rate = self.required_savings_rate
        if required_rate is None:
            return None
        return required_rate <= 50

    @property
    def auto_calculate_current_amount(self):
        """Tính current_amount từ ngân sách liên kết"""
        if not self.linked_budget:
            return 0
        # Trả về số tiền dư của ngân sách liên kết
        return max(int(self.linked_budget.amount) - int(self.linked_budget.spent), 0)

    @property
    def progress_assessment(self):
        """Đánh giá tiến độ: Chậm, Hợp lý, Nhanh"""
        if not self.deadline:
            return None
        
        from datetime import date
        today = date.today()
        
        # Tính số tháng đã trôi qua kể từ khi tạo goal
        months_elapsed = (today.year - self.created_at.year) * 12 + (today.month - self.created_at.month)
        months_elapsed = max(months_elapsed, 1)
        
        # Tính số tháng còn lại đến deadline
        months_remaining = (self.deadline.year - today.year) * 12 + (self.deadline.month - today.month)
        
        if months_remaining <= 0:
            # Hạn chót đã qua
            if self.percentage >= 100:
                return "✅ Hoàn thành"
            else:
                return "❌ Quá hạn"
        
        # Tính tổng số tháng từ lúc tạo goal đến deadline
        total_months = months_elapsed + months_remaining
        
        # Tính tiến độ kỳ vọng (bao nhiêu % nên đạt được)
        expected_progress = (months_elapsed / total_months) * 100 if total_months > 0 else 0
        
        # So sánh tiến độ thực tế với kỳ vọng
        actual_progress = self.percentage
        difference = actual_progress - expected_progress
        
        if difference >= 20:
            return "🚀 Rất nhanh"
        elif difference >= 10:
            return "⚡ Nhanh"
        elif difference >= -10:
            return "✅ Hợp lý"
        elif difference >= -20:
            return "🐢 Chậm"
        else:
            return "🛑 Rất chậm"


class ChatMessage(models.Model):
    ROLE_CHOICES = [('user', 'Người dùng'), ('assistant', 'Trợ lý AI')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người dùng')
    session_key = models.CharField(max_length=40, default='default', db_index=True, verbose_name='Phiên chat')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='Vai trò')
    content = models.TextField(verbose_name='Nội dung')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tin nhắn chat'
        verbose_name_plural = 'Tin nhắn chat'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class AISuggestion(models.Model):
    TYPE_CHOICES = [
        ('spending_alert', 'Cảnh báo chi tiêu'),
        ('saving_tip', 'Mẹo tiết kiệm'),
        ('goal_progress', 'Tiến độ mục tiêu'),
        ('budget_advice', 'Tư vấn ngân sách'),
        ('category_insight', 'Phân tích danh mục'),
        ('anomaly_detect', 'Chi tiêu bất thường'),
        ('income_boost', 'Cải thiện thu nhập'),
        ('smart_saving', 'Tiết kiệm thông minh'),
        ('recurring_expense', 'Chi phí lặp lại'),
        ('budget_optimization', 'Tối ưu hóa ngân sách'),
        ('savings_milestone', 'Kỉ niệm tiết kiệm'),
        ('spending_pattern', 'Mô hình chi tiêu'),
        ('category_trend', 'Xu hướng danh mục'),
    ]
    PRIORITY_CHOICES = [('low', 'Thấp'), ('medium', 'Trung bình'), ('high', 'Cao')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Người dùng')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, verbose_name='Loại')
    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    message = models.TextField(verbose_name='Nội dung')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, verbose_name='Ưu tiên')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Gợi ý AI'
        verbose_name_plural = 'Gợi ý AI'
        ordering = ['-created_at']

    @property
    def priority_color(self):
        return {'low': 'secondary', 'medium': 'warning', 'high': 'danger'}.get(self.priority, 'secondary')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Người dùng')
    avatar_url = models.URLField(blank=True, null=True, verbose_name='Ảnh đại diện (URL)')
    currency = models.CharField(max_length=10, default='VND', verbose_name='Tiền tệ')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Hồ sơ người dùng'
        verbose_name_plural = 'Hồ sơ người dùng'

    def __str__(self):
        return f"{self.user.username} ({self.currency})"


class AdminAccount(User):
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = 'Quản trị viên'
        verbose_name_plural = 'Quản trị viên'
        ordering = ['-date_joined']


class RegularUser(User):
    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'
        ordering = ['-date_joined']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN SYSTEM MODELS - Hệ thống quản lý cho Admin
# ═══════════════════════════════════════════════════════════════════════════

class CategoryMaster(models.Model):
    """Danh mục mẫu - Quản lý bộ danh mục chuẩn cho hệ thống"""
    TYPE_CHOICES = [('income', 'Thu nhập'), ('expense', 'Chi tiêu')]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='Tên danh mục')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name='Loại')
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name='Icon (emoji)')
    color = models.CharField(max_length=20, blank=True, null=True, verbose_name='Màu sắc (hex)')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    is_active = models.BooleanField(default=True, verbose_name='Kích hoạt')
    order = models.IntegerField(default=0, verbose_name='Thứ tự')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Danh mục mẫu'
        verbose_name_plural = 'Danh mục mẫu'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class CurrencyMaster(models.Model):
    """Quản lý tiền tệ - Cấu hình các loại tiền tệ và tỷ giá"""
    code = models.CharField(max_length=3, unique=True, verbose_name='Mã tiền tệ')
    name = models.CharField(max_length=100, verbose_name='Tên tiền tệ')
    symbol = models.CharField(max_length=10, verbose_name='Ký hiệu')
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=4, default=1, verbose_name='Tỷ giá (so với VND)')
    is_active = models.BooleanField(default=True, verbose_name='Kích hoạt')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tiền tệ'
        verbose_name_plural = 'Tiền tệ'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class AITrainingData(models.Model):
    """Dữ liệu huấn luyện AI - Nơi Admin nạp kiến thức cho AI"""
    CATEGORY_CHOICES = [
        ('finance_tips', 'Mẹo tài chính'),
        ('tax_rules', 'Quy định thuế'),
        ('saving_strategies', 'Chiến lược tiết kiệm'),
        ('investment_guide', 'Hướng dẫn đầu tư'),
        ('budget_tips', 'Mẹo lập ngân sách'),
        ('other', 'Khác'),
    ]
    
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, verbose_name='Danh mục')
    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    content = models.TextField(verbose_name='Nội dung')
    keywords = models.CharField(max_length=500, blank=True, null=True, verbose_name='Từ khóa (cách nhau bằng dấu phẩy)')
    is_active = models.BooleanField(default=True, verbose_name='Kích hoạt')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dữ liệu huấn luyện AI'
        verbose_name_plural = 'Dữ liệu huấn luyện AI'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class AIPromptConfig(models.Model):
    """Cấu hình Prompt AI - Điều chỉnh tính cách của AI"""
    TONE_CHOICES = [
        ('strict', 'Khắt khe'),
        ('balanced', 'Cân bằng'),
        ('encouraging', 'Động viên'),
        ('friendly', 'Thân thiện'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name='Tên cấu hình')
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='balanced', verbose_name='Tính cách')
    system_prompt = models.TextField(verbose_name='System Prompt')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    is_active = models.BooleanField(default=False, verbose_name='Kích hoạt')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cấu hình Prompt AI'
        verbose_name_plural = 'Cấu hình Prompt AI'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.tone})"


class AIConversationMonitor(models.Model):
    """Giám sát hội thoại AI - Xem câu hỏi phổ biến của User"""
    question = models.TextField(verbose_name='Câu hỏi')
    question_count = models.IntegerField(default=1, verbose_name='Số lần hỏi')
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name='Danh mục')
    is_flagged = models.BooleanField(default=False, verbose_name='Đánh dấu')
    notes = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Giám sát hội thoại AI'
        verbose_name_plural = 'Giám sát hội thoại AI'
        ordering = ['-question_count']
    
    def __str__(self):
        return self.question[:100]


class BudgetAlertThreshold(models.Model):
    """Quản lý định mức cảnh báo - Thiết lập ngưỡng thông báo"""
    name = models.CharField(max_length=100, verbose_name='Tên định mức')
    threshold_percentage = models.IntegerField(default=80, verbose_name='Ngưỡng (%)')
    alert_type = models.CharField(max_length=50, verbose_name='Loại cảnh báo')
    description = models.TextField(blank=True, null=True, verbose_name='Mô tả')
    is_active = models.BooleanField(default=True, verbose_name='Kích hoạt')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Định mức cảnh báo'
        verbose_name_plural = 'Định mức cảnh báo'
        ordering = ['threshold_percentage']
    
    def __str__(self):
        return f"{self.name} ({self.threshold_percentage}%)"


class UserAnalytics(models.Model):
    """Báo cáo xu hướng - Thống kê tổng quát về người dùng"""
    date = models.DateField(auto_now_add=True, verbose_name='Ngày')
    total_users = models.IntegerField(default=0, verbose_name='Tổng người dùng')
    active_users = models.IntegerField(default=0, verbose_name='Người dùng hoạt động')
    total_transactions = models.IntegerField(default=0, verbose_name='Tổng giao dịch')
    total_income = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='Tổng thu nhập')
    total_expense = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='Tổng chi tiêu')
    avg_budget_per_user = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name='Ngân sách trung bình/người')
    popular_categories = models.TextField(blank=True, null=True, verbose_name='Danh mục phổ biến')
    notes = models.TextField(blank=True, null=True, verbose_name='Ghi chú')
    
    class Meta:
        verbose_name = 'Phân tích người dùng'
        verbose_name_plural = 'Phân tích người dùng'
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics - {self.date}"


class UserAccountStatus(models.Model):
    """Quản lý trạng thái tài khoản - Khóa/Mở khóa tài khoản"""
    STATUS_CHOICES = [
        ('active', 'Hoạt động'),
        ('suspended', 'Tạm khóa'),
        ('banned', 'Cấm'),
        ('inactive', 'Không hoạt động'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_status', verbose_name='Người dùng')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Trạng thái')
    reason = models.TextField(blank=True, null=True, verbose_name='Lý do')
    suspended_until = models.DateTimeField(blank=True, null=True, verbose_name='Tạm khóa đến')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Trạng thái tài khoản'
        verbose_name_plural = 'Trạng thái tài khoản'
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"


class AuditLog(models.Model):
    """Nhật ký hoạt động - Theo dõi các thay đổi quan trọng"""
    ACTION_CHOICES = [
        ('create', 'Tạo'),
        ('update', 'Cập nhật'),
        ('delete', 'Xóa'),
        ('login', 'Đăng nhập'),
        ('logout', 'Đăng xuất'),
        ('export', 'Xuất dữ liệu'),
        ('import', 'Nhập dữ liệu'),
        ('other', 'Khác'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Người dùng')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='Hành động')
    model_name = models.CharField(max_length=100, verbose_name='Model')
    object_id = models.IntegerField(blank=True, null=True, verbose_name='ID đối tượng')
    description = models.TextField(verbose_name='Mô tả')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='Địa chỉ IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Nhật ký hoạt động'
        verbose_name_plural = 'Nhật ký hoạt động'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.model_name} ({self.created_at})"
