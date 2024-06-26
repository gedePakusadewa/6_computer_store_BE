# Generated by Django 4.2 on 2024-04-09 05:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computer_store', '0003_auto_20240409_1303'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DROP PROCEDURE IF EXISTS cart_get_all_by_user_id;
            CREATE PROCEDURE cart_get_all_by_user_id(user_id int)
            BEGIN
                SELECT
                    p.id,
                    p.name, 
                    p.image_url,
                    p.price,
                    c.total_order 
                FROM computer_store_productmodel AS p 
                INNER JOIN computer_store_cartmodel AS c ON p.id = c.product_id
                WHERE c.user_id = user_id;
            END
            """
        )
    ]
