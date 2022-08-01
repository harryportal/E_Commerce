# Generated by Django 4.0.5 on 2022-08-01 17:02

from django.db import migrations, models
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_productimage_image_alter_productimage_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='paystack_order_reference',
            field=models.CharField(default=store.models.generate_random_transaction_reference, max_length=25),
        ),
    ]