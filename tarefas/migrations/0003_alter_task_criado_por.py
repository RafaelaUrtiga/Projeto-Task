# Generated by Django 5.0.4 on 2024-05-27 19:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tarefas', '0002_task_atualizado_em_task_criado_em_task_criado_por_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='criado_por',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks_criadas', to=settings.AUTH_USER_MODEL),
        ),
    ]
