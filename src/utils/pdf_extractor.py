"""
Módulo mejorado para extracción de texto de PDFs con soporte para:
- Extracción precisa de documentos de licitaciones
- Manejo avanzado de tablas y formatos complejos
- Filtrado de ruido institucional
- Corrección de errores comunes en documentos técnicos
"""

import os
import re
import io
import platform
from typing import Optional, List, Dict
from PIL import Image
import fitz
import pdfplumber
import pytesseract
import pandas as pd

class PDFTextExtractor:
    """
    Clase mejorada para extraer texto de documentos PDF, especialmente optimizada para:
    - Documentos de contratación pública
    - Pliegos de licitación
    - Documentos con estructura compleja
    
    Args:
        tesseract_path (str, optional): Ruta personalizada al ejecutable de Tesseract OCR.
        table_settings (dict, optional): Configuración personalizada para extracción de tablas.
    """
    
    def __init__(self, tesseract_path: Optional[str] = None, 
                 table_settings: Optional[Dict] = None):
        self._configure_tesseract(tesseract_path)
        self.table_settings = table_settings or {
            "vertical_strategy": "lines", 
            "horizontal_strategy": "lines",
            "intersection_y_tolerance": 15,
            "intersection_x_tolerance": 15
        }
        # Patrones específicos para documentos de licitación
        self.licitacion_patterns = {
            'section_header': r'^(SECCI[OÓ]N|CAP[IÍ]TULO)\s+[IVXLCDM]+\s*[-:]?\s*(.*)$',
            'subsection': r'^\d+\.\d+\.?\s*(.*)$',
            'item': r'^\d+\.\d+\.\d+\.?\s*(.*)$'
        }
    
    def _configure_tesseract(self, tesseract_path: Optional[str] = None) -> None:
        """Configura el path de Tesseract OCR con verificación mejorada."""
        if tesseract_path:
            if not os.path.exists(tesseract_path):
                raise FileNotFoundError(f"Tesseract no encontrado en: {tesseract_path}")
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            # Rutas comunes por sistema operativo
            paths_by_os = {
                "Windows": [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
                ],
                "Linux": ["/usr/bin/tesseract"],
                "Darwin": ["/usr/local/bin/tesseract"]
            }
            
            # Probar rutas hasta encontrar una válida
            for path in paths_by_os.get(platform.system(), []):
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    return
            
            raise pytesseract.TesseractNotFoundError(
                "No se pudo encontrar Tesseract OCR. Por favor especifique la ruta manualmente."
            )
    
    def extract_text(self, pdf_path: str, use_ocr: bool = False, 
                    extract_tables: bool = True) -> Dict[str, str]:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo {pdf_path} no existe")
        
        try:
            result = {
                'text': '',
                'tables': [],
                'metadata': self._extract_metadata(pdf_path)
            }
            
            # Extracción de texto principal (aseguramos string)
            text = self._ensure_str(self._extract_with_fitz(pdf_path))
            
            # OCR complementario si es necesario
            if use_ocr or self._needs_ocr(text):
                ocr_text = self._ensure_str(self._extract_with_ocr(pdf_path))
                if ocr_text.strip():
                    text += "\n" + ocr_text
            
            # Procesamiento especial para documentos de licitación
            text = self._process_licitacion_text(text)
            
            # Extracción de tablas (manejo seguro)
            if extract_tables:
                tables = self._extract_tables_advanced(pdf_path)
                result['tables'] = tables
                table_text = self._ensure_str(self._format_tables_for_text(tables))
                if table_text.strip():
                    text += "\n" + table_text
 
            result['text'] = self._clean_text(self._ensure_str(text))
            return result
            
        except Exception as e:
            # Propagar con la traza real para debug si quieres, pero mantenemos el mensaje como antes
            raise Exception(f"Error al procesar {pdf_path}: {str(e)}")


    
    def _needs_ocr(self, text: str, threshold: int = 100) -> bool:
        """Determina si el texto extraído necesita OCR complementario."""
        # Eliminar espacios y saltos de línea para evaluación
        clean_text = re.sub(r'\s+', '', text)
        return len(clean_text) < threshold
    
    def _extract_metadata(self, pdf_path: str) -> Dict:
        """Extrae metadatos básicos del PDF."""
        with fitz.open(pdf_path) as doc:
            return {
                'pages': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'creation_date': doc.metadata.get('creationDate', '')
            }
    

    
    def _extract_with_ocr(self, pdf_path: str) -> str:
        """OCR robusto: intenta spa, hace fallback y evita errores de permiso cerrando imágenes."""
        ocr_text = ""

        # Intentar asegurar variables de entorno y comando
        # Ajusta la ruta si tu tesseract está en otra carpeta
        possible_tess_base = r"C:\Program Files\Tesseract-OCR"
        if os.path.exists(possible_tess_base):
            os.environ.setdefault('TESSDATA_PREFIX', os.path.join(possible_tess_base, "tessdata"))
            pytesseract.pytesseract.tesseract_cmd = os.path.join(possible_tess_base, "tesseract.exe")

        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=300)

                # Generar bytes PNG en memoria y abrir con contexto para asegurar cierre
                img_bytes = pix.tobytes("png")
                try:
                    with Image.open(io.BytesIO(img_bytes)) as img:
                        # Forzar a RGB por seguridad (evita ciertos problemas con tesseract)
                        img = img.convert("RGB")

                        # Intento principal: idioma español
                        raw = ""
                        try:
                            raw = pytesseract.image_to_string(img, lang='spa', config='--oem 3 --psm 3')
                        except Exception as e_spa:
                            # Aviso y fallback: intentar sin especificar idioma o con 'eng'
                            print(f"[OCR WARN] spa failed on page {page_num+1}: {repr(e_spa)} -- intentando fallback...")
                            try:
                                raw = pytesseract.image_to_string(img, config='--oem 3 --psm 3')
                            except Exception as e_fallback:
                                print(f"[OCR ERROR] fallback also failed on page {page_num+1}: {repr(e_fallback)}")
                                raw = ""

                        # Filtrar y asegurar string
                        filtered = self._filter_licitacion_content(raw)
                        filtered = self._ensure_str(filtered)

                        ocr_text += filtered + "\n"

                except PermissionError as perr:
                    # Mensaje claro para que cierres cualquier visor de PDF o proceso que bloquee el archivo
                    print(f"[PERMISSION ERROR] No se pudo procesar la página {page_num+1}: {perr}")
                    print("Cierra cualquier visor/editor que esté usando el PDF y vuelve a intentarlo.")
                    # continuamos a la siguiente página en vez de romper todo
                    continue
                except Exception as e:
                    print(f"[UNEXPECTED ERROR] página {page_num+1}: {repr(e)}")
                    continue

        return ocr_text


    
    def _filter_licitacion_content(self, text: str) -> str:
        """
        Filtra contenido específico de documentos de licitación:
        - Encabezados/pies de página institucionales
        - Números de página
        - Ruido común en estos documentos
        """

        text = self._ensure_str(text)

        # Patrones comunes en documentos de licitación ecuatoriana
        patterns_to_filter = [
            # Patrones SERCOP
            r'DIRECCI[OÓ]N:.*PLATAFORMA GUBERNAMENTAL.*QUITO-ECUADOR',
            r'SERCOP.*SERVICIO NACIONAL DE CONTRATACI[OÓ]N P[UÚ]BLICA',
            r'GOBIERNO.*ECUADOR',
            r'C[OÓ]DIGO POSTAL:\s*\d{6}',
            
            # Números de página
            r'^\s*\d+\s*$',
            
            # Ruido común
            r'^\s*-\s*$',
            r'^\s*\.+\s*$',
            r'^\s*[_\-=]+\s*$'
        ]
        
        if not isinstance(text, str):
            text = " ".join(str(x) for x in text)

        filtered_lines = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
                
            # Verificar si la línea coincide con patrones a filtrar
            should_filter = any(re.search(pattern, line, re.IGNORECASE) 
                              for pattern in patterns_to_filter)
            
            if not should_filter:
                filtered_lines.append(line)
        
        return "\n".join(filtered_lines)
    
    def _process_licitacion_text(self, text: str) -> str:
        """
        Procesa texto de licitaciones para:
        - Identificar y marcar secciones
        - Corregir errores comunes
        - Estructurar el contenido
        """
        # Corrección de errores comunes en OCR de documentos técnicos
        corrections = {
            r'(\w)\s*-\s*(\w)': r'\1-\2',  # Unir palabras separadas incorrectamente
            r'ﬁ': 'fi',
            r'ﬀ': 'ff',
            r'ﬂ': 'fl',
            r'(\d)\s+(\d)': r'\1\2',  # Unir números separados
            r'\b([A-Z])\s+([A-Z])\b': r'\1\2',  # Unir siglas
            r'\b(\d+)\s*\.\s*(\d+)\b': r'\1.\2',  # Decimales mal separados
            r'\b([a-z])\s+([a-z])\b': r'\1\2',  # Unir palabras cortadas
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text)
        
        # Identificación de estructura del documento
        lines = text.splitlines()
        processed_lines = []
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detección de secciones y subsecciones
            section_match = re.match(self.licitacion_patterns['section_header'], line)
            subsection_match = re.match(self.licitacion_patterns['subsection'], line)
            item_match = re.match(self.licitacion_patterns['item'], line)
            
            if section_match:
                current_section = f"\nSECCIÓN {section_match.group(1).strip()}: {section_match.group(2).strip()}\n"
                processed_lines.append(current_section)
            elif subsection_match:
                processed_lines.append(f"\nSubsección: {subsection_match.group(1).strip()}\n")
            elif item_match:
                processed_lines.append(f"• {item_match.group(1).strip()}")
            else:
                processed_lines.append(line)
        
        return "\n".join(processed_lines)
    
    def _extract_with_fitz(self, pdf_path: str) -> str:
        """Extrae texto usando PyMuPDF (fitz) con manejo mejorado de formatos."""
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        return text

    def _ensure_str(self, value) -> str:
        """
        Garantiza que 'value' se convierta a str de forma segura.
        - Si es str, lo devuelve.
        - Si es lista/tuple, une sus elementos por saltos de línea (recursivo).
        - Para otros tipos, hace str(value) con fallback a '' si falla.
        """
        if isinstance(value, str):
            return value
        if isinstance(value, (list, tuple)):
            return "\n".join(self._ensure_str(x) for x in value)
        try:
            return str(value)
        except Exception:
            return ""


    def _extract_tables_advanced(self, pdf_path: str) -> List[Dict]:
        """
        Extrae tablas con manejo mejorado para formatos complejos de licitaciones.
        
        Returns:
            Lista de diccionarios con:
            - 'page': Número de página
            - 'table': Datos de la tabla (lista de listas)
        """
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extraer tablas con configuración personalizada
                page_tables = page.extract_tables(self.table_settings)
                
                for table_data in page_tables:
                    # Limpieza de celdas
                    cleaned_table = []
                    for row in table_data:
                        cleaned_row = [
                            self._clean_table_cell(cell) if cell is not None else ""
                            for cell in row
                        ]
                        cleaned_table.append(cleaned_row)
                    
                    # Solo agregar tablas con contenido válido
                    if any(any(cell.strip() for cell in row) for row in cleaned_table):
                        tables.append({
                            'page': page_num + 1,
                            'table': cleaned_table
                        })
        
        return tables


    
    def _clean_table_cell(self, cell: str) -> str:
        """Limpia el contenido de una celda de tabla."""
        if not cell:
            return ""
        
        # Normalizar espacios y saltos de línea
        cell = re.sub(r'\s+', ' ', str(cell)).strip()
        # Eliminar caracteres especiales pero preservar símbolos importantes
        cell = re.sub(r'[^\w\s\-$%.,;:()/\'"&@#]', '', cell)
        return cell
    
    def _format_tables_for_text(self, tables: List[Dict]) -> str:
        """Formatea las tablas extraídas para inclusión en el texto plano."""
        table_text = ""
        for i, table_data in enumerate(tables, 1):
            table_text += f"\n\nTABLA {i} (Página {table_data['page']}):\n"
            
            # Convertir a DataFrame para manejo más fácil
            df = pd.DataFrame(table_data['table'])
            
            # Formatear como texto con alineación
            for _, row in df.iterrows():
                formatted_row = " | ".join(f"{str(cell):<30}" for cell in row)
                table_text += formatted_row + "\n"
        
        return table_text
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Limpia y normaliza el texto extraído con reglas específicas para licitaciones."""
        # Normalización de espacios
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Unir líneas que probablemente fueron separadas incorrectamente
        text = re.sub(r'(\w)-\s+(\w)', r'\1-\2', text)  # Palabras con guiones
        text = re.sub(r'([a-z])\s+([A-Z])', r'\1 \2', text)  # Evitar unir párrafos
        
        # Eliminar caracteres no imprimibles pero preservar símbolos importantes
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    

        
        # Corrección de encodings comunes
        replacements = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
            'Ã±': 'ñ', 'Ã': 'Ñ', 'Â°': '°', 'â€“': '-', 'â€œ': '"',
            'â€': '"', 'â€™': "'", 'â€¢': '-'
        }
        
        for wrong, right in replacements.items():
            text = text.replace(wrong, right)
        
        return text


# Función de conveniencia mejorada
def extract_text_from_pdf(pdf_path: str, use_ocr: bool = False, 
                         extract_tables: bool = True) -> Dict[str, str]:
    """
    Función helper mejorada para extraer texto de un PDF con opciones configurables.
    
    Args:
        pdf_path: Ruta al archivo PDF.
        use_ocr: Si True, fuerza el uso de OCR.
        extract_tables: Si True, extrae y procesa tablas por separado.
        
    Returns:
        Diccionario con texto estructurado y tablas.
    """
    extractor = PDFTextExtractor()
    return extractor.extract_text(pdf_path, use_ocr, extract_tables)