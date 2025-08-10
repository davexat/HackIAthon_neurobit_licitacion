from sri_info import consultar_ruc_sri
from supercias_info import obtener_informacion_compania

def reemplazar_none_con_vacio(obj):
    """
    Recorre recursivamente un objeto (diccionario o lista) y reemplaza
    todos los valores `None` con un string vacío "".
    """
    if isinstance(obj, dict):
        # Si es un diccionario, itera sobre sus items
        return {k: reemplazar_none_con_vacio(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Si es una lista, itera sobre sus elementos
        return [reemplazar_none_con_vacio(elem) for elem in obj]
    # Si el valor es None, lo reemplaza. Si no, lo deja como está.
    return "" if obj is None else obj

# ==============================================================================
# FUNCIÓN DE UNIÓN PULIDA Y ROBUSTA
# ==============================================================================
def unificar_info_empresa_produccion(ruc: str) -> dict:
    """
    Consulta información de un RUC en el SRI y Supercias, unifica los datos de
    forma segura y prepara el resultado para su uso en una aplicación.

    Características:
    - Es robusto ante fallos en las fuentes de datos (si una falla, devuelve los datos de la otra).
    - Reemplaza todos los valores `None` por strings vacíos ("") para una integración
      más sencilla con aplicaciones web.
    - Devuelve siempre un diccionario, aunque esté vacío si ambas fuentes fallan.

    Args:
        ruc (str): El número de RUC a consultar.

    Returns:
        dict: Un diccionario con la información combinada y limpia.
    """
    # 1. Obtener la información de ambas fuentes
    info_sri_raw = consultar_ruc_sri(ruc)
    info_supercias_raw = obtener_informacion_compania(ruc)

    # 2. Inicializar diccionarios como vacíos para garantizar una operación segura
    sri_dict = {}
    supercias_dict = {}

    # 3. Validar y procesar datos del SRI
    if isinstance(info_sri_raw, list) and info_sri_raw:
        # Asegurarse de que el primer elemento también sea un diccionario
        if isinstance(info_sri_raw[0], dict):
            sri_dict = info_sri_raw[0]

    # 4. Validar y procesar datos de Supercias
    if isinstance(info_supercias_raw, dict):
        supercias_dict = info_supercias_raw

    # 5. Combinar los diccionarios. Esta operación ahora es 100% segura.
    # El orden importa: las claves de supercias_dict sobreescribirán las de sri_dict si coinciden.
    info_unida = sri_dict | supercias_dict
    
    # 6. Si no se obtuvo nada de ninguna fuente, devolver un diccionario vacío.
    if not info_unida:
        return {}

    # 7. Limpiar el resultado final reemplazando todos los None con ""
    resultado_limpio = reemplazar_none_con_vacio(info_unida)

    return resultado_limpio