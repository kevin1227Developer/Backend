import psycopg2
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

def mostrar_datos_tabla(cursor, table_name):
    cursor.execute(f"SELECT * FROM esquema.{table_name};")
    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

    print(f"\nDatos de la tabla {table_name}:")
    print(df.head())  # Muestra las primeras filas para visualización

try:
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    print("Conexión exitosa!")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'esquema';
    """)

    tables = cursor.fetchall()
    print("\nTablas encontradas en el esquema 'esquema':")

    with pd.ExcelWriter('datos_transformados.xlsx') as writer:
        for table in tables:
            table_name = table[0]
            print(f"\nExtrayendo datos de la tabla {table_name}:")

            # Mostrar los datos de la tabla en consola
            mostrar_datos_tabla(cursor, table_name)

            cursor.execute(f"SELECT * FROM esquema.{table_name};")
            data = cursor.fetchall()

            df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])

            df = df.fillna(0)

            df.to_excel(writer, sheet_name=table_name, index=False)

        print("Datos transformados y guardados en 'datos_transformados.xlsx'.")

except Exception as e:
    print("Error al conectar con la base de datos o durante el proceso ETL:", e)

finally:
    if connection:
        cursor.close()
        connection.close()
        print("\nConexión cerrada.")
