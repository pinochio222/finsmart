from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from finance.models import UserProfile


class Command(BaseCommand):
    help = 'Create default superuser for Django admin if not exists'

    def handle(self, *args, **options):
        User = get_user_model()
        email = 'admin@finsmart.vn'
        password = 'Admin@FinSmart2026'

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(f'Superuser already exists.')
            return

        User.objects.create_superuser(
            username=email,
            email=email,
            password=password,
            first_name='Admin'
        )

        admin_user = User.objects.get(username=email)
        profile, _ = UserProfile.objects.get_or_create(user=admin_user)
        profile.currency = 'VND'
        profile.avatar_url = 'https://i.pravatar.cc/160?img=5'
        profile.save()

        self.stdout.write(self.style.SUCCESS(
            f'Created superuser: {email} / {password}'
        ))
