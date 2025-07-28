from .queries import execute_query

def get_databases(credentials):
    """Get list of databases"""
    result = execute_query(credentials, None, "SHOW DATABASES")
    return [db["Database"] for db in result] if result else []

def get_tables(credentials, database):
    """Get list of tables in a database"""
    result = execute_query(credentials, database, "SHOW TABLES")
    return [list(table.values())[0] for table in result] if result else []

def get_table_columns(credentials, database, table_name):
    """Get column names for a table"""
    result = execute_query(credentials, database, f"SHOW COLUMNS FROM `{table_name}`")
    return [row["Field"] for row in result] if result else []
    
def create_table(credentials, database, table_name, columns):
    """Create a new table"""
    columns_def = ", ".join([f"`{col['name']}` {col['type']}" for col in columns])
    query = f"CREATE TABLE `{table_name}` ({columns_def})"
    return execute_query(credentials, database, query, fetch=False)