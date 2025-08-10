import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

def create_generative_model() -> genai.GenerativeModel:
    load_dotenv()
    TOKEN_API_KEY = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=TOKEN_API_KEY)
    model = genai.GenerativeModel(
        "gemini-2.0-flash-exp", 
        system_instruction=get_system_prompt())
    return model

def get_system_prompt() -> str:
    return ("Eres un clasificador experto de textos de pliegos y propuestas de licitación. Tu trabajo es etiquetar y segmentar el texto plano recibido desde el extractor de PDFs (fase 2.1). Debes extraer también entidades clave (fechas, montos, porcentajes, RUC, etc.), normalizarlas y devolver TODO en un único JSON. No produzcas explicaciones, razonamientos ni texto adicional fuera del JSON. No incluyas cadenas de pensamiento.")

def get_user_prompt() -> str:
    return ('1. Entrada: recibirás un único campo `document_text` (texto plano tal cual fue extraído del PDF). El texto puede contener párrafos, saltos de línea, lista, etc.\n2. Objetivo: segmentar el documento en unidades útiles (preferencia por nivel oración — si una oración puede recibir una etiqueta, etiquétala — pero si varias oraciones contiguas comparten la misma etiqueta, agrúpalas en un segmento). También extraer entidades: `dates`, `amounts`, `percentages`, `ruc` y `percent_compliance` si aplica.\n3. Etiquetas/Clases sugeridas (usar exactamente estos nombres cuando correspondan):\n* `Condiciones Legales`\n* `Requisitos Técnicos`\n* `Condiciones Económicas`\n* `Garantías`\n* `Plazos`\n* `Penalidades`\n* `Criterios de Evaluación`\n* `Documentación Requerida`\n* `Alcance del Trabajo`\n* `Criterios Administrativos`\n* `Otros` (usar sólo si no encaja en las anteriores)\n* `Ambiguo` (usar cuando no hay suficiente contexto; devolver `candidate_labels`)\n4. Reglas de etiquetado:\n* Etiqueta a nivel oración por defecto. Si 2+ oraciones adyacentes tienen la misma etiqueta, combina en un segmento.\n* Si una oración contiene varias ideas que pertenecen a distintas etiquetas, separa esas ideas en sub-segmentos (p. ej. si una oración contiene plazo y multa, crea dos sub-segmentos con sus respectivos spans).\n* Permite múltiples etiquetas por segmento si realmente aplica (devuélvelas como lista).\n5. Extracción y normalización de entidades:\n* `dates`: devolver lista en formato `YYYY-MM-DD` cuando sea posible; si no se puede normalizar, devolver el texto original y `"normalized": null`.\n* `amounts`: devolver objeto con `original_text`, `currency` (si se detecta), y `value` (numérico, sin separadores). Ej: `{"original":"$1.200.000,00","currency":"USD","value":1200000}` — si no se puede identificar moneda, `currency: null`.\n* `percentages`: devolver numérico (ej. `5.5`).\n* `ruc`: extraer secuencias de dígitos que cumplan formatos comunes (10–13 dígitos) y devolverlas como string.\n* No inventes valores. Solo extrae lo que esté textual en `document_text`.\n6. Spans: para cada segmento y cada entidad devuelve `span: [start_char, end_char]` en índices de caracteres (UTF-8) dentro de `document_text`.\n7. Confianza: devuelve un `confidence` entre `0.0` y `1.0` por segmento y por entidad (heurística: `1.0` si hay coincidencia explícita con palabras clave o expresiones regulares, menor si es inferido por contexto).\n8. Formato de salida: EXACTAMENTE el siguiente JSON (sin campos extra):\n{"document_id": "<opcional_id_input>","language": "<es|en|undetermined>","segments": [{"id": 1,"labels": ["Condiciones Legales"],"text": "...","span": [start, end],"sentences": [{"text": "...","span": [s_start, s_end],"labels": ["Condiciones Legales"],"confidence": 0.95}],"entities": [{"type":"RUC","text":"1790012345001","span":[s,e],"confidence":0.98},{"type":"DATE","text":"01/01/2025","normalized":"2025-01-01","span":[s,e],"confidence":0.9}],"keywords": ["contratista","garantía"],"confidence": 0.92}],"entities_global": [{"type":"AMOUNT","original":"$500,000","currency":"USD","value":500000,"span":[s,e],"confidence":0.95}],"warnings": [],"metadata": {"model_version":"v1","processing_date":"2025-08-10"}}\n\n9. Comportamiento ante ambigüedad: si una unidad es `Ambiguo`, incluye `candidate_labels` con hasta 3 etiquetas ordenadas por preferencia y una `explain_short` (máx. 20 palabras).\n10. Salida obligatoria: responde únicamente con JSON válido y nada más.')

def parse_json_response(response: str) -> dict:
    response = response.strip(" \n \t ")
    start = response.find("{")
    end = response.rfind("}")
    if start != -1 and end != -1 and end > start:
        json_str = response[start:end+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    raise ValueError("No JSON found in response")

class GeminiAPI:
    def __init__(self):
        self.model = create_generative_model()

    def classify_document(self, prompt: str) -> str:
        response = self.model.generate_content(
            f"{get_user_prompt()}\n\n---DOCUMENTO INICIO---\n{prompt}\n---DOCUMENTO FIN---"
        )
        response_text = "".join([p.text for p in response.candidates[0].content.parts])
        return parse_json_response(response_text)
