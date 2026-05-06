# Generated migration to remove auto_update feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0007_aiconversationmonitor_aipromptconfig_aitrainingdata_and_more'),
    ]

    operations = [
        # Delete GoalTransaction model
        migrations.DeleteModel(
            name='GoalTransaction',
        ),
        # Remove is_auto_update field from Goal
        migrations.RemoveField(
            model_name='goal',
            name='is_auto_update',
        ),
    ]
