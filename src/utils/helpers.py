import pandas as pd

def prepare_data_for_export(data):
    """Convert data for CSV export"""
    return pd.DataFrame(data)

def get_column_types():
    """Return common MySQL column types"""
    return [
        "INT", "VARCHAR(255)", "TEXT", "DATE", "DATETIME", 
        "FLOAT", "BOOLEAN", "BIGINT", "DOUBLE"
    ]