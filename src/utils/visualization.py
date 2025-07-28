import pandas as pd
import plotly.express as px

def visualize_data(data, viz_type):
    """Visualize query results"""
    if not data:
        return None
    
    df = pd.DataFrame(data)
    
    if viz_type == "Table":
        return df
    elif viz_type == "Bar Chart" and len(df.columns) >= 2:
        return px.bar(df, x=df.columns[0], y=df.columns[1])
    elif viz_type == "Pie Chart" and len(df.columns) >= 2:
        return px.pie(df, names=df.columns[0], values=df.columns[1])
    elif viz_type == "Line Chart" and len(df.columns) >= 2:
        return px.line(df, x=df.columns[0], y=df.columns[1])
    elif viz_type == "Scatter Plot" and len(df.columns) >= 2:
        return px.scatter(df, x=df.columns[0], y=df.columns[1])
    elif viz_type == "Histogram" and len(df.columns) >= 1:
        return px.histogram(df, x=df.columns[0])
    
    return df