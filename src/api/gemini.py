import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

def create_generative_model(api_key: str) -> genai.GenerativeModel:
    load_dotenv()
    TOKEN_API_KEY = api_key or os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=TOKEN_API_KEY)
    model = genai.GenerativeModel(
        "gemini-2.0-flash-exp", 
        system_instruction=get_system_prompt())
    return model

def get_system_prompt() -> str:
    return (
        "Eres un clasificador experto de textos de pliegos y propuestas de licitación. "
        "Tu tarea: segmentar y etiquetar el texto plano recibido (campo document_text) y extraer entidades clave. "
        "RESPONDE SÓLO con JSON válido conforme al esquema compacto. No expliques nada fuera del JSON. "
        "No uses cadenas de pensamiento."
    )

def get_user_prompt() -> str:
    return (
        "INPUT: recibirás un objeto con al menos los campos: document_id (opcional), document_text, "
        "chunk_index (opcional), total_chunks (opcional).\n"
        "REGLAS DE OUTPUT (obligatorio):\n"
        "1) Responde EXCLUSIVAMENTE con JSON EXACTO siguiendo este schema compacto:\n"
        "{"
        "\"document_id\":\"<opcional>\","
        "\"language\":\"<es|en|undetermined>\","
        "\"segments\":["
        "{\"id\":1,\"labels\":[\"Condiciones Legales\"],\"span\":[start,end],"
        "\"excerpt\":\"...\",\"entities\":[{\"type\":\"RUC\",\"text\":\"...\",\"span\":[s,e],\"confidence\":0.99}],"
        "\"confidence\":0.95}"
        "],"
        "\"entities\":[{\"type\":\"AMOUNT\",\"original\":\"...\",\"currency\":\"USD\",\"value\":1234,\"span\":[s,e],\"confidence\":0.99}],"
        "\"warnings\":[],"
        "\"meta\":{\"model\":\"v1\",\"processing_date\":\"YYYY-MM-DD\",\"chunk_index\":1,\"total_chunks\":7}"
        "}\n"
        "2) Etiquetas permitidas (usar exactamente estos nombres, con espacios y acentos): "
        "\"Condiciones Legales\", \"Requisitos Técnicos\", \"Condiciones Económicas\", \"Garantías\", "
        "\"Plazos\", \"Penalidades\", \"Criterios de Evaluación\", \"Documentación Requerida\", "
        "\"Alcance del Trabajo\", \"Criterios Administrativos\", \"Otros\", \"Ambiguo\".\n"
        "3) Span: índices de carácter sobre document_text (UTF-8). Usa span para referenciar texto; "
        "NO incluyas el texto completo en la respuesta.\n"
        "4) Excerpt: máximo 40 caracteres. Regla: reemplaza newlines por espacio, colapsa múltiples espacios, "
        "recorta y añade '…' si truncas. Útil para la UI.\n"
        "5) Entities: incluir ocurrencias encontradas con su span y confidence. No dupliques exactamente la misma (type,span).\n"
        "6) Si una unidad es AMBIGUA: usa labels: [\"Ambiguo\"] y añade candidate_labels (máx 3) + explain_short (máx 20 palabras).\n"
        "7) Confidence: 0.0–1.0 (heurística: 1.0 = regex o coincidencia exacta; 0.9=palabras clave fuertes; <0.6 = inferido).\n"
        "8) Minimiza tokens: Considera como unidad principal de clasificación a la idea completa, entendida como el bloque mínimo de texto que expresa un único concepto, disposición o cláusula."
        "Una idea puede abarcar una oración completa, varias oraciones consecutivas, o parte de una oración, según corresponda."
        "Mantén juntas todas las oraciones que expresen la misma idea o pertenezcan a la misma categoría de etiqueta."
        "Solo divide una idea si hay un cambio claro de tema o de categoría de etiqueta."
        "Evita repetir texto innecesariamente: si una idea ya está cubierta en un segmento, no la dupliques en otro."
        "sea necesario (si lo incluyes, aplicar misma política de excerpt/span y no repetir texto completo).\n"
        "9) Si detectas problemas de OCR (p. ej. muchas palabras sin espacios), añade a warnings: \"ocr_spacing_issue\" y evita etiquetas confiables.\n"
        "10) SALIDA OBLIGATORIA: JSON válido y nada más."
    )

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
    def __init__(self, api_key: str = None):
        self.model = create_generative_model(api_key)

    def classify_document(self, prompt: str) -> dict:
        response = self.model.generate_content(
            f"{get_user_prompt()}\n\n---DOCUMENTO INICIO---\n{prompt}\n---DOCUMENTO FIN---",
            generation_config={"max_output_tokens": 8192}
        )
        response_text = "".join([p.text for p in response.candidates[0].content.parts])
        return parse_json_response(response_text)
