# Generated by Django 5.0.3 on 2024-03-10 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_rename_admin_user_id_product_admin_user'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddConstraint(
            model_name='cartitem',
            constraint=models.UniqueConstraint(fields=('product_id', 'cart_id'), name='unique-cart-product'),
        ),
    ]
