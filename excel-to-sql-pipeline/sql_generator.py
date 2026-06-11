def generate_create_table(schema):
    table_name = schema["table_name"]
    columns = schema["columns"]
    primary_keys = schema.get("primary_key", [])

    col_defs = []
    for col, dtype in columns.items():
        col_defs.append(f"{col} {dtype}")

    pk_sql = ""
    if primary_keys:
        pk_sql = f", PRIMARY KEY ({', '.join(primary_keys)})"

    create_sql = (
        f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(col_defs) + pk_sql + "\n);"
    )
    return create_sql


def generate_insert(df, schema):
    table_name = schema["table_name"]
    columns = list(schema["columns"].keys())

    values_list = []

    for _, row in df.iterrows():
        values = []
        for col in columns:
            val = row.get(col, "")
            if isinstance(val, str):
                val = val.replace("'", "''")
                values.append(f"'{val}'")
            else:
                values.append(str(val))
        values_list.append(f"({', '.join(values)})")

    insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n"
    insert_sql += ",\n".join(values_list) + ";"

    return insert_sql
