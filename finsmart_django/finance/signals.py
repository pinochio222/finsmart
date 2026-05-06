from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category


@receiver(post_save, sender=Category)
def sync_category_to_admin(sender, instance, created, **kwargs):
    """
    Khi user tạo/sửa danh mục, tự động cập nhật ở admin
    - Nếu user tạo danh mục mới, cũng tạo bản sao với is_default=True
    - Nếu user sửa danh mục, cũng cập nhật bản sao admin
    """
    if instance.user:  # Chỉ xử lý danh mục của user
        # Tìm danh mục admin tương ứng (cùng tên, loại, không có user)
        admin_category = Category.objects.filter(
            name=instance.name,
            type=instance.type,
            user__isnull=True,
            is_default=True
        ).first()
        
        if created:
            # Nếu danh mục user mới được tạo, tạo bản sao ở admin
            if not admin_category:
                Category.objects.create(
                    name=instance.name,
                    type=instance.type,
                    icon=instance.icon,
                    color=instance.color,
                    is_default=True,
                    user=None
                )
        else:
            # Nếu danh mục user được sửa, cập nhật bản sao ở admin
            if admin_category:
                admin_category.icon = instance.icon
                admin_category.color = instance.color
                admin_category.save()


@receiver(post_save, sender=Category)
def sync_admin_category_to_users(sender, instance, created, **kwargs):
    """
    Khi admin tạo/sửa danh mục mặc định, tự động cập nhật ở user
    - Nếu admin tạo danh mục mặc định, cũng tạo bản sao cho tất cả user
    - Nếu admin sửa danh mục mặc định, cũng cập nhật bản sao user
    """
    if not instance.user and instance.is_default:  # Chỉ xử lý danh mục admin mặc định
        from django.contrib.auth.models import User
        
        if created:
            # Nếu admin tạo danh mục mặc định mới, tạo bản sao cho tất cả user
            all_users = User.objects.filter(is_staff=False)
            for user in all_users:
                user_category = Category.objects.filter(
                    name=instance.name,
                    type=instance.type,
                    user=user
                ).first()
                
                if not user_category:
                    Category.objects.create(
                        name=instance.name,
                        type=instance.type,
                        icon=instance.icon,
                        color=instance.color,
                        is_default=False,
                        user=user
                    )
        else:
            # Nếu admin sửa danh mục mặc định, cập nhật bản sao user
            user_categories = Category.objects.filter(
                name=instance.name,
                type=instance.type,
                user__isnull=False
            )
            
            for user_cat in user_categories:
                user_cat.icon = instance.icon
                user_cat.color = instance.color
                user_cat.save(update_fields=['icon', 'color'])


@receiver(post_delete, sender=Category)
def sync_category_delete(sender, instance, **kwargs):
    """
    Khi xóa danh mục, xóa bản sao tương ứng
    """
    if instance.user:
        # Nếu xóa danh mục user, xóa bản sao admin
        Category.objects.filter(
            name=instance.name,
            type=instance.type,
            user__isnull=True,
            is_default=True
        ).delete()
    elif instance.is_default:
        # Nếu xóa danh mục admin mặc định, xóa bản sao user
        Category.objects.filter(
            name=instance.name,
            type=instance.type,
            user__isnull=False
        ).delete()
