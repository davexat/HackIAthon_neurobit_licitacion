def get_sample_text():
    return """
    El contratista deberá cumplir con todas las normas de seguridad.
    El plazo será de 90 días a partir de la firma del contrato.
    El presupuesto estimado es de $500,000.
    El RUC del contratista es 1790012345001.
    """

def get_sample_contract() -> str:
    return """
    CONTRATO DE OBRA PUBLICA
    Entre la PREFECTURA DEL GUAYAS y EDIFIKA S.A.
    Proyecto: Ampliacion de la Via Samborondon - Asfaltado completo de 10 carriles
    Monto: USD 20,000,000.00
    Plazo: 12 meses
    CLAUSULAS CONTRACTUALES
    PRIMERA - OBJETO DEL CONTRATO
    La PREFECTURA DEL GUAYAS encarga a EDIFIKA S.A. RUC: 0992881364001, la ejecucion de la obra denominada "Ampliacion de la Via Samborondon - Asfaltado completo de 10 carriles", conforme a los estudios tecnicos, planos, especificaciones y cronograma aprobado. La obra incluye:
    - Replanteo topografico
    - Movimiento de tierras
    - Instalacion de drenaje pluvial
    - Construccion de subbase y base
    - Aplicacion de carpeta asfaltica AC-20 modificada
    - Senalizacion horizontal y vertical
    - Supervision tecnica y entrega formal
    SEGUNDA - MONTO DEL CONTRATO
    El valor total del contrato asciende a USD 20,000,000.00, incluido IVA. Este monto cubre costos directos, indirectos, supervision, garantias y contingencias.
    
    TERCERA - PLAZO DE EJECUCION
    La obra se ejecutara en un plazo de doce (12) meses, contados desde la firma del acta de inicio.
    
    CUARTA - GARANTIAS
    EDIFIKA S.A. debera presentar:
    - Garantia de fiel cumplimiento: 5% del contrato
    - Garantia de buen uso del anticipo: 100% del anticipo
    - Garantia por vicios ocultos: 5% del contrato, vigente por 12 meses
    
    QUINTA - ANTICIPO
    La contratante entregara un anticipo del 30% del contrato (USD 6,000,000.00), amortizable desde el mes 2 al mes 9.
    
    SEXTA - MULTAS Y PENALIZACIONES
    - Multa por retraso: 0.1% diario del valor total
    - Penalizacion tecnica: hasta 10% de la partida afectada
    - Causales de terminacion: abandono, incumplimiento grave, falsedad documental
    
    SEPTIMA - RECEPCION DE LA OBRA
    - Recepcion provisional: al concluir la obra
    - Recepcion definitiva: 12 meses despues, sin vicios ocultos
    
    OCTAVA - RESOLUCION DE CONTROVERSIAS
    - Conciliacion directa
    - Mediacion ante Camara de Comercio de Guayaquil
    - Jurisdiccion ordinaria en Guayaquil
    
    NOVENA - LEGISLACION APLICABLE
    LOSNCP, su reglamento, Codigo Civil, Codigo Organico de Finanzas Publicas, normas MTOP, INEN y ASTM.
    
    ANEXOS
    ANEXO I - Cronograma de Ejecucion
    Mes Fase Actividad Principal
    1 Estudios Topografia, permisos
    2-3 Movimiento de tierras Excavacion, relleno
    4-5 Drenaje Alcantarillas, cunetas
    6-7 Subbase y base Material granular
    8-9 Asfaltado Carpeta asfaltica
    10 Senalizacion Pintura, postes
    11 Supervision final Control de calidad
    12 Recepcion Inspeccion tecnica
    
    ANEXO II - Presupuesto Detallado
    Partida Monto (USD)
    Estudios preliminares 500,000.00
    Movimiento de tierras 2,000,000.00
    Obras de drenaje 2,500,000.00
    Subbase y base 3,000,000.00
    Asfaltado 5,000,000.00
    
    Partida Monto (USD)
    Senalizacion 1,000,000.00
    Supervision 1,000,000.00
    Recepcion y cierre 1,000,000.00
    Imprevistos 3,000,000.00
    Total 20,000,000.00
    
    ANEXO III - Garantias
    Tipo Monto (USD) Vigencia Emisor
    Fiel cumplimiento 1,000,000.00 Hasta recepcion provis. Banco del Pacifico
    Anticipo 6,000,000.00 Hasta amortizacion Seguros Equinoccial
    Vicios ocultos 1,000,000.00 12 meses Banco Pichincha
    
    ANEXO IV - Especificaciones Tecnicas
    - Mezcla asfaltica: AC-20 modificada
    - Espesor: 10 cm (principales), 7 cm (laterales)
    - Drenaje: PVC reforzado, pozos cada 50 m
    - Senalizacion: Pintura termoplastica reflectiva
    - Normas: INEN, ASTM, MTOP
    
    ANEXO V - Acta de Inicio (Modelo)
    Incluye fecha de inicio, firmas, observaciones y registro fotografico.
    
    FORMULARIOS
    Formulario de Oferta Tecnica
    - Experiencia: 2 obras viales > USD 8M
    - Personal tecnico: ingeniero residente, topografo, especialista vial
    - Maquinaria: pavimentadora, rodillo, motoniveladora
    - Plan de trabajo: cronograma detallado
    
    Formulario de Oferta Economica
    - Monto ofertado: USD 20,000,000.00
    - Anticipo: 30%
    - Forma de pago: avances mensuales
    - Validez: 90 dias
    - Garantia de mantenimiento: 2%
    
    ACTA DE ADJUDICACION
    ACTA N.o 001-2025-PG
    Fecha: [dia/mes/2025]
    Adjudicado a: EDIFIKA S.A.
    Monto: USD 20,000,000.00
    Plazo: 12 meses
    Firmas: Prefectura del Guayas y EDIFIKA S.A.
    
    PRESUPUESTO MENSUAL
    Mes Fase Monto (USD)
    1 Estudios 500,000.00
    2-3 Movimiento de tierras 2,000,000.00
    4-5 Drenaje 2,500,000.00
    6-7 Subbase y base 3,000,000.00
    8-9 Asfaltado 5,000,000.00
    10 Senalizacion 1,000,000.00
    11 Supervision 1,000,000.00
    12 Recepcion 1,000,000.00
    
    FLUJO DE CAJA PROYECTADO
    Mes Avance (USD) Amortizacion Pago Neto Costo Saldo Mensual Saldo Acumulado
    1 500,000.00 0.00 6,000,000.00 500,000.00 +5,500,000.00 +5,500,000.00
    2-9 1M-2.5M 750,000.00 250K-1.75M Igual -750,000.00 +250K -> -500K
    10-12 1,000,000.00 0.00 1,000,000.00 1,000,000.00 0.00 -500,000.00
    """