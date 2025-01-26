import psycopg2
import os
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

# Función para obtener los datos del mes y cliente desde la base de datos
def obtener_datos_mes(mes, client_id):
    try:
        print(f"Conectando a la base de datos para el mes {mes} y cliente {client_id}...")
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_DATABASE,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = connection.cursor()
        print("Conexión exitosa!")

        cursor.execute("""
        SELECT 
            r.id_record, 
            i.value AS inyeccion, 
            c.value AS consumo,
            t.CU, t.G, t.T, 
            xm.value AS xm_value
        FROM esquema.records r
        LEFT JOIN esquema.injection i ON r.id_record = i.id_record
        LEFT JOIN esquema.consumption c ON r.id_record = c.id_record
        LEFT JOIN esquema.services s ON r.id_service = s.id_service
        LEFT JOIN esquema.tariffs t ON s.id_market = t.id_market
        LEFT JOIN esquema.xm_data_hourly_per_agent xm 
            ON EXTRACT(HOUR FROM r.record_timestamp) = EXTRACT(HOUR FROM xm.record_timestamp)
        WHERE EXTRACT(MONTH FROM r.record_timestamp) = %s AND r.id_service = %s;
        """, (mes, client_id))

        data = cursor.fetchall()

        if not data:
            raise Exception("No se encontraron datos para el cliente y mes especificados.")
        
        return data

    except Exception as e:
        print(f"Error al conectar o consultar la base de datos: {e}")
        raise Exception("Error al conectar o consultar la base de datos.")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Función para guardar los resultados en un archivo de texto
def guardar_resultados_en_txt(energia_activa, comercializacion_excedentes, excedentes_tipo_1, excedentes_tipo_2, ee2_total, horas_ee2):
    with open('factura_resultados.txt', 'w') as f:
        f.write(f"Energía Activa (EA): {energia_activa}\n")
        f.write(f"Comercialización de Excedentes (EC): {comercializacion_excedentes}\n")
        f.write(f"Excedentes de Energía tipo 1 (EE1): {excedentes_tipo_1}\n")
        f.write(f"Excedentes de Energía tipo 2 (EE2): {excedentes_tipo_2}\n")
        f.write(f"Total de horas con exceso (EE2): {len(horas_ee2)}\n")
        f.write("\nDetalles de la factura:\n")
        f.write(f"EA: {energia_activa}\n")
        f.write(f"EC: {comercializacion_excedentes}\n")
        f.write(f"EE1: {excedentes_tipo_1}\n")
        f.write(f"EE2: {ee2_total}\n")

# Función para calcular la factura
def calcular_factura(client_id, mes):
    print(f"\nCalculando factura para el cliente {client_id} y mes {mes}...")

    data = obtener_datos_mes(mes, client_id)
    
    energia_activa = 0
    comercializacion_excedentes = 0
    excedentes_tipo_1 = 0
    excedentes_tipo_2 = 0
    ee2_total = 0
    ee1_total = 0
    horas_ee2 = []

    for row in data:
        # Imprimir los valores de cada fila para ver si coinciden
        print(f"Fila de datos: {row}")
        
        # Asegúrate de que los índices de las columnas estén correctos según los datos que se están recuperando
        inyeccion, consumo, CU, G, T, xm_value = row[1], row[2], row[3], row[4], row[5], row[6]
        
        print(f"Procesando registro: {row[0]} - Inyección: {inyeccion}, Consumo: {consumo}, CU: {CU}, G: {G}, XM: {xm_value}")
        
        # Energía activa (EA)
        energia_activa += (consumo + G)
        
        # Comercialización de excedentes (EC)
        comercializacion_excedentes += (inyeccion * CU)

        # Excedentes tipo 1 (EE1)
        if inyeccion >= consumo:
            excedentes_tipo_1 += (inyeccion - consumo)
            ee1_total += consumo  # Todo se considera como EE1 si inyección >= consumo

        # Excedentes tipo 2 (EE2)
        if inyeccion < consumo:
            excedente_hora = consumo - inyeccion
            ee2_total += excedente_hora * xm_value  # Se multiplica por xm_value para EE2
            horas_ee2.append(excedente_hora)  # Se añaden las horas con excedente

    guardar_resultados_en_txt(energia_activa, comercializacion_excedentes, excedentes_tipo_1, excedentes_tipo_2, ee2_total, horas_ee2)
    
    print("Factura calculada y guardada en 'factura_resultados.txt'")

# Llamar a la función con un cliente y mes específicos
client_id = 1  # Cambia esto por el ID del cliente que deseas consultar
mes = 1  # Cambia esto por el mes para el que deseas calcular la factura
calcular_factura(client_id, mes)
