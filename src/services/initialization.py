# from src.database.queries import execute_query
# from src.database.schema import create_database, create_table
# import streamlit as st

# def initialize_sample_data(credentials, database):
#     """Insert sample data if tables are empty"""
#     if execute_query(credentials, database, "SELECT COUNT(*) AS count FROM students", fetch=True)[0]['count'] > 0:
#         return True
    
#     sample_data = {
#         "students": [
#             ("Alice Johnson", "Computer Science", 2020, 3.8, 85000, "POINT(-74.0059 40.7128)"),
#             ("Bob Smith", "Data Science", 2021, 3.5, 92000, "POINT(-74.0100 40.7150)"),
#             ("Komal Patel", "Business", 2019, 3.9, 78000, None)
#         ],
#         "courses": [
#             ("Data Structures", "CS", 4, "Dr. Smith", None),
#             ("Machine Learning", "DS", 3, "Dr. Johnson", None),
#             ("Machine Learning Fundamentals", None, None, None, "Introduction to ML algorithms"),
#             ("Advanced Data Science", None, None, None, "Deep learning and neural networks")
#         ],
#         "departments": [
#             ("Computer Science", "CS", "Dr. Smith"),
#             ("Data Science", "DS", "Dr. Johnson")
#         ],
#         "faculty": [
#             ("Dr. Smith", "CS", "Professor"),
#             ("Dr. Johnson", "DS", "Associate Professor")
#         ],
#         "enrollments": [
#             ("Alice Johnson", "Data Structures", "A"),
#             ("Bob Smith", "Machine Learning", "B+")
#         ]
#     }

#     try:
#         for table, data in sample_data.items():
#             for record in data:
#                 if table == "students":
#                     query = """
#                     INSERT INTO students 
#                     (name, major, enrollment_year, gpa, salary, location) 
#                     VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s))
#                     """
#                 else:
#                     placeholders = ", ".join(["%s"] * len(record))
#                     query = f"INSERT INTO {table} VALUES (NULL, {placeholders})"
                
#                 execute_query(credentials, database, query, record, fetch=False)
        
#         st.toast("✅ Sample data initialized", icon="✅")
#         return True
#     except Exception as e:
#         st.error(f"❌ Data initialization failed: {str(e)}")
#         return False