"""
Módulo para extracción de texto de PDFs con soporte para OCR y manejo de tablas

Funcionalidades:
- Extracción de texto nativo de PDFs
- Reconocimiento óptico de caracteres (OCR) para PDFs escaneados
- Extracción de datos tabulares
- Procesamiento multiplataforma
"""

import os
import re
import io
import platform
from typing import Optional
from PIL import Image

import pymupdf as fitz
import fitz
import pdfplumber
import pytesseract

class PDFTextExtractor:
    """
    Clase para extraer texto de documentos PDF, con soporte para OCR cuando sea necesario.
    
    Args:
        tesseract_path (str, optional): Ruta personalizada al ejecutable de Tesseract OCR.
                       Si no se especifica, intentará autodetectar la ubicación.
    """
    
    def __init__(self, tesseract_path: Optional[str] = None):
        self._configure_tesseract(tesseract_path)
    
    def _configure_tesseract(self, tesseract_path: Optional[str] = None) -> None:
        """Configura el path de Tesseract OCR automáticamente según el sistema operativo."""
        if tesseract_path:
            if not os.path.exists(tesseract_path):
                raise FileNotFoundError(f"Tesseract no encontrado en: {tesseract_path}")
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        else:
            try:
                # Verifica si ya está en PATH
                pytesseract.get_tesseract_version()
            except pytesseract.TesseractNotFoundError:
                # Configuración automática por SO
                if platform.system() == "Windows":
                    default_win = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                    if os.path.exists(default_win):
                        pytesseract.pytesseract.tesseract_cmd = default_win
                elif platform.system() == "Linux":
                    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
                elif platform.system() == "Darwin":  # macOS
                    pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"
    
    def extract_text(self, pdf_path: str, use_ocr: bool = False) -> str:
        """
        Extrae texto de un archivo PDF.
        
        Args:
            pdf_path: Ruta al archivo PDF.
            use_ocr: Si True, fuerza el uso de OCR incluso si hay texto seleccionable.
            
        Returns:
            Texto extraído del PDF.
            
        Raises:
            FileNotFoundError: Si el PDF no existe.
            Exception: Si ocurre un error durante el procesamiento.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"El archivo {pdf_path} no existe")
        
        try:
            if use_ocr:
                return self._extract_with_ocr(pdf_path)
            
            # Extracción primaria con PyMuPDF
            text = self._extract_with_fitz(pdf_path)
            
            # Si el texto es muy corto, intentar con OCR
            if len(text.strip()) < 100:
                text += "\n" + self._extract_with_ocr(pdf_path)
            
            # Complementar con pdfplumber para tablas
            text += "\n" + self._extract_with_pdfplumber(pdf_path)
            
            return self._clean_text(text)
        
        except Exception as e:
            raise Exception(f"Error al procesar {pdf_path}: {str(e)}")
    
    def _extract_with_fitz(self, pdf_path: str) -> str:
        """Extrae texto usando PyMuPDF (fitz)."""
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() or ""
        return text
    
    def _extract_with_ocr(self, pdf_path: str) -> str:
        """Extrae texto de PDFs escaneados usando OCR."""
        ocr_text = ""
        with fitz.open(pdf_path) as doc:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                ocr_text += pytesseract.image_to_string(img) + "\n"
        return ocr_text
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extrae texto y tablas usando pdfplumber."""
        plumber_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extraer texto con layout preservado
                text = page.extract_text(layout=True, x_density=8, y_density=2)
                plumber_text += text or ""
                
                # Extraer tablas
                for table in page.extract_tables():
                    for row in table:
                        plumber_text += " | ".join(str(cell).strip() for cell in row if cell) + "\n"
        return plumber_text
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Limpia y normaliza el texto extraído."""
        # Normalizar espacios y saltos de línea
        text = re.sub(r'\s+', ' ', text).strip()
        # Eliminar caracteres no imprimibles
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        return text


# Función de conveniencia para uso rápido
def extract_text_from_pdf(pdf_path: str, use_ocr: bool = False) -> str:
    """
    Función helper para extraer texto de un PDF sin necesidad de instanciar la clase.
    
    Args:
        pdf_path: Ruta al archivo PDF.
        use_ocr: Si True, fuerza el uso de OCR.
        
    Returns:
        Texto extraído del PDF.
    """
    extractor = PDFTextExtractor()
    return extractor.extract_text(pdf_path, use_ocr)