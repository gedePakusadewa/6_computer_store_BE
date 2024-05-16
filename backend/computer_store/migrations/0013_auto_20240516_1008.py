# Generated by Django 4.2 on 2024-05-16 02:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computer_store', '0012_auto_20240514_1205'),
    ]

    operations = [
        migrations.RunSQL(
            """
                DROP PROCEDURE IF EXISTS cart_get_all_by_user_id;
                CREATE PROCEDURE cart_get_all_by_user_id(user_id int)
                BEGIN
                    SELECT
                        p.id AS 'id_product',
                        p.name, 
                        p.image_url,
                        p.price,
                        c.total_order,
                        c.id AS 'id_cart'
                    FROM computer_store_productmodel AS p 
                    INNER JOIN computer_store_cartmodel AS c ON p.id = c.product_id
                    WHERE c.user_id = user_id;
                END
            """
        )
    ]
