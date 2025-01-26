from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
import json
from dotenv import load_dotenv

# Cargar las variables de entorno
load_dotenv()

# Configuración de base de datos
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")

app = FastAPI()

# Clase para el cuerpo de la solicitud para calcular la factura
class CalculateInvoiceRequest(BaseModel):
    client_id: int
    mes: int

class ClientStatisticsResponse(BaseModel):
    consumo_total: float
    inyeccion_total: float

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
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(e)}")
    finally:
        if connection:
            cursor.close()
            connection.close()

@app.post("/calculate-invoice")
async def calculate_invoice(request: CalculateInvoiceRequest):
    try:
        # Lógica para calcular la factura
        data = obtener_datos_mes(request.mes, request.client_id)
        
        energia_activa = 0
        comercializacion_excedentes = 0
        excedentes_tipo_1 = 0
        excedentes_tipo_2 = 0
        ee2_total = 0
        ee1_total = 0
        horas_ee2 = []

        for row in data:
            inyeccion, consumo, CU, G, T, xm_value = row[1], row[2], row[3], row[4], row[5], row[6]
            
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

        # Crear el diccionario con los resultados
        result = {
            "energia_activa": energia_activa,
            "comercializacion_excedentes": comercializacion_excedentes,
            "excedentes_tipo_1": excedentes_tipo_1,
            "excedentes_tipo_2": excedentes_tipo_2,
            "ee2_total": ee2_total
        }

        # Guardar los resultados en un archivo JSON
        with open('factura_resultados.json', 'w') as json_file:
            json.dump(result, json_file, indent=4)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular la factura: {str(e)}")

# Otros endpoints...

