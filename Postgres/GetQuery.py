import traceback
from   datetime import datetime
from   Postgres.Connect import connect
import decimal

debug = False;

def queryDecorator(func):
    def wrapper(*args, **kwargs):
        results = func(*args, **kwargs);
        if (results is None) or len(results) == 0: return [];
        returnArray = [];
        # zip the columns and values together
        for value in results.get('results', []):
            updateObj = {};
            obj = dict(zip(results.get('columns', []), value));
            for key,value in obj.items():
                if isinstance(value, decimal.Decimal):
                    updateObj[key] = float(value);
                else: updateObj[key] = value;

            returnArray.append(updateObj);
        return returnArray;
    return wrapper;

@queryDecorator
def getQuery(useQuery = """ """, useValues = []):
    connection = connect(); 
    if (connection is None): 
        print('Unable to connect to the database');
    if (len(useQuery)  == 0): return;
    try: 
        cursor = connection.cursor();
        useQuery = useQuery.replace("$", "%s") + ';'

        for value in useValues:
            if (isinstance(value, datetime)):
                useQuery = useQuery.replace("%s", "'{}'".format(value.strftime('%Y-%m-%d %H:%M:%S')), 1);
            elif (isinstance(value, int)) or (isinstance(value, float)):
                useQuery = useQuery.replace("%s", "{}".format(value), 1);
            else: 
                useQuery = useQuery.replace("%s", "'{}'".format(value), 1);

        cursor.execute(useQuery);
        if debug: print(cursor.mogrify(useQuery, useValues));
        if cursor.arraysize == 0: return [];
        # Check if query returned results
        results  = cursor.fetchall();
        if (results is None) or len(results) == 0: return [];
        colnames = [desc[0] for desc in cursor.description];
        connection.commit();
        cursor.close();
        return {
            "results": results,
            "columns": colnames
        }
    except Exception as error: 
        print(error)
        traceback.print_exc()