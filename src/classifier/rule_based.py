import re
import unicodedata
from typing import List, Dict

def test():
    """Prueba de humo: ejecuta la clasificación sobre un texto de ejemplo y muestra resultados."""
    ejemplo = "El contratista deberá cumplir con todas las normas de seguridad.\
     El plazo será de 90 días a partir de la firma del contrato. El presupuesto estimado es de $500,000.\
     Se solicita presentar póliza de seguro de buena ejecución. La primera entrega parcial será en 30 días hábiles.\
     Contacto: soporte@empresa.com o visite https://www.empresa.com/terminos."

    resultados = classify_paragraph(ejemplo)
    print("=== Resultados de clasificación ===")
    for r in resultados:
        print(f"- [{r['categoria']}] {r['texto']}")
    # Aserciones simples (no detienen la ejecución)
    try:
        assert any(r["categoria"] == "CONDICIONES_LEGALES" for r in resultados)
        assert any(r["categoria"] == "CONDICIONES_ECONOMICAS" for r in resultados)
        assert any(r["categoria"] == "GARANTIAS_Y_POLIZAS" for r in resultados)
        print("Aserciones básicas: OK")
    except AssertionError:
        print("Aserciones básicas: alguna categoría esperada no se detectó")

def get_categories() -> dict[str, list[str]]:
    """Devuelve categorías con palabras clave en minúsculas.
        Nota: se evita duplicar términos entre categorías cuando sea posible.
        """
    categories = {
        "CONDICIONES_LEGALES": [
            "contratista", "ley", "norma", "garantía", "responsabilidad",
            "cláusula", "contrato", "incumplimiento",
        ],
        "REQUISITOS_TECNICOS": [
            "plazo", "entrega", "materiales", "especificación", "obra",
            "técnico", "alcance", "documentación", "procedimiento",
        ],
        "CONDICIONES_ECONOMICAS": [
            "presupuesto", "costo", "pago", "monto", "precio",
            "tarifa", "anticipo", "factura",
        ],
        "GARANTIAS_Y_POLIZAS": [
            "póliza", "seguro", "fianza", "caución", "aval",
            "garantía de cumplimiento", "garantía de calidad",
        ],
        "PLAZOS_Y_ENTREGABLES": [
            "entregable", "entregables", "cronograma", "hito", "milestone",
            "entrega parcial", "fecha de entrega", "vencimiento", "deadline",
        ],
    }
    return categories

def _normalize(text: str) -> str:
    """Normaliza texto: minúsculas y sin acentos."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text

def _build_keyword_patterns(categories: Dict[str, List[str]]) -> Dict[str, List[re.Pattern]]:
    """Construye patrones por categoría con límites de palabra y flexión simple (s/es)."""
    patterns: Dict[str, List[re.Pattern]] = {}
    for cat, keywords in categories.items():
        pats = []
        for kw in keywords:
            if not kw:
                continue
            # Normalizar keyword y escapar para regex
            nkw = _normalize(kw).strip()
            if not nkw:
                continue
            # Si la keyword tiene espacios (multi-palabra), se busca como frase completa con límites aproximadamente
            if " " in nkw:
                # Evitar cortar palabras, permitir espacios múltiples
                pat = re.compile(rf"(?<!\w){re.escape(nkw)}(?!\w)")
            else:
                # Coincidencia por palabra con flexión simple plural s/es
                # Ej.: "precio" -> "precio(s|es)?"
                pat = re.compile(rf"\b{re.escape(nkw)}(?:s|es)?\b")
            pats.append(pat)
        patterns[cat] = pats
    return patterns

def classify_text(text) -> str:
    """Clasifica un texto basado en palabras clave, con normalización y coincidencia por palabra.
    - Normaliza a minúsculas sin acentos.
    - Cuenta coincidencias por categoría con patrones regex.
    - Desempate mediante prioridad fija de categorías.
    """
    categories = get_categories()
    norm_text = _normalize(str(text))
    patterns = _build_keyword_patterns(categories)

    scores = {categoria: 0 for categoria in categories}
    for categoria, pats in patterns.items():
        for pat in pats:
            # count non-overlapping matches
            matches = pat.findall(norm_text)
            if matches:
                scores[categoria] += len(matches)

    # Si nadie tiene puntuación, OTRO
    max_cat = max(scores, key=scores.get) if scores else None
    if not max_cat or scores[max_cat] == 0:
        return "OTRO"

    # Desempate por prioridad (más específicas primero)
    prioridad = [
        "GARANTIAS_Y_POLIZAS",
        "PLAZOS_Y_ENTREGABLES",
        "CONDICIONES_ECONOMICAS",
        "REQUISITOS_TECNICOS",
        "CONDICIONES_LEGALES",
    ]
    max_score = max(scores.values())
    candidatas = [c for c, s in scores.items() if s == max_score]
    if len(candidatas) == 1:
        return candidatas[0]
    for cat in prioridad:
        if cat in candidatas:
            return cat
    # Fallback determinista
    return sorted(candidatas)[0]

def classify_paragraph(paragraph) -> list:
    """Divide un párrafo en oraciones considerando abreviaturas/siglas, URLs y correos,
    y clasifica cada oración usando classify_text. Retorna una lista de
    diccionarios con las claves 'texto' y 'categoria'.
    """
    if paragraph is None:
        return []

    text = str(paragraph).strip()
    if not text:
        return []

    DOT = "§DOT§"  # marcador temporal para puntos protegidos
    NL = "§NL§"  # marcador temporal para saltos de línea

    protected = text.replace("\r\n", "\n").replace("\r", "\n")
    protected = re.sub(r"\n+", f" {NL} ", protected)

    # Proteger URLs y correos (reemplazando los '.' internos)
    def _protect_dots(m: re.Match) -> str:
        return m.group(0).replace(".", DOT)

    # URLs con http(s)
    protected = re.sub(r"https?://\S+", _protect_dots, protected)
    # Dominios tipo www.
    protected = re.sub(r"\bwww\.\S+", _protect_dots, protected)
    # Emails básicos
    protected = re.sub(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+", _protect_dots, protected)

    # Abreviaturas comunes (títulos, compañías y otras)
    abbreviations = [
        # Títulos y grados
        "Dr.", "Dra.", "Sr.", "Sra.", "Ing.", "Lic.", "Arq.",
        "Phd.", "Ph.D.", "M.Sc.", "MSc.", "Mg.", "Mtr.",
        # Compañías y razones sociales
        "S.A.", "S.A.S.", "S.R.L.", "S.L.", "C.A.", "S.A.C.", "C.V.", "Ltd.", "Inc.", "Co.", "Corp.", "Cía.",
        # Otras comunes
        "etc.", "Art.", "art.", "No.", "Nº.", "N°.", "a.m.", "p.m.", "p.ej.", "p.e.", "e.g.",
    ]
    for abbr in abbreviations:
        escaped = re.escape(abbr)
        replacement = abbr.replace(".", DOT)
        protected = re.sub(escaped, replacement, protected)

    # Proteger siglas con puntos (p. ej., U.S.A., EE.UU., A.B.C.)
    protected = re.sub(
        r"(?<!\w)((?:[A-ZÁÉÍÓÚÑ]\.){2,})(?!\w)",
        lambda m: m.group(1).replace(".", DOT),
        protected
    )

    # Proteger números decimales (p. ej., 3.14)
    protected = re.sub(r"(\d)\.(\d)", r"\1" + DOT + r"\2", protected)

    # Dividir por final de oración: ., ?, ! seguidos de espacio/fin
    parts = re.split(r"(?<=[.!?])\s+", protected)

    # Dividir adicionalmente por saltos de línea marcados
    candidates: list[str] = []
    for part in parts:
        subparts = re.split(r"\s*" + re.escape(NL) + r"\s*", part)
        for sp in subparts:
            s = sp.strip()
            if s:
                candidates.append(s)

    # Restaurar puntos y clasificar
    results: list[dict] = []
    for s in candidates:
        s = s.replace(DOT, ".").replace(NL, " ").strip()
        if not s:
            continue
        categoria = classify_text(s)
        results.append({"texto": s, "categoria": categoria})

    return results