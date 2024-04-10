# Generated by Django 4.2 on 2024-04-10 02:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computer_store', '0004_auto_20240409_1319'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DROP PROCEDURE IF EXISTS product_get_product_by_search;
            CREATE PROCEDURE product_get_product_by_search(keywords varchar(100))
            BEGIN
                SELECT
                    *
                FROM 
                    computer_store_productmodel
                WHERE
                    name LIKE CONCAT('%', keywords, '%');
            END 
            """
        )
    ]
