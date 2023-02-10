from Postgres.Connect import connect
from psycopg2.extras import execute_values
import json
import traceback

debug = False


def toColumns(array, output='columns'):
    if array is None or len(array) == 0:
        return []
    useColumns = [json.dumps(string) for string in array]
    columns = ''
    if output == 'columns':
        for idx, elem in enumerate(useColumns):
            useString = elem.replace("'", ' ')
            if (idx < len(useColumns) - 1):
                columns += useString + ','
            else:
                columns += useString

        return columns

    elif output == 'conflict':
        for idx, elem in enumerate(useColumns):
            if (idx < len(useColumns) - 1):
                columns += elem + " = EXCLUDED." + elem + ","
            else:
                columns += elem + " = EXCLUDED." + elem

        return columns


def insertQuery(useSchema, useColumns=[], useValues=[]):
    if len(useColumns) == 0 or len(useValues) == 0:
        return
    connection = connect()
    try:
        cursor = connection.cursor()
        useColumnStatement = toColumns(useColumns, 'columns')
        useConflictStatement = toColumns(useColumns, 'conflict')
        cursor.execute(
            "select column_name from INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE where table_name = '{0}'".format(useSchema))
        usePrimaryKeys = cursor.fetchall()

        if usePrimaryKeys is None or len(usePrimaryKeys) == 0:
            print("No Primary Keys Found")
            return

        # convert list of tuples to list of strings
        usePrimaryKeys = toColumns([string[0]
                                   for string in usePrimaryKeys], 'columns')
        # Use Query
        useQuery = """INSERT INTO {0} ({1}) VALUES %s ON CONFLICT ({2}) DO UPDATE SET {3}
        """.format(useSchema, useColumnStatement, usePrimaryKeys, useConflictStatement)

        if debug:
            print(useQuery)
        # Execute Query
        execute_values(cursor, useQuery, useValues,
                       template=None, page_size=100)
        connection.commit()
        cursor.close()

    except Exception as error:
        print(error)
        traceback.print_exc()

    finally:
        connection.close()


def updateQuery(useSchema, useColumns=[], useValues=[], key = "productSKU"):
    connection = connect()
    try:
        cursor = connection.cursor();
        useColumnStatement = toColumns(useColumns, 'columns');
        for row in useValues:
            [ image, productSKU ] = row; 
            useQuery = """UPDATE {0} SET {1} = '{2}' WHERE "{3}" = '{4}'""".format(useSchema, useColumnStatement, image,key,productSKU);
            cursor.execute(useQuery);
            cursor.mogrify(useQuery)
        connection.commit()
        cursor.close()

    except Exception as error:
        print(error)
        traceback.print_exc()

    finally:
        connection.close()
