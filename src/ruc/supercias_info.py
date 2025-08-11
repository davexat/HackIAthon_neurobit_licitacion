import requests
import os
from PIL import Image  # Para manipulación de imágenes
import io             # Para manejar bytes en memoria
import pytesseract    # El nuevo motor de OCR

# Nota: Se han eliminado las dependencias de 'easyocr' y 'cv2'.
# Asegúrate de que no haya 'import easyocr' o 'import cv2' en este archivo.

# Función para obtener el CAPTCHA y los datos
def obtener_informacion_compania(ruc):
    try:
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "host": "appscvsgen.supercias.gob.ec"
        }
        sesion = requests.Session()
        _req = sesion.get("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", headers=headers)
        html = _req.text
        print("Inicio")

        # Extraer el ViewState
        indiceView = html.find("j_id1:javax.faces.ViewState:0")
        view = ""
        if indiceView > -1:
            indexValueInicio = html.find("value=", indiceView)
            indexValueFin = html.find("\"", indexValueInicio + 7)
            view = html[indexValueInicio + 7:indexValueFin]
            view = view.replace(":", "%3A")

        dtSesion = sesion.cookies.get_dict()

        # --- Flujo de requests para obtener el CAPTCHA (sin cambios) ---
        print("Cambiar a búsqueda por RUC")
        headers_ajax = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "cookie": "JSESSIONID=" + dtSesion.get("JSESSIONID", ""),
            "referer": "https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf"
        }
        payload = f"javax.faces.partial.ajax=true&javax.faces.source=frmBusquedaCompanias%3AtipoBusqueda&javax.faces.partial.execute=frmBusquedaCompanias%3AtipoBusqueda&javax.faces.partial.render=frmBusquedaCompanias%3AparametroBusqueda+frmBusquedaCompanias%3ApanelCompaniaSeleccionada+frmBusquedaCompanias%3ApanelCaptcha+frmBusquedaCompanias%3AbtnConsultarCompania&javax.faces.behavior.event=valueChange&javax.faces.partial.event=change&frmBusquedaCompanias%3AtipoBusqueda=2&javax.faces.ViewState={view}"
        sesion.post("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", data=payload, headers=headers_ajax)
        
        payload = f"javax.faces.partial.ajax=true&javax.faces.source=frmBusquedaCompanias%3AparametroBusqueda&javax.faces.partial.execute=frmBusquedaCompanias%3AparametroBusqueda&javax.faces.partial.render=frmBusquedaCompanias%3AparametroBusqueda&frmBusquedaCompanias%3AparametroBusqueda_query={ruc}&frmBusquedaCompanias=frmBusquedaCompanias&frmBusquedaCompanias%3AtipoBusqueda=2&frmBusquedaCompanias%3AparametroBusqueda_input={ruc}&frmBusquedaCompanias%3Abrowser=Chrome&frmBusquedaCompanias%3AaltoBrowser=372&frmBusquedaCompanias%3AanchoBrowser=1536&frmBusquedaCompanias%3AmenuDispositivoMovil=hidden&javax.faces.ViewState={view}"
        _req = sesion.post("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", data=payload, headers=headers_ajax)
        html = _req.text
        
        indiceNombre = html.find("data-item-value=")
        id_nombre = ""
        if indiceNombre > -1:
            indexValueFin = html.find("\"", indiceNombre + 17)
            id_nombre = html[indiceNombre + 17:indexValueFin]
            id_nombre = id_nombre.replace(" ", "+")

        payload = f"javax.faces.partial.ajax=true&javax.faces.source=frmBusquedaCompanias%3AparametroBusqueda&javax.faces.partial.execute=frmBusquedaCompanias%3AparametroBusqueda&javax.faces.partial.render=frmBusquedaCompanias%3AparametroBusqueda+frmBusquedaCompanias%3ApanelCompaniaSeleccionada+frmBusquedaCompanias%3ApanelCaptcha+frmBusquedaCompanias%3AbtnConsultarCompania&javax.faces.behavior.event=itemSelect&javax.faces.partial.event=itemSelect&frmBusquedaCompanias%3AparametroBusqueda_itemSelect={id_nombre}&frmBusquedaCompanias%3AparametroBusqueda_input={id_nombre}&javax.faces.ViewState={view}"
        _req = sesion.post("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", data=payload, headers=headers_ajax)
        html = _req.text

        # --- INICIO DE LA LÓGICA DE OCR CORREGIDA ---
        indicesrc = html.find("src=")
        if indicesrc > -1:
            indexValueFin = html.find("\"", indicesrc + 5)
            imgcaptcha_path = html[indicesrc + 5:indexValueFin]
            urlimge = "https://appscvsgen.supercias.gob.ec" + imgcaptcha_path
            print(urlimge)
            _reqimg = sesion.get(urlimge, headers=headers)

            # Procesar la imagen directamente desde memoria, sin guardarla en disco
            buffer = _reqimg.content
            captcha = ""
            try:
                img = Image.open(io.BytesIO(buffer))
                print("Procesando imagen del CAPTCHA con Pytesseract desde memoria...")
                
                # Configuración para Tesseract: tratar la imagen como una sola línea de texto.
                custom_config = r'--oem 3 --psm 7'
                texto_extraido = pytesseract.image_to_string(img, config=custom_config)
                
                # Limpiar el resultado para obtener solo letras y números
                captcha = "".join(filter(str.isalnum, texto_extraido)).strip()
                print(f"Texto del CAPTCHA reconocido: '{captcha}'")
            
            except Exception as ocr_error:
                print(f"Error durante el procesamiento del CAPTCHA: {ocr_error}")
                return None # Falló el OCR, no se puede continuar

            # Enviar CAPTCHA resuelto
            payload = f"javax.faces.partial.ajax=true&javax.faces.source=frmBusquedaCompanias%3AbtnConsultarCompania&javax.faces.partial.execute=frmBusquedaCompanias%3AbtnConsultarCompania+frmBusquedaCompanias%3Acaptcha+frmBusquedaCompanias%3Abrowser+frmBusquedaCompanias%3AaltoBrowser+frmBusquedaCompanias%3AanchoBrowser+frmBusquedaCompanias%3AmenuDispositivoMovil&frmBusquedaCompanias%3AbtnConsultarCompania=frmBusquedaCompanias%3AbtnConsultarCompania&frmBusquedaCompanias%3Acaptcha={captcha}&frmBusquedaCompanias%3Abrowser=Chrome&frmBusquedaCompanias%3AaltoBrowser=614&frmBusquedaCompanias%3AanchoBrowser=1536&frmBusquedaCompanias%3AmenuDispositivoMovil=hidden&javax.faces.ViewState={view}"
            _req = sesion.post("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", data=payload, headers=headers_ajax, allow_redirects=True)

            if _req.status_code == 200:
                print("*" * 10)
                _req_final = sesion.get("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/informacionCompanias.jsf", headers=headers)
                rptaJson = procesar_informacion(_req_final.text)
                return rptaJson
        
        # Si no se encuentra la imagen del captcha o algo falla antes
        return None

    except Exception as e:
        print(f"Error general en obtener_informacion_compania: {e}")
        return None
# --- FIN DE LA LÓGICA DE OCR CORREGIDA ---


# --- El resto de tus funciones (procesar_informacion, etc.) sin cambios ---
# ... (Aquí va tu función procesar_informacion y las demás) ...
def procesar_informacion(html):
    dtEmpres = {}

    # Nombre de la compañía
    posInicio = html.find("barra.png")
    if posInicio > -1:
        posvalue = html.find(">", posInicio)
        posvalueFin = html.find("<", posvalue + 1)
        dtEmpres["Nombre"] = html[posvalue + 1:posvalueFin].strip()

    # Expediente
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt121")
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Expediente"] = html[posvalue + 7:posvalueFin]

    # RUC
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt126", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["RUC"] = html[posvalue + 7:posvalueFin]

    # ... (y el resto de tu lógica de parsing) ...
    
    # --- Lógica de CIIU (sin cambios) ---
    dtEmpres["ActividadesCIIU"] = []
    actividades = []
    posicion_actual = 0
    label_principal = "CIIU actividad principal:"
    pos_label_p = html.find(label_principal, posicion_actual)
    if pos_label_p > -1:
        pos_textarea_open_p = html.find('<textarea', pos_label_p)
        pos_value_start_p = html.find('>', pos_textarea_open_p)
        pos_value_end_p = html.find('</textarea>', pos_value_start_p)
        ciiu_codigo = html[pos_value_start_p + 1 : pos_value_end_p].strip()
        label_descripcion = "Descripción:"
        pos_label_desc = html.find(label_descripcion, pos_value_end_p)
        pos_textarea_open_d = html.find('<textarea', pos_label_desc)
        pos_value_start_d = html.find('>', pos_textarea_open_d)
        pos_value_end_d = html.find('</textarea>', pos_value_start_d)
        ciiu_descripcion = html[pos_value_start_d + 1 : pos_value_end_d].strip()
        if ciiu_codigo:
            actividades.append({
                "Tipo": "Principal",
                "CIIU": ciiu_codigo,
                "Descripcion": ciiu_descripcion
            })
        posicion_actual = pos_value_end_d
    for i in range(1, 6):
        label_complementaria = f"CIIU actividad complementaria {i}:"
        pos_label_c = html.find(label_complementaria, posicion_actual)
        if pos_label_c > -1:
            pos_textarea_open_c = html.find('<textarea', pos_label_c)
            pos_value_start_c = html.find('>', pos_textarea_open_c)
            pos_value_end_c = html.find('</textarea>', pos_value_start_c)
            ciiu_codigo_comp = html[pos_value_start_c + 1 : pos_value_end_c].strip()
            label_descripcion = "Descripción:" # Re-usamos la variable
            pos_label_desc_c = html.find(label_descripcion, pos_value_end_c)
            pos_textarea_open_d_c = html.find('<textarea', pos_label_desc_c)
            pos_value_start_d_c = html.find('>', pos_textarea_open_d_c)
            pos_value_end_d_c = html.find('</textarea>', pos_value_start_d_c)
            ciiu_descripcion_comp = html[pos_value_start_d_c + 1 : pos_value_end_d_c].strip()
            if ciiu_codigo_comp:
                actividades.append({
                    "Tipo": f"Complementaria {i}",
                    "CIIU": ciiu_codigo_comp,
                    "Descripcion": ciiu_descripcion_comp
                })
            posicion_actual = pos_value_end_d_c
        else:
            break
    dtEmpres["ActividadesCIIU"] = actividades

    # Capital Suscrito
    posInicio = html.find("Capital suscrito:")
    if posInicio > -1:
        posvalueInicio = html.find('value="', posInicio)
        if posvalueInicio > -1:
            posvalueFin = html.find('"', posvalueInicio + 7)
            capital_suscrito = html[posvalueInicio + 7:posvalueFin].strip()
            dtEmpres["CapitalSuscrito"] = capital_suscrito

    return dtEmpres
