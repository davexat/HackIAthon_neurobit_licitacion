import re
import json
from typing import Dict, Any, List

def normalize_value(text: str) -> Any:
    """
    Limpia y normaliza un valor extraído para su comparación.
    Convierte montos a flotantes, extrae porcentajes y limpia texto.
    """
    if not isinstance(text, str):
        return text

    text = text.strip()
    
    # Extraer porcentajes numéricos
    percentage_match = re.search(r'(\d+\.?\d*)\s*%', text)
    if percentage_match:
        return float(percentage_match.group(1))

    # Extraer montos en USD y convertirlos a número
    # Elimina "USD", espacios y comas antes de convertir
    amount_match = re.search(r'USD\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
    if amount_match:
        return float(amount_match.group(1).replace(',', ''))
        
    # Extraer números de meses
    months_match = re.search(r'(\d+)\s*(meses|mes)', text, re.IGNORECASE)
    if months_match:
        return int(months_match.group(1))

    # Para otros textos, devolver en minúsculas y limpio
    return text.lower().strip()

def extract_data_from_oferta(oferta_content: str) -> Dict[str, Any]:
    """
    Extrae información clave del texto del documento de la oferta (contrato).
    """
    data = {}
    
    # Expresiones regulares para cada campo clave
    patterns = {
        "objeto": r'La PREFECTURA DEL GUAYAS encarga a EDIFIKA S\.A\..*la ejecución de la obra denominada "([^"]+)"',
        "monto": r'Monto:\s*(USD\s*[\d,]+\.\d+)',
        "plazo": r'Plazo:\s*(\d+\s*meses)',
        "anticipo": r'anticipo del\s*(\d+%)',
        "garantia_fiel_cumplimiento": r'Garantía de fiel cumplimiento:\s*(\d+% del contrato)',
        "garantia_anticipo": r'Garantía de buen uso del anticipo:\s*(\d+% del anticipo)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, oferta_content, re.DOTALL | re.IGNORECASE)
        if match:
            data[key] = normalize_value(match.group(1))

    return data

def extract_data_from_pliego(pliego_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrae información clave de la estructura JSON del pliego.
    NOTA: El pliego es un modelo y a menudo contiene rangos o texto en lugar de valores fijos.
    """
    data = {}
    
    # El monto se encuentra en la tabla de la página 8
    try:
        table_page_8 = next(t['table'] for t in pliego_data['additionalProp1']['tables'] if t['page'] == 8)
        # La celda del monto es la última en la fila que comienza con "Presupuesto Referencial"
        monto_row = next(row for row in table_page_8 if "Presupuesto Referencial" in row[0])
        data["monto"] = f"Referencial: {monto_row[-1]}" # Ejemplo, ya que no hay un valor numérico
    except StopIteration:
        data["monto"] = "No encontrado"

    # Plazo y anticipo de la sección III, página 2
    try:
        seccion_iii = next(t['table'] for t in pliego_data['additionalProp1']['tables'] if t['page'] == 2 and t['table'][0][0] == 'SECCIÓN III')
        contenido_seccion_iii = seccion_iii[0][1]
        
        plazo_match = re.search(r'3\.5\.\s*Plazo de ejecución', contenido_seccion_iii)
        if plazo_match:
            data["plazo"] = "Definido en cronograma" # El pliego no define un valor fijo aquí
            
        anticipo_match = re.search(r'3\.6\.1\.\s*Anticipo', contenido_seccion_iii)
        if anticipo_match:
            data["anticipo"] = "A definir por la entidad" # El pliego no define un % fijo aquí
    except StopIteration:
        data["plazo"] = "No encontrado"
        data["anticipo"] = "No encontrado"
        
    # Las garantías se mencionan en la evaluación, pero sin valores fijos en el pliego
    data["garantia_fiel_cumplimiento"] = "Requerida"
    data["garantia_anticipo"] = "Requerida"

    return data


def compare_documents(pliego: Dict[str, Any], oferta: Dict[str, Any]) -> str:
    """
    Compara los datos extraídos y genera un informe en formato Markdown.
    """
    report = []
    report.append("# Análisis Comparativo: Pliego vs. Oferta\n")
    report.append("| Parámetro | Valor en Pliego (Referencial) | Valor en Oferta (Contrato) | Estado |")
    report.append("|---|---|---|:---:|")

    # Mapeo de claves a nombres legibles
    key_map = {
        "monto": "Monto Total",
        "plazo": "Plazo de Ejecución",
        "anticipo": "Anticipo",
        "garantia_fiel_cumplimiento": "Garantía Fiel Cumplimiento",
        "garantia_anticipo": "Garantía Buen Uso Anticipo",
    }
    
    all_keys = sorted(key_map.keys())

    for key in all_keys:
        param_name = key_map.get(key, key.replace("_", " ").title())
        val_pliego = pliego.get(key, "No especificado")
        val_oferta = oferta.get(key, "No especificado")
        
        status_emoji = "❓" # Por defecto: no se puede determinar
        
        # Lógica de comparación
        if val_pliego != "No especificado" and val_oferta != "No especificado":
            # Comparamos si los valores son iguales. Para texto, es una comparación simple.
            # Para números, la normalización ya los hizo comparables.
            if str(val_pliego) == str(val_oferta):
                status_emoji = "Coincide"
            else:
                # Si no coinciden, verificamos si es una regla genérica del pliego.
                if isinstance(val_pliego, str) and ("Requerida" in val_pliego or "definir" in val_pliego):
                    status_emoji = "Cumple" # La oferta provee un valor donde el pliego solo lo requería
                else:
                    status_emoji = "Discrepancia"
        
        # Formatear valores para el reporte
        val_pliego_str = f"{val_pliego}%" if key.startswith('garantia') or key == 'anticipo' and isinstance(val_pliego, (int, float)) else str(val_pliego)
        val_oferta_str = f"{val_oferta}%" if key.startswith('garantia') or key == 'anticipo' and isinstance(val_oferta, (int, float)) else f"USD {val_oferta:,.2f}" if key == 'monto' and isinstance(val_oferta, (int, float)) else str(val_oferta)
        
        report.append(f"| **{param_name}** | {val_pliego_str} | {val_oferta_str} | {status_emoji} |")
        
    return "\n".join(report)

# --- INICIO DEL SCRIPT ---
if __name__ == "__main__":
    # 1. Cargar el JSON del Pliego desde un archivo
    try:
        with open('pliego_input.json', 'r', encoding='utf-8') as f:
            pliego_json_data = json.load(f)
        # Extraer los datos del pliego
        pliego_structured_data = extract_data_from_pliego(pliego_json_data)
    except FileNotFoundError:
        print("Error: Asegúrate de tener el archivo 'pliego_input.json' en el mismo directorio.")
        pliego_structured_data = {}
    
    # 2. Definir el contenido de la Oferta (Contrato)
    # En una aplicación real, esto vendría de leer un archivo PDF/texto.
    oferta_text_content = """
    CONTRATO DE OBRA PÚBLICA
    Entre la PREFECTURA DEL GUAYAS y EDIFIKA S.A.
    Proyecto: Ampliación de la Vía Samborondón - Asfaltado completo de 10 carriles
    Monto: USD 20,000,000.00
    Plazo: 12 meses
    CLÁUSULAS CONTRACTUALES
    PRIMERA - OBJETO DEL CONTRATO
    La PREFECTURA DEL GUAYAS encarga a EDIFIKA S.A. RUC: 0992881364001, la ejecución de la
    obra denominada "Ampliación de la Vía Samborondón - Asfaltado completo de 10 carriles",
    conforme a los estudios técnicos, planos, especificaciones y cronograma aprobado.
    QUINTA - ANTICIPO
    La contratante entregará un anticipo del 30% del contrato (USD 6,000,000.00), amortizable
    desde el mes 2 al mes 9.
    CUARTA - GARANTÍAS
    EDIFIKA S.A. deberá presentar:
    Garantía de fiel cumplimiento: 5% del contrato
    Garantía de buen uso del anticipo: 100% del anticipo
    """
    
    # Extraer los datos de la oferta
    oferta_structured_data = extract_data_from_oferta(oferta_text_content)
    
    # 3. Comparar ambos documentos y mostrar el reporte
    if pliego_structured_data and oferta_structured_data:
        comparison_report = compare_documents(pliego_structured_data, oferta_structured_data)
        print(comparison_report)
    else:
        print("No se pudieron extraer datos de uno o ambos documentos. No se puede generar el reporte.")