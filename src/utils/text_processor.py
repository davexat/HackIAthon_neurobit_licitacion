"""
Módulo para procesamiento y análisis de texto extraído de PDFs

Funcionalidades:
- Limpieza y normalización de texto
- Extracción de entidades clave
- Detección de secciones
- Análisis de contenido relevante para licitaciones
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import datetime

@dataclass
class ContractSection:
    """Estructura para almacenar secciones identificadas del contrato"""
    name: str
    content: str
    start_pos: int
    end_pos: int

class TextProcessor:
    """
    Procesador de texto especializado para documentos contractuales de licitaciones
    
    Args:
        language (str): Idioma para procesamiento (por defecto 'es' para español)
    """
    
    def __init__(self, language: str = 'es'):
        self.language = language
        self.common_sections = {
            'es': [
                ('OBJETO DEL CONTRATO', 'objeto'),
                ('MONTO DEL CONTRATO', 'monto'),
                ('PLAZO DE EJECUCIÓN', 'plazo'),
                ('GARANTÍAS', 'garantias'),
                ('ANTICIPO', 'anticipo'),
                ('MULTAS Y PENALIZACIONES', 'multas'),
                ('RECEPCIÓN DE LA OBRA', 'recepcion'),
                ('RESOLUCIÓN DE CONTROVERSIAS', 'controversias'),
                ('LEGISLACIÓN APLICABLE', 'legislacion')
            ],
            'en': [
                ('CONTRACT OBJECTIVE', 'objective'),
                ('CONTRACT AMOUNT', 'amount'),
                ('EXECUTION PERIOD', 'period'),
                ('GUARANTEES', 'guarantees'),
                ('ADVANCE PAYMENT', 'advance'),
                ('PENALTIES', 'penalties'),
                ('WORK RECEPTION', 'reception'),
                ('DISPUTE RESOLUTION', 'disputes'),
                ('APPLICABLE LAW', 'law')
            ]
        }
    
    def clean_text(self, text: str) -> str:
        """
        Limpieza avanzada del texto extraído
        
        Args:
            text: Texto crudo a limpiar
            
        Returns:
            Texto normalizado y limpio
        """
        # Normalización de espacios y saltos de línea
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Eliminación de caracteres especiales no útiles
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Normalización de comillas y guiones
        text = re.sub(r'[“”"]', '"', text)
        text = re.sub(r'[‘’]', "'", text)
        text = re.sub(r'–', '-', text)
        
        # Corrección de palabras rotas por saltos de línea
        text = re.sub(r'(\w)-\s(\w)', r'\1\2', text)
        
        return text

    def detect_sections(self, text: str) -> List[ContractSection]:
        """
        Identifica secciones comunes en contratos de licitación
        
        Args:
            text: Texto del contrato a analizar
            
        Returns:
            Lista de secciones identificadas
        """
        sections = []
        section_patterns = self.common_sections.get(self.language, [])
        
        for pattern, section_name in section_patterns:
            # Busca el patrón en mayúsculas seguido de posible numeración (PRIMERA, 1., etc.)
            regex = re.compile(r'(?:\b[A-Z]+\b\s*–\s*)?' + re.escape(pattern) + r'\b', re.IGNORECASE)
            match = regex.search(text)
            
            if match:
                start_pos = match.start()
                # Busca el inicio de la siguiente sección
                next_section = None
                for next_pattern, _ in section_patterns:
                    if next_pattern == pattern:
                        continue
                    next_match = re.search(re.escape(next_pattern), text[start_pos+1:], re.IGNORECASE)
                    if next_match and (next_section is None or next_match.start() < next_section.start()):
                        next_section = next_match
                
                end_pos = next_section.start() + start_pos + 1 if next_section else len(text)
                content = text[start_pos:end_pos].strip()
                
                sections.append(ContractSection(
                    name=section_name,
                    content=content,
                    start_pos=start_pos,
                    end_pos=end_pos
                ))
        
        return sections

    def extract_key_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extrae entidades clave de un texto contractual
        
        Args:
            text: Texto a analizar
            
        Returns:
            Diccionario con las entidades encontradas por categoría
        """
        entities = {
            'dates': self._extract_dates(text),
            'amounts': self._extract_monetary_amounts(text),
            'percentages': self._extract_percentages(text),
            'ruc_numbers': self._extract_ruc_numbers(text),
            'clauses': self._extract_important_clauses(text)
        }
        
        return {k: v for k, v in entities.items() if v}

    def _extract_dates(self, text: str) -> List[str]:
        """Extrae fechas en formato común (dd/mm/aaaa, dd-mm-aaaa, etc.)"""
        date_patterns = [
            r'\b\d{2}[/-]\d{2}[/-]\d{4}\b',  # dd/mm/aaaa o dd-mm-aaaa
            r'\b\d{1,2}\s+(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}\b',  # 1 enero 2023
            r'\b(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{1,2},\s+\d{4}\b'  # enero 1, 2023
        ]
        
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(dates))  # Eliminar duplicados

    def _extract_monetary_amounts(self, text: str) -> List[str]:
        """Extrae montos monetarios (USD, $, etc.)"""
        amount_pattern = r'(?:USD\s*|$\s*)?\d{1,3}(?:\.\d{3})*(?:,\d{2})?\b'
        return re.findall(amount_pattern, text)

    def _extract_percentages(self, text: str) -> List[str]:
        """Extrae porcentajes"""
        return re.findall(r'\b\d{1,3}%\b', text)

    def _extract_ruc_numbers(self, text: str) -> List[str]:
        """Extrae números de RUC (Ecuador)"""
        return re.findall(r'\b\d{13}\b', text)

    def _extract_important_clauses(self, text: str) -> List[str]:
        """Identifica cláusulas importantes"""
        clause_keywords = {
            'es': ['obligatorio', 'prohibido', 'deberá', 'penalización', 'multa', 
                  'responsabilidad', 'garantía', 'terminación', 'confidencialidad'],
            'en': ['shall', 'must', 'prohibited', 'penalty', 'fine', 
                  'liability', 'warranty', 'termination', 'confidentiality']
        }
        
        keywords = clause_keywords.get(self.language, [])
        pattern = r'(?i)\b(?:' + '|'.join(keywords) + r')\b[^.!?]*[.!?]'
        return re.findall(pattern, text)

    def compare_with_bid(self, contract_text: str, bid_text: str) -> Dict[str, List[str]]:
        """
        Compara un texto de pliego con una oferta para detectar inconsistencias
        
        Args:
            contract_text: Texto del pliego de condiciones
            bid_text: Texto de la oferta/propuesta
            
        Returns:
            Diccionario con alertas de inconsistencias
        """
        contract_sections = self.detect_sections(contract_text)
        bid_sections = self.detect_sections(bid_text)
        
        alerts = {
            'missing_sections': [],
            'inconsistent_amounts': [],
            'date_discrepancies': [],
            'guarantee_issues': []
        }
        
        # 1. Verificar secciones faltantes
        contract_section_names = {s.name for s in contract_sections}
        bid_section_names = {s.name for s in bid_sections}
        alerts['missing_sections'] = list(contract_section_names - bid_section_names)
        
        # 2. Comparar montos
        contract_amounts = self._extract_monetary_amounts(contract_text)
        bid_amounts = self._extract_monetary_amounts(bid_text)
        
        if contract_amounts and bid_amounts:
            main_contract_amount = max(contract_amounts, key=lambda x: float(re.sub(r'[^\d,]', '', x).replace(',', '.')))
            main_bid_amount = max(bid_amounts, key=lambda x: float(re.sub(r'[^\d,]', '', x).replace(',', '.')))
            
            if main_contract_amount != main_bid_amount:
                alerts['inconsistent_amounts'].append(
                    f"Monto principal difiere: Pliego={main_contract_amount}, Oferta={main_bid_amount}"
                )
        
        # 3. Comparar fechas clave (plazos)
        contract_dates = self._extract_dates(contract_text)
        bid_dates = self._extract_dates(bid_text)
        
        if contract_dates and bid_dates:
            try:
                contract_last_date = max(
                    [datetime.datetime.strptime(d, '%d/%m/%Y') for d in contract_dates if re.match(r'\d{2}/\d{2}/\d{4}', d)]
                )
                bid_last_date = max(
                    [datetime.datetime.strptime(d, '%d/%m/%Y') for d in bid_dates if re.match(r'\d{2}/\d{2}/\d{4}', d)]
                )
                
                if bid_last_date > contract_last_date:
                    alerts['date_discrepancies'].append(
                        f"Plazo ofertado ({bid_last_date.strftime('%d/%m/%Y')}) "
                        f"excede el plazo del pliego ({contract_last_date.strftime('%d/%m/%Y')})"
                    )
            except ValueError:
                pass
        
        return alerts


# Funciones de conveniencia para uso rápido
def clean_contract_text(text: str, language: str = 'es') -> str:
    """
    Limpia texto contractual eliminando formatos no deseados
    
    Args:
        text: Texto crudo a limpiar
        language: Idioma del texto ('es' o 'en')
        
    Returns:
        Texto limpio y normalizado
    """
    processor = TextProcessor(language)
    return processor.clean_text(text)

def analyze_contract_sections(text: str, language: str = 'es') -> List[ContractSection]:
    """
    Identifica y extrae secciones comunes en contratos
    
    Args:
        text: Texto del contrato
        language: Idioma del contrato
        
    Returns:
        Lista de secciones identificadas
    """
    processor = TextProcessor(language)
    return processor.detect_sections(text)