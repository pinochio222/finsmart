from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Category, AISuggestion,
    ChatMessage, AdminAccount, RegularUser
)
from django.db.models import Count, Sum
from datetime import date

try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.site_header = "FinSmart Admin"
admin.site.site_title = "FinSmart"
admin.site.index_title = "Bảng Điều Khiển Quản Trị"


# ═══════════════════════════════════════════════════════════════════════════
# BASE ADMIN CLASSES
# ═══════════════════════════════════════════════════════════════════════════

class BaseSeparatedUserAdmin(UserAdmin):
    ordering = ['-date_joined']
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'last_login', 'get_user_stats']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['date_joined', 'last_login', 'get_detailed_stats']
    
    def get_user_stats(self, obj):
        """Display user statistics"""
        return "Người dùng"
    get_user_stats.short_description = "Thống Kê"
    
    def get_detailed_stats(self, obj):
        """Display detailed statistics"""
        chat_count = ChatMessage.objects.filter(user=obj).count()
        
        stats = f"""
        <h3>📊 Thống Kê Chi Tiết</h3>
        <ul>
            <li><strong>Tin nhắn chat:</strong> {chat_count}</li>
        </ul>
        """
        return stats
    get_detailed_stats.short_description = "Thống Kê Chi Tiết"


@admin.register(AdminAccount)
class AdminAccountAdmin(BaseSeparatedUserAdmin):
    list_display = BaseSeparatedUserAdmin.list_display + ['is_superuser']
    list_filter = ['is_active', 'is_superuser', 'date_joined', 'last_login']
    list_per_page = 20  # Phân trang: 20 tài khoản mỗi trang

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=True)

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        super().save_model(request, obj, form, change)


@admin.register(RegularUser)
class RegularUserAdmin(BaseSeparatedUserAdmin):
    list_filter = ['is_active', 'date_joined', 'last_login']
    list_per_page = 20  # Phân trang: 20 người dùng mỗi trang
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Thông tin cá nhân', {'fields': ('first_name', 'last_name', 'email')}),
        ('Trạng thái', {'fields': ('is_active',)}),
        ('Mốc thời gian', {'fields': ('last_login', 'date_joined')}),
        ('Thống kê', {'fields': ('get_detailed_stats',), 'classes': ('collapse',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_staff=False)

    def save_model(self, request, obj, form, change):
        obj.is_staff = False
        obj.is_superuser = False
        super().save_model(request, obj, form, change)


# ═══════════════════════════════════════════════════════════════════════════
# HIDDEN MODELS - ChatMessage và AISuggestion đã được ẩn khỏi admin panel
# ═══════════════════════════════════════════════════════════════════════════

# @admin.register(ChatMessage)
# class ChatMessageAdmin(admin.ModelAdmin):
#     list_display = ['user', 'role', 'get_content_preview', 'session_key', 'created_at']
#     list_filter = ['role', 'created_at', 'user']
#     search_fields = ['user__username', 'content', 'session_key']
#     readonly_fields = ['created_at', 'user', 'role', 'content', 'session_key']
#     list_per_page = 20  # Phân trang: 20 tin nhắn mỗi trang
#     
#     def get_content_preview(self, obj):
#         """Display content preview"""
#         preview = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
#         return preview
#     get_content_preview.short_description = "Nội Dung"
#     
#     def has_add_permission(self, request):
#         return False
#     
#     def has_delete_permission(self, request, obj=None):
#         return False
#     
#     def has_change_permission(self, request, obj=None):
#         return False


# ═══════════════════════════════════════════════════════════════════════════
# DANH MỤC BAN ĐẦU
# ═══════════════════════════════════════════════════════════════════════════

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'is_default']
    list_filter = ['type', 'is_default', 'created_at']
    search_fields = ['name', 'user__username']
    list_editable = ['is_default']
    list_per_page = 20  # Phân trang: 20 danh mục mỗi trang
    
    def save_model(self, request, obj, form, change):
        # Nếu tạo danh mục mới từ admin (không có user), đặt is_default=True
        if not change and not obj.user:
            obj.is_default = True
        super().save_model(request, obj, form, change)


# @admin.register(AISuggestion)
# class AISuggestionAdmin(admin.ModelAdmin):
#     list_display = ['user', 'type', 'priority_color', 'created_at']
#     list_filter = ['type', 'created_at']
#     search_fields = ['user__username', 'content']
#     readonly_fields = ['created_at']
#     list_per_page = 20  # Phân trang: 20 gợi ý mỗi trang
