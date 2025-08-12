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


# --- Nuevo Endpoint para Extracción de PDF ---
@app.post("/api/v1/extract_pdf", tags=["PDF"])
async def extract_pdf_data(
    file: UploadFile = File(...),
    use_ocr: Optional[bool] = Form(False),
    extract_tables: Optional[bool] = Form(True)
) -> Dict[str, Any]:
    """
    Extrae texto y tablas de un archivo PDF subido.

    - **file**: El archivo PDF a procesar.
    - **use_ocr**: Opcional. Si se establece en `True`, fuerza el uso de OCR. Por defecto es `False`.
    - **extract_tables**: Opcional. Si se establece en `True`, intenta extraer tablas. Por defecto es `True`.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF.")

    # Guardar el archivo en una ubicación temporal
    # Esto es crucial ya que 'pdf_extractor' necesita una ruta de archivo.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name
    
    print(f"INFO: Procesando PDF temporal en: {temp_file_path} con use_ocr={use_ocr} y extract_tables={extract_tables}")
    
    try:
        # Llamar a la función de extracción con los parámetros recibidos
        extracted_data = extract_text_from_pdf(
            pdf_path=temp_file_path, 
            use_ocr=use_ocr, 
            extract_tables=extract_tables
        )
        print("INFO: Extracción de PDF completada con éxito.")
        return extracted_data
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"ERROR: Fallo al procesar el PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {e}")
    finally:
        # Asegurarse de eliminar el archivo temporal
        os.unlink(temp_file_path)
        print("INFO: Archivo temporal eliminado.")
