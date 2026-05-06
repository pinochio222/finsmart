from django.core.management.base import BaseCommand
from finance.models import Goal


class Command(BaseCommand):
    help = 'Fix goal icons - set default icon for goals with None icon'

    def handle(self, *args, **options):
        # Update all goals with None icon to default icon
        updated = Goal.objects.filter(icon__isnull=True).update(icon='🎯')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated} goals with default icon 🎯')
        )
