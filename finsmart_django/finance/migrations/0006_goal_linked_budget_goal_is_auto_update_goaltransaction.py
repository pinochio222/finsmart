# Generated migration for Goal-Budget-Transaction linking

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_alter_aisuggestion_type'),
    ]

    operations = [
        # Add linked_budget field to Goal
        migrations.AddField(
            model_name='goal',
            name='linked_budget',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='finance.budget', verbose_name='Ngân sách liên kết'),
        ),
        # Add is_auto_update field to Goal
        migrations.AddField(
            model_name='goal',
            name='is_auto_update',
            field=models.BooleanField(default=False, verbose_name='Tự động cập nhật từ giao dịch'),
        ),
        # Create GoalTransaction model
        migrations.CreateModel(
            name='GoalTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=0, max_digits=15, verbose_name='Số tiền góp vào')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='finance.goal', verbose_name='Mục tiêu')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goal_links', to='finance.transaction', verbose_name='Giao dịch')),
            ],
            options={
                'verbose_name': 'Giao dịch mục tiêu',
                'verbose_name_plural': 'Giao dịch mục tiêu',
                'ordering': ['-created_at'],
            },
        ),
        # Add unique constraint
        migrations.AddConstraint(
            model_name='goaltransaction',
            constraint=models.UniqueConstraint(fields=('goal', 'transaction'), name='unique_goal_transaction'),
        ),
    ]
