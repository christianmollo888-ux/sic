import psycopg2
import json
import datetime

DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

def default_serializer(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return str(obj)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

result = {}
tables = ['CN_GLOSA', 'CN_TRANS']
for table in tables:
    cur.execute(f'SELECT * FROM "{table}" LIMIT 1')
    cols = [d[0] for d in cur.description]
    row = cur.fetchone()
    if row:
        row_dict = dict(zip(cols, row))
    else:
        row_dict = {}
    result[table] = {
        "columns": cols,
        "sample": row_dict
    }

with open("c:/sicjac/db_info.json", "w") as f:
    json.dump(result, f, indent=2, default=default_serializer)

print("DONE")
