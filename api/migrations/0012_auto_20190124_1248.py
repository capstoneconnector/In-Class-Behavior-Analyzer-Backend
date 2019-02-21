# Generated by Django 2.1.5 on 2019-01-24 17:48

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20190124_1237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='reset_code_expiration',
        ),
        migrations.AlterField(
            model_name='position',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c9d994ea-8297-43db-8f8c-0827a75d5841'), editable=False, primary_key=True, serialize=False),
        ),
    ]