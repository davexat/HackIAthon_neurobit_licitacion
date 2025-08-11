# src/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Importamos la función desde el módulo ruc.ruc_search
# Python entiende esta ruta porque ejecutaremos el comando desde la raíz del proyecto.
from ruc.ruc_search import unificar_info_empresa_produccion

# --- Inicialización de la aplicación FastAPI ---
app = FastAPI(
    title="API de Consulta de Empresas Ecuador",
    description="Una API para unificar información del SRI y Supercias.",
    version="1.0.0"
)

# --- Configuración de CORS ---
# Permite que tu frontend se comunique con esta API.
origins = ["*"] # Para desarrollo. En producción, sé más específico.

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Definición del Endpoint de la API ---
@app.get("/api/v1/empresa/{ruc}", tags=["Empresas"])
def obtener_datos_empresa(ruc: str):
    """
    Obtiene la información consolidada de una empresa a partir de su RUC.
    """
    print(f"INFO: Recibida petición para el RUC: {ruc}")
    
    datos_empresa = unificar_info_empresa_produccion(ruc)
    
    if not datos_empresa:
        print(f"WARN: No se encontró información para el RUC {ruc}")
        raise HTTPException(
            status_code=404, 
            detail=f"No se encontró información para el RUC {ruc}"
        )
        
    print(f"INFO: Devolviendo datos para el RUC: {ruc}")
    return datos_empresa

@app.get("/", tags=["General"])
def read_root():
    return {"mensaje": "Bienvenido a la API de Consulta de Empresas"}