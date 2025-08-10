import requests

def consultar_ruc_sri(ruc):
    """
    Consulta la información de un RUC en el SRI.

    Args:
        ruc (str): El número de RUC a consultar.

    Returns:
        dict or None: Un diccionario con la información del RUC si la consulta es exitosa y
                      la respuesta es JSON válido, de lo contrario, None.
    """
    url = f"https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/ConsolidadoContribuyente/obtenerPorNumerosRuc?&ruc={ruc}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Lanza una excepción para códigos de estado de error (4xx o 5xx)

        # Intenta parsear la respuesta como JSON
        try:
            data = response.json()
            return data
        except requests.exceptions.JSONDecodeError:
            print("La respuesta no es un JSON válido.")
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la petición: {e}")
        return None

if __name__ == '__main__':
    # Ejemplo de uso de la función:
    ruc_ingresado = str(input("Ingrese un RUC: "))
    informacion_ruc = consultar_ruc_sri(ruc_ingresado)

    if informacion_ruc:
        print("Información del RUC:")
        print(informacion_ruc)
    else:
        print("No se pudo obtener información para el RUC proporcionado.")