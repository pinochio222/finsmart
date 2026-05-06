from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random

from finance.models import UserProfile


class Command(BaseCommand):
    help = 'Create a test user for demo purposes'

    def handle(self, *args, **options):
        User = get_user_model()

        email = 'test@finsmart.vn'
        password = 'Test123456'

        if User.objects.filter(username=email).exists():
            self.stdout.write(f'Test user already exists: {email}')
            return

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name='Nguyễn',
            last_name='Test',
        )

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.currency = 'VND'
        profile.avatar_url = 'https://i.pravatar.cc/160?img=12'
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f'Created test user: {email} / {password}'
        ))

        try:
            from finance.models import Category, Transaction, Budget, Goal
            from datetime import date, timedelta

            income_cats = list(Category.objects.filter(type='income')[:3])
            expense_cats = list(Category.objects.filter(type='expense')[:6])
            today = date.today()

            for i in range(20):
                is_income = random.random() < 0.3
                cat = random.choice(income_cats) if is_income and income_cats else random.choice(expense_cats) if expense_cats else None
                if not cat:
                    continue
                Transaction.objects.create(
                    user=user,
                    category=cat,
                    amount=Decimal(random.randint(50, 2000) * 1000),
                    type=cat.type,
                    description=f'Giao dịch mẫu {i+1}',
                    date=today - timedelta(days=random.randint(0, 29)),
                )

            if expense_cats:
                for cat in expense_cats[:3]:
                    Budget.objects.create(
                        user=user,
                        category=cat,
                        amount=Decimal(random.randint(1, 5) * 1000000),
                        month=today.month,
                        year=today.year,
                    )

            Goal.objects.create(
                user=user,
                name='Quỹ dự phòng',
                target_amount=Decimal(10000000),
                current_amount=Decimal(2500000),
                deadline=date(today.year + 1, 12, 31),
            )

            self.stdout.write(self.style.SUCCESS('Sample data created for test user'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not create sample data: {e}'))
