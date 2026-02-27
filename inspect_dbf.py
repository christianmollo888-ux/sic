from dbfread import DBF
import os

dbf_dir = r"C:\sicjac\dbf"
files = [f for f in os.listdir(dbf_dir) if f.lower().endswith('.dbf')]

for dbf_file in files:
    path = os.path.join(dbf_dir, dbf_file)
    print(f"\n--- Analyzing {dbf_file} ---")
    table = DBF(path, load=False)
    print(f"Fields: {len(table.fields)}")
    for field in table.fields:
        print(f"  - {field.name}: {field.type} (length {field.length})")
    print(f"Record count: {len(table)}")
    # Print first record as sample
    for record in table:
        print(f"Sample record: {record}")
        break
