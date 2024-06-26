# Generated by Django 4.2 on 2024-05-06 02:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('computer_store', '0007_auto_20240429_1357'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchasingDetailModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('price', models.IntegerField()),
                ('total_price', models.IntegerField()),
                ('created_date', models.DateField()),
                ('modified_date', models.DateField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='computer_store.productmodel')),
            ],
        ),
        migrations.CreateModel(
            name='PurchasingModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_date', models.DateField()),
                ('modified_date', models.DateField()),
                ('purchasing_detail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='computer_store.purchasingdetailmodel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
