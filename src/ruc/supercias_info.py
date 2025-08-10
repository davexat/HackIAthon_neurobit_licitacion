import requests
import easyocr
import cv2
import os

# Función para obtener el CAPTCHA y los datos
def obtener_informacion_compania(ruc):
    try:
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "host": "appscvsgen.supercias.gob.ec"
        }

        # Iniciar sesión
        sesion = requests.Session()

        # Obtener el ViewState inicial
        _req = sesion.get("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", headers=headers)
        html = _req.text
        print("Inicio")

        # Extraer el ViewState
        indiceView = html.find("j_id1:javax.faces.ViewState:0")
        if indiceView > -1:
            indexValueInicio = html.find("value=", indiceView)
            indexValueFin = html.find("\"", indexValueInicio + 7)
            view = html[indexValueInicio + 7:indexValueFin]
            view = view.replace(":", "%3A")

        dtSesion = sesion.cookies.get_dict()

        # Solicitar tipo de búsqueda
        print("Cambiar a búsqueda por RUC")
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "cookie": "JSESSIONID=" + dtSesion["JSESSIONID"],
            "referer": "https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf"
        }

        payload = f"javax.faces.partial.ajax=true&javax.faces.source=frmBusquedaCompanias%3AtipoBusqueda&javax.faces.partial.execute=frmBusquedaCompanias%3AtipoBusqueda&javax.faces.partial.render=frmBusquedaCompanias%3AparametroBusqueda+frmBusquedaCompanias%3ApanelCompaniaSeleccionada+frmBusquedaCompanias%3ApanelCaptcha+frmBusquedaCompanias%3AbtnConsultarCompania&javax.faces.behavior.event=valueChange&javax.faces.partial.event=change&frmBusquedaCompanias%3AtipoBusqueda=2&javax.faces.ViewState={view}"
        _req = sesion.post("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", data=payload, headers=headers)

        # Enviar la consulta con el RUC
        payload = f"javax.faces.partial.ajax=true&javax.faces.source=frmBusquedaCompanias%3AparametroBusqueda&javax.faces.partial.execute=frmBusquedaCompanias%3AparametroBusqueda&javax.faces.partial.render=frmBusquedaCompanias%3AparametroBusqueda&frmBusquedaCompanias%3AparametroBusqueda_query={ruc}&frmBusquedaCompanias=frmBusquedaCompanias&frmBusquedaCompanias%3AtipoBusqueda=2&frmBusquedaCompanias%3AparametroBusqueda_input={ruc}&frmBusquedaCompanias%3Abrowser=Chrome&frmBusquedaCompanias%3AaltoBrowser=372&frmBusquedaCompanias%3AanchoBrowser=1536&frmBusquedaCompanias%3AmenuDispositivoMovil=hidden&javax.faces.ViewState={view}"
        _req = sesion.post("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", data=payload, headers=headers)
        html = _req.text

        # Obtener el nombre de la compañía
        indiceNombre = html.find("data-item-value=")
        id_nombre = ""
        if indiceNombre > -1:
            indexValueFin = html.find("\"", indiceNombre + 17)
            id_nombre = html[indiceNombre + 17:indexValueFin]
            id_nombre = id_nombre.replace(" ", "+")

        # Solicitar imagen del CAPTCHA
        payload = f"javax.faces.partial.ajax=true&javax.faces.source=frmBusquedaCompanias%3AparametroBusqueda&javax.faces.partial.execute=frmBusquedaCompanias%3AparametroBusqueda&javax.faces.partial.render=frmBusquedaCompanias%3AparametroBusqueda+frmBusquedaCompanias%3ApanelCompaniaSeleccionada+frmBusquedaCompanias%3ApanelCaptcha+frmBusquedaCompanias%3AbtnConsultarCompania&javax.faces.behavior.event=itemSelect&javax.faces.partial.event=itemSelect&frmBusquedaCompanias%3AparametroBusqueda_itemSelect={id_nombre}&frmBusquedaCompanias%3AparametroBusqueda_input={id_nombre}&javax.faces.ViewState={view}"
        _req = sesion.post("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", data=payload, headers=headers)

        html = _req.text
        indicesrc = html.find("src=")
        if indicesrc > -1:
            indexValueFin = html.find("\"", indicesrc + 5)
            imgcaptcha = html[indicesrc + 5:indexValueFin]

            urlimge = "https://appscvsgen.supercias.gob.ec" + imgcaptcha
            print(urlimge)
            _reqimg = sesion.get(urlimge, headers=headers)

            # Guardar la imagen del CAPTCHA
            buffer = _reqimg.content
            rutaimg = "imgtemp.png"  # Guardar la imagen localmente

            with open(rutaimg, "wb") as f:
                f.write(buffer)

            if os.path.isfile(rutaimg):
                print("Procesando imagen del CAPTCHA")
                gray = cv2.imread(rutaimg, 0)
                thresholded = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                reader = easyocr.Reader(['en'])
                result = reader.readtext(thresholded, detail=0, paragraph=True)

                captcha = result[0].replace(" ", "")
                print(captcha)

                # Enviar CAPTCHA resuelto
                payload = f"javax.faces.partial.ajax=true&javax.faces.source=frmBusquedaCompanias%3AbtnConsultarCompania&javax.faces.partial.execute=frmBusquedaCompanias%3AbtnConsultarCompania+frmBusquedaCompanias%3Acaptcha+frmBusquedaCompanias%3Abrowser+frmBusquedaCompanias%3AaltoBrowser+frmBusquedaCompanias%3AanchoBrowser+frmBusquedaCompanias%3AmenuDispositivoMovil&frmBusquedaCompanias%3AbtnConsultarCompania=frmBusquedaCompanias%3AbtnConsultarCompania&frmBusquedaCompanias%3Acaptcha={captcha}&frmBusquedaCompanias%3Abrowser=Chrome&frmBusquedaCompanias%3AaltoBrowser=614&frmBusquedaCompanias%3AanchoBrowser=1536&frmBusquedaCompanias%3AmenuDispositivoMovil=hidden&javax.faces.ViewState={view}"
                _req = sesion.post("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf", data=payload, headers=headers, allow_redirects=True)

                if _req.status_code == 200:
                    print("*" * 10)
                    _req = sesion.get("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/informacionCompanias.jsf", headers=headers, allow_redirects=True)
                    rptaJson = procesar_informacion(_req.text)
                    print(rptaJson)

    except Exception as e:
        print(f"Error: {e}")

def extract_from_textarea(html, textarea_id):
    """
    Busca una etiqueta textarea por su id y extrae el texto que contiene.
    """
    # Construimos el identificador único del textarea
    search_str = f'id="{textarea_id}"'
    
    # Encontramos la posición del id
    pos_id = html.find(search_str)
    if pos_id == -1:
        return "" # No se encontró el textarea

    # A partir de la posición del id, encontramos el cierre de la etiqueta de apertura '>'
    pos_value_start = html.find('>', pos_id)
    if pos_value_start == -1:
        return ""

    # Buscamos la etiqueta de cierre '</textarea>' que le corresponde
    pos_value_end = html.find('</textarea>', pos_value_start)
    if pos_value_end == -1:
        return ""

    # Extraemos el valor, lo limpiamos y lo retornamos
    value = html[pos_value_start + 1 : pos_value_end]
    return value.strip()

# Función para procesar la información de la compañía

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

    # Fecha de constitución
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt131", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["FechaConstitucion"] = html[posvalue + 7:posvalueFin]

    # Nacionalidad
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt136", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Nacionalidad"] = html[posvalue + 7:posvalueFin]

    # Plazo social
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt141", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["PlazoSocial"] = html[posvalue + 7:posvalueFin]

    # Oficina de control
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt146", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["OficinaControl"] = html[posvalue + 7:posvalueFin]

    # Tipo de compañía
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt151", posInicio)
    if posInicio > -1:
        posvalue = html.find(">", posInicio)
        posvalueFin = html.find("<", posvalue + 1)
        dtEmpres["TipoConpania"] = html[posvalue + 1:posvalueFin]

    # Situación legal
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt156", posInicio)
    if posInicio > -1:
        posvalue = html.find(">", posInicio)
        posvalueFin = html.find("<", posvalue + 1)
        dtEmpres["situacionLegal"] = html[posvalue + 1:posvalueFin]

    # Provincia
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt167", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Provincia"] = html[posvalue + 7:posvalueFin].strip()

    # Cantón
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt172", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Canton"] = html[posvalue + 7:posvalueFin].strip()

    # Ciudad
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt177", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Ciudad"] = html[posvalue + 7:posvalueFin]

    # Parroquia
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt182", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Parroquia"] = html[posvalue + 7:posvalueFin]

    # Calle
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt187", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Calle"] = html[posvalue + 7:posvalueFin]

    # Número
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt192", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Numero"] = html[posvalue + 7:posvalueFin]

    # Intersección
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt197", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Interseccion"] = html[posvalue + 7:posvalueFin]

    # Ciudadela
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt202", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Ciudadela"] = html[posvalue + 7:posvalueFin]

    # Conjunto
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt207", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Conjunto"] = html[posvalue + 7:posvalueFin]

    # Referencia
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt242", posInicio)
    if posInicio > -1:
        posvalue = html.find("value=", posInicio)
        posvalueFin = html.find("\"", posvalue + 7)
        dtEmpres["Referencia"] = html[posvalue + 7:posvalueFin]

    # Casillero Postal
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt253", posInicio)
    dtEmpres["CasilleroPostal"] = ""
    if posInicio > -1:
        posvalue = html.find("/>", posInicio)
        temp = html[posInicio:posvalue]
        posvaluetemp = temp.find("value=")
        if posvaluetemp > -1:
            posvalue = html.find("value=", posInicio)
            posvalueFin = html.find("\"", posvalue + 7)
            dtEmpres["CasilleroPostal"] = html[posvalue + 7:posvalueFin]

    # Celular
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt258", posInicio)
    dtEmpres["Celular"] = ""
    if posInicio > -1:
        posvalue = html.find("/>", posInicio)
        temp = html[posInicio:posvalue]
        posvaluetemp = temp.find("value=")
        if posvaluetemp > -1:
            posvalue = html.find("value=", posInicio)
            posvalueFin = html.find("\"", posvalue + 7)
            dtEmpres["Celular"] = html[posvalue + 7:posvalueFin]

    # Telefono1
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt263", posInicio)
    dtEmpres["Telefono1"] = ""
    if posInicio > -1:
        posvalue = html.find("/>", posInicio)
        temp = html[posInicio:posvalue]
        posvaluetemp = temp.find("value=")
        if posvaluetemp > -1:
            posvalue = html.find("value=", posInicio)
            posvalueFin = html.find("\"", posvalue + 7)
            dtEmpres["Telefono1"] = html[posvalue + 7:posvalueFin].strip()

    # Telefono2
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt268", posInicio)
    dtEmpres["Telefono2"] = ""
    if posInicio > -1:
        posvalue = html.find("/>", posInicio)
        temp = html[posInicio:posvalue]
        posvaluetemp = temp.find("value=")
        if posvaluetemp > -1:
            posvalue = html.find("value=", posInicio)
            posvalueFin = html.find("\"", posvalue + 7)
            dtEmpres["Telefono2"] = html[posvalue + 7:posvalueFin]

    # Sitio Web
    posInicio = html.find("frmInformacionCompanias:j_idt110:j_idt273", posInicio)
    dtEmpres["SitioWeb"] = ""
    if posInicio > -1:
        posvalue = html.find("/>", posInicio)
        temp = html[posInicio:posvalue]
        posvaluetemp = temp.find("value=")
        if posvaluetemp > -1:
            posvalue = html.find("value=", posInicio)
            posvalueFin = html.find("\"", posvalue + 7)
            dtEmpres["SitioWeb"] = html[posvalue + 7:posvalueFin]

    # --- INICIO DEL CÓDIGO MODIFICADO PARA CIIU ---

    dtEmpres["ActividadesCIIU"] = []
    actividades = []
    
    # Usaremos una variable para saber dónde continuar la búsqueda en el HTML
    posicion_actual = 0

    # 1. Extraer la Actividad Principal
    # Buscamos la etiqueta de texto que es nuestra "ancla"
    label_principal = "CIIU actividad principal:"
    pos_label_p = html.find(label_principal, posicion_actual)
    
    if pos_label_p > -1:
        # A partir de la etiqueta, encontramos el textarea del CÓDIGO
        pos_textarea_open_p = html.find('<textarea', pos_label_p)
        pos_value_start_p = html.find('>', pos_textarea_open_p)
        pos_value_end_p = html.find('</textarea>', pos_value_start_p)
        ciiu_codigo = html[pos_value_start_p + 1 : pos_value_end_p].strip()
        
        # Ahora, buscamos la etiqueta "Descripción:" DESPUÉS de haber encontrado el código
        label_descripcion = "Descripción:"
        pos_label_desc = html.find(label_descripcion, pos_value_end_p)
        
        # Y encontramos el textarea de la DESCRIPCIÓN
        pos_textarea_open_d = html.find('<textarea', pos_label_desc)
        pos_value_start_d = html.find('>', pos_textarea_open_d)
        pos_value_end_d = html.find('</textarea>', pos_value_start_d)
        ciiu_descripcion = html[pos_value_start_d + 1 : pos_value_end_d].strip()

        # Si encontramos un código, lo añadimos a la lista
        if ciiu_codigo:
            actividades.append({
                "Tipo": "Principal",
                "CIIU": ciiu_codigo,
                "Descripcion": ciiu_descripcion
            })
        
        # Actualizamos nuestra posición para la siguiente búsqueda
        posicion_actual = pos_value_end_d

    # 2. Extraer las Actividades Complementarias
    for i in range(1, 6):
        label_complementaria = f"CIIU actividad complementaria {i}:"
        pos_label_c = html.find(label_complementaria, posicion_actual)
        
        if pos_label_c > -1:
            # Encontramos el textarea del CÓDIGO complementario
            pos_textarea_open_c = html.find('<textarea', pos_label_c)
            pos_value_start_c = html.find('>', pos_textarea_open_c)
            pos_value_end_c = html.find('</textarea>', pos_value_start_c)
            ciiu_codigo_comp = html[pos_value_start_c + 1 : pos_value_end_c].strip()
            
            # Buscamos la "Descripción:" DESPUÉS del código complementario
            pos_label_desc_c = html.find(label_descripcion, pos_value_end_c)
            
            # Y el textarea de la DESCRIPCIÓN complementaria
            pos_textarea_open_d_c = html.find('<textarea', pos_label_desc_c)
            pos_value_start_d_c = html.find('>', pos_textarea_open_d_c)
            pos_value_end_d_c = html.find('</textarea>', pos_value_start_d_c)
            ciiu_descripcion_comp = html[pos_value_start_d_c + 1 : pos_value_end_d_c].strip()

            # Si el código no está vacío, lo añadimos
            if ciiu_codigo_comp:
                actividades.append({
                    "Tipo": f"Complementaria {i}",
                    "CIIU": ciiu_codigo_comp,
                    "Descripcion": ciiu_descripcion_comp
                })
            
            # Actualizamos la posición para buscar la siguiente actividad complementaria
            posicion_actual = pos_value_end_d_c
        else:
            # Si no encontramos "actividad complementaria 1", salimos del bucle
            # para no seguir buscando la 2, 3, etc.
            break
            
    dtEmpres["ActividadesCIIU"] = actividades

    # Buscar el valor de "Capital suscrito" en el HTML
    posInicio = html.find("Capital suscrito:")
    if posInicio > -1:
        # Buscar el valor después de "Capital suscrito:"
        posvalueInicio = html.find('value="', posInicio)
        if posvalueInicio > -1:
            posvalueFin = html.find('"', posvalueInicio + 7)
            capital_suscrito = html[posvalueInicio + 7:posvalueFin].strip()
            # Agregarlo a dtEmpres
            dtEmpres["CapitalSuscrito"] = capital_suscrito

    return dtEmpres


# --- Ejecución ---
if __name__ == "__main__":
    ruc_a_consultar = "0990004196001"  # El RUC que deseas consultar
    obtener_informacion_compania(ruc_a_consultar)
