import requests

ruc = str(input("Ingrese un RUC: "))

sri_info = {}

url = f"https://srienlinea.sri.gob.ec/sri-catastro-sujeto-servicio-internet/rest/ConsolidadoContribuyente/obtenerPorNumerosRuc?&ruc={ruc}" # Reemplaza con un RUC de ejemplo válido
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Lanza una excepción para códigos de estado de error (4xx o 5xx)

    # Intenta parsear la respuesta como JSON
    try:
        sri_info = response.json()
        print("Respuesta JSON:")
        print(sri_info)
    except requests.exceptions.JSONDecodeError:
        print("La respuesta no es un JSON válido. Contenido de la respuesta:")
        print(response.text)

except requests.exceptions.RequestException as e:
    print(f"Error al realizar la petición: {e}")