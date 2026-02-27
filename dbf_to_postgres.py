import os
import psycopg2
from dbfread import DBF
from psycopg2 import sql

# Connection parameters
DB_CONFIG = {
    "host": "localhost",
    "database": "sicjac",
    "port": "5435",
    "user": "postgres",
    "password": "P4$$w0rd.2025"
}

DBF_DIR = r"C:\sicjac\dbf"

def map_dbf_type_to_pg(field):
    """Maps DBF field types to PostgreSQL data types."""
    field_type = field.type.upper()
    if field_type == 'C':  # Character
        return f"VARCHAR({field.length})"
    elif field_type == 'N':  # Numeric
        if getattr(field, 'decimal_count', 0) > 0:
            return f"DECIMAL({field.length}, {field.decimal_count})"
        else:
            return "INTEGER" if field.length < 10 else "BIGINT"
    elif field_type == 'D':  # Date
        return "DATE"
    elif field_type == 'L':  # Logical
        return "BOOLEAN"
    elif field_type == 'M':  # Memo
        return "TEXT"
    else:
        return "TEXT"

def migrate_dbf_to_pg():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
        print("Connected to PostgreSQL successfully.")

        # Get list of DBF files
        files = [f for f in os.listdir(DBF_DIR) if f.lower().endswith('.dbf')]
        if not files:
            print(f"No DBF files found in {DBF_DIR}")
            return

        for dbf_file in files:
            table_name = os.path.splitext(dbf_file)[0].upper() # Normalize to uppercase
            path = os.path.join(DBF_DIR, dbf_file)
            
            print(f"\nProcessing {dbf_file} -> table {table_name}...")
            
            try:
                # Read DBF header
                dbf = DBF(path, encoding='latin-1')
                
                # Create table query using sql.SQL for safety
                col_defs = []
                field_names = []
                for field in dbf.fields:
                    col_name = field.name.upper() # Normalize to uppercase
                    field_names.append(col_name)
                    col_type = map_dbf_type_to_pg(field)
                    col_defs.append(sql.SQL("{} {}").format(sql.Identifier(col_name), sql.SQL(col_type)))
                
                create_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({});").format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(col_defs)
                )
                
                cur.execute(create_query)
                print(f"Table {table_name} ensures present.")

                # Clear table
                cur.execute(sql.SQL("TRUNCATE TABLE {};").format(sql.Identifier(table_name)))

                # Insert data
                if len(dbf) == 0:
                    print("No records to import.")
                    continue

                insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, field_names)),
                    sql.SQL(', ').join(sql.Placeholder() * len(field_names))
                )

                # Batch insert
                records = []
                batch_size = 1000
                count = 0
                
                for record in dbf:
                    # DBF records have uppercase keys by default
                    row = tuple(record[name] if name in record else None for name in field_names)
                    records.append(row)
                    
                    if len(records) >= batch_size:
                        cur.executemany(insert_query, records)
                        count += len(records)
                        records = []
                        print(f"  Imported {count} records...")

                if records:
                    cur.executemany(insert_query, records)
                    count += len(records)
                
                print(f"Successfully imported {count} records into {table_name}.")

            except Exception as e:
                import traceback
                print(f"Error processing {dbf_file}: {e}")
                traceback.print_exc()

        cur.close()
        conn.close()
        print("\nMigration completed successfully.")

    except Exception as e:
        print(f"Database connection error: {e}")

if __name__ == "__main__":
    migrate_dbf_to_pg()
