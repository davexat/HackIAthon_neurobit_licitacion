import re
from typing import List, Dict, Any

def reconstruir_documento_desde_json(segmentos: List[Dict[str, Any]]) -> str:
    """
    Reconstruye un documento narrativo a partir de segmentos clasificados.
    """
    estructura = {
        "Objeto del Contrato": [],
        "Monto": [],
        "Plazo": [],
        "Garantías": [],
        "Penalidades": [],
        "Condiciones Legales": [],
        "Otros": []
    }

    # Clasificar los segmentos
    for seg in segmentos:
        label = seg.get("label", "Otros")
        texto = seg.get("excerpt", "").strip()
        if texto:
            if label in estructura:
                estructura[label].append(texto)
            else:
                estructura["Otros"].append(texto)

    # Función para normalizar valores monetarios
    def normalizar_montos(texto):
        texto = re.sub(r'(\d+)K\b', lambda m: str(int(m.group(1)) * 1000), texto)
        texto = re.sub(r'(\d+)M\b', lambda m: str(int(m.group(1)) * 1000000), texto)
        texto = re.sub(r'USD\s?(\d[\d.,]*)', lambda m: f"USD {float(m.group(1).replace(',', '')):,.2f}", texto)
        return texto

    # Construir el documento final
    partes = []
    for seccion, textos in estructura.items():
        if textos:
            partes.append(f"\n### {seccion}\n")
            for t in textos:
                partes.append(f"- {normalizar_montos(t)}")

    return "\n".join(partes).strip()
