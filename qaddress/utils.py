from django.db import connection

def truncate_tables():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM "qaddress_districtdata"')
        cursor.execute('DELETE FROM "qaddress_countydata"')
        cursor.execute('DELETE FROM "qaddress_cpdata"')
