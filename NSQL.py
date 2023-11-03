import streamlit as st
import pyodbc as odbc
import pandas as pd
from dotenv import load_dotenv
import openai
import pymysql

# Loading environment variables
load_dotenv()
openai.api_key ='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'

# Setting up the Streamlit sidebar
st.sidebar.header("Interact with Database")
st.sidebar.markdown("""
## About 
Works with the help of OpenAI""")

st.sidebar.write("For Reference")
st.sidebar.write('''-[Streamlit](https://streamlit.io/) 
        -  [OpenAI](https://platform.openai.com/docs/models)''')


def main():
    st.header("AdventureWorks querying to a database in Natural Language")

    # Database connection details
    DRIVER_NAME = 'ODBC Driver 17 for SQL Server'
    SERVER_NAME = 'DESKTOP-K69AN5L\SQLEXPRESS'
    DATABASE_NAME = 'AdventureWorksLT2022'

    # Creating the connection string
    connection_string = f'DRIVER={{{DRIVER_NAME}}};SERVER={SERVER_NAME};DATABASE={DATABASE_NAME};trusted_connection=yes'

    try:
        # Establishing the connection with the SQL Server
        curs = odbc.connect(connection_string)
        cursor = curs.cursor()

        # Fetching the list of tables from the database
        cursor.execute("SELECT concat(Table_schema, '.', Table_name) FROM information_schema.tables")
        tables = cursor.fetchall()

        st.write("Connection Established")

        # Displaying the list of tables for selection
        option = st.selectbox("Select Your Table", options=tables, index=0, format_func=lambda x: x[0])
        st.write("Table Chosen", option)

        # Extracting the table name from the selected option
        # option1 = option.split(".")[1]
        option1 = option[0].split(".")[1]

        # Fetching the list of columns for the selected table
        cursor.execute(f"SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{option1}'")
        columns = cursor.fetchall()

        # Displaying the columns as radio buttons
        selected_column = st.radio("Columns", options=[x[0] for x in columns])

        # Input field for the natural language query
        query = st.text_input("Write your query")

        if query:
            # Generating SQL query using OpenAI
            prompt = f"Generate a SQL server query to retrieve {query} from the database with table {option} "
            response = openai.Completion.create(engine='text-davinci-003', prompt=prompt, max_tokens=100)
            generated_query = response.choices[0].text.strip()
            st.write(generated_query)

            # Executing the generated query
            result = cursor.execute(generated_query)

            # Fetching the data and column names
            field = [i[0] for i in cursor.description]
            data = result.fetchall()

            # Displaying the data as a pandas DataFrame
            if len(data) > 0:
                df = pd.DataFrame(data, columns=field)
                st.write("Data:")
                st.write(df)
            else:
                st.write("No data retrieved.")

    except odbc.Error as e:
        st.error(f"Error: {e}")

if __name__ == '__main__':
    main()
