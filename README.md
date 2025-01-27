# Proyecto de Facturación de Energía

Este proyecto tiene como objetivo gestionar la facturación de energía utilizando datos de consumo e inyección. Se conecta a una base de datos PostgreSQL para extraer datos relevantes y generar informes de facturación.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```
prueba_tecnica/
│
├── venv/                     # Entorno virtual
│   ├── .env                  # Variables de entorno
│   ├── connect_db.py         # Conexión a la base de datos
│   ├── factura_energia.py    # Lógica de cálculo de facturas
│   ├── factura_resultados.txt # Resultados de la factura generada
│   └── requirements.txt       # Dependencias del proyecto
│
└── info/                     # Archivos de datos
    ├── consumption.csv       # Datos de consumo
    ├── injection.csv         # Datos de inyección
    ├── records.csv           # Registros de consumo
    ├── services.csv          # Servicios disponibles
    └── tariffs.csv           # Tarifas aplicables
```

## Descripción de Archivos

### 📁 `prueba_tecnica/venv/main.py`
Este archivo es el punto de entrada principal de tu aplicación. Aquí es donde se inicia la ejecución del programa. Generalmente, se encarga de coordinar las diferentes partes del sistema, como la conexión a la base de datos y la ejecución de las funciones de facturación.

### 📦 `prueba_tecnica/venv/requirements.txt`
Este archivo contiene una lista de todas las dependencias necesarias para ejecutar el proyecto. Al instalar las dependencias desde este archivo, aseguras que tu entorno tenga todas las bibliotecas requeridas, como `psycopg2` para la conexión a PostgreSQL y `pandas` para el manejo de datos.

### 📄 `prueba_tecnica/venv/factura_resultados.txt`
Este archivo es donde se guardan los resultados de la facturación. Después de ejecutar el cálculo de la factura, los detalles se escriben en este archivo, lo que permite a los usuarios revisar la información de la factura generada.

### ⚙️ `prueba_tecnica/venv/factura_energia.py`
Este archivo contiene la lógica para calcular la factura de energía. Se encarga de extraer datos de la base de datos, procesar la información y calcular los costos basados en el consumo y la inyección de energía. También maneja la escritura de los resultados en `factura_resultados.txt`.

### 🔗 `prueba_tecnica/venv/connect_db.py`
Este archivo se encarga de establecer la conexión con la base de datos PostgreSQL. Utiliza las variables de entorno definidas en el archivo `.env` para obtener la configuración de la base de datos. Es fundamental para que el resto de la aplicación pueda acceder a los datos necesarios para el cálculo de la factura.

## Requisitos

Para ejecutar este proyecto, asegúrate de tener instalado:

- Python 3.8 o superior
- PostgreSQL
- Las dependencias especificadas en `requirements.txt`

## Instalación

1. Clona el repositorio:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd prueba_tecnica
   ```

2. Crea un entorno virtual y actívalo:

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias:

   ```bash
   pip install -r venv/requirements.txt
   ```

4. Configura las variables de entorno en el archivo `.env`:

   ```plaintext
   DB_HOST=localhost
   DB_DATABASE=esquema
   DB_USER=postgres
   DB_PASSWORD=1234
   DB_PORT=5432
   ```

## Uso

Para calcular la factura de un cliente específico, ejecuta el siguiente comando:

```bash
python venv/factura_energia.py
```

Esto generará un archivo `factura_resultados.txt` con los detalles de la factura calculada.

## Ejemplo de Uso

Al ejecutar el comando para calcular la factura, se generará un archivo `factura_resultados.txt` que contendrá información como:

![Ejemplo de factura](venv\imagen\prueba.jpg)

## Errores Comunes

- **Error de conexión a la base de datos**: Asegúrate de que las credenciales en el archivo `.env` sean correctas y que el servidor de PostgreSQL esté en funcionamiento.
- **Dependencias no instaladas**: Verifica que hayas ejecutado `pip install -r venv/requirements.txt` correctamente.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-caracteristica`).
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva característica'`).
4. Envía un pull request.

## Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

## Posibles mejoras futuras:

- Añadir autenticación y autorización para la API.
- Mejorar el manejo de errores (por ejemplo, retornar mensajes de error más descriptivos).
- Optimizar la consulta SQL si el volumen de datos es grande.
- Mejorar la estructura del archivo JSON de salida para hacerla más legible.
- Incluir pruebas automáticas para los endpoints de la API.

## Esquema de Base de Datos

A continuación se presenta el esquema de la base de datos utilizado en este proyecto:

```sql
-- Crear el esquema de base de datos
CREATE SCHEMA esquema;

-- Crear tabla services
CREATE TABLE esquema.services (
    id_service SERIAL PRIMARY KEY,        -- Identificador único del servicio
    id_market INTEGER NOT NULL,           -- Identificador del mercado
    cdi INTEGER NOT NULL,                 -- CDI (definición específica)
    voltage_level INTEGER NOT NULL,       -- Nivel de voltaje
    CONSTRAINT pk_services PRIMARY KEY (id_market, cdi, voltage_level)  -- Clave primaria compuesta
);

-- Crear tabla tariffs
CREATE TABLE esquema.tariffs (
    id_market INTEGER NOT NULL,           -- Relación con services
    cdi INTEGER NOT NULL,                 -- Relación con services
    voltage_level INTEGER NOT NULL,       -- Relación con services
    G FLOAT NOT NULL,                     -- Tarifa G
    T FLOAT NOT NULL,                     -- Tarifa T
    D FLOAT NOT NULL,                     -- Tarifa D
    R FLOAT NOT NULL,                     -- Tarifa R
    C FLOAT NOT NULL,                     -- Tarifa C
    P FLOAT NOT NULL,                     -- Tarifa P
    CU FLOAT NOT NULL,                    -- Tarifa CU
    PRIMARY KEY (id_market, cdi, voltage_level),
    FOREIGN KEY (id_market, cdi, voltage_level) REFERENCES esquema.services (id_market, cdi, voltage_level)
);

-- Crear tabla records
CREATE TABLE esquema.records (
    id_record SERIAL PRIMARY KEY,         -- Identificador único del registro
    id_service INTEGER NOT NULL,          -- Relación con services
    record_timestamp TIMESTAMP NOT NULL,  -- Fecha y hora del registro
    FOREIGN KEY (id_service) REFERENCES esquema.services (id_service)
);

-- Crear tabla injection
CREATE TABLE esquema.injection (
    id_record INTEGER NOT NULL,           -- Relación con records
    value FLOAT NOT NULL,                 -- Valor de la inyección
    FOREIGN KEY (id_record) REFERENCES esquema.records (id_record)
);

-- Crear tabla consumption
CREATE TABLE esquema.consumption (
    id_record INTEGER NOT NULL,           -- Relación con records
    value FLOAT NOT NULL,                 -- Valor del consumo
    FOREIGN KEY (id_record) REFERENCES esquema.records (id_record)
);

-- Crear tabla xm_data_hourly_per_agent
CREATE TABLE esquema.xm_data_hourly_per_agent (
    value FLOAT NOT NULL,                 -- Valor por agente
    record_timestamp TIMESTAMP NOT NULL   -- Marca de tiempo del registro
);


