from django.db import connection

#TODO:
    #find a new structure to place db helper
    #search what is connection, connection.cursor, cursor.execute, cursor.fetahcall()
    #is there alternative to this?
class DB_helper():
    def function_get_all(self, function_name):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM "+ function_name +";")
            row = cursor.fetchall()

        return row
    
    def store_procedure(self, sp_name):
        with connection.cursor() as cursor:
            cursor.execute("CALL "+ sp_name +";")
            row = cursor.fetchall()

        return row