from django.core.management.base import BaseCommand
from finance.models import Category


DEFAULT_CATEGORIES = [
    {'name': 'Lương', 'type': 'income', 'color': '#16a34a'},
    {'name': 'Thưởng', 'type': 'income', 'color': '#15803d'},
    {'name': 'Kinh doanh', 'type': 'income', 'color': '#166534'},
    {'name': 'Đầu tư', 'type': 'income', 'color': '#14532d'},
    {'name': 'Thu nhập khác', 'type': 'income', 'color': '#22c55e'},
    {'name': 'Tiết kiệm', 'type': 'income', 'color': '#86efac'},
    {'name': 'Ăn uống', 'type': 'expense', 'color': '#f97316'},
    {'name': 'Di chuyển', 'type': 'expense', 'color': '#3b82f6'},
    {'name': 'Nhà ở', 'type': 'expense', 'color': '#8b5cf6'},
    {'name': 'Giải trí', 'type': 'expense', 'color': '#ec4899'},
    {'name': 'Y tế', 'type': 'expense', 'color': '#ef4444'},
    {'name': 'Học tập', 'type': 'expense', 'color': '#06b6d4'},
    {'name': 'Quần áo', 'type': 'expense', 'color': '#f59e0b'},
    {'name': 'Điện thoại', 'type': 'expense', 'color': '#6366f1'},
    {'name': 'Mua sắm', 'type': 'expense', 'color': '#d946ef'},
    {'name': 'Chi tiêu khác', 'type': 'expense', 'color': '#6b7280'},
]


class Command(BaseCommand):
    help = 'Seed default categories'

    def handle(self, *args, **options):
        created = 0
        for cat_data in DEFAULT_CATEGORIES:
            _, is_new = Category.objects.get_or_create(
                name=cat_data['name'],
                is_default=True,
                defaults={
                    'type': cat_data['type'],
                    'color': cat_data['color'],
                    'is_default': True,
                    'user': None,
                }
            )
            if is_new:
                created += 1
        self.stdout.write(
            self.style.SUCCESS(f'Seeded {created} new default categories (total: {Category.objects.filter(is_default=True).count()})')
        )
