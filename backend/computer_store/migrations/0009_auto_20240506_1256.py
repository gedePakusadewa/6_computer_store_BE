# Generated by Django 4.2 on 2024-05-06 04:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('computer_store', '0008_purchasingdetailmodel_purchasingmodel'),
    ]

    operations = [
        migrations.RunSQL(
            """
                DROP PROCEDURE IF EXISTS profile_delete_user_by_user_id;
                CREATE PROCEDURE cart_delete_by_user_id(id int)
                BEGIN
                    DELETE FROM computer_store_cartmodel WHERE user_id = id;    
                END
            """
        )
    ]