import { Bidder } from "@/types/bidder";

export const mockBidders: Bidder[] = [
  {
    id: "1",
    nombre: "Constructora Andina S.A.",
    presupuestoOfertado: 1250000,
    plazoOfertado: "180 días",
    scoreCumplimiento: 95,
    nivelRiesgo: "bajo",
    estadoLegal: "ACTIVO",
    capitalSuscrito: 500000,
    coherenciaActividad: true,
    ruc: "1792345678001",
    estadoSRI: "ACTIVO",
    estadoSupercias: "ACTIVO",
    objetoContrato: "Construcción de edificio administrativo de 5 plantas",
    actividadPrincipal: "F4100.10 - CONSTRUCCIÓN DE EDIFICIOS COMPLETOS Y DE PARTES DE EDIFICIOS",
    montoOfertado: 1250000,
    plazoEjecucion: "180 días",
    validezOferta: "90 días",
    requisitos: [
      {
        requisito: "Certificado de Capacidad Residual",
        estado: "cumplido",
        observacion: "Certificado vigente con capacidad de $2,500,000"
      },
      {
        requisito: "Experiencia mínima 5 años",
        estado: "cumplido",
        observacion: "Presenta 8 proyectos similares en los últimos 10 años"
      },
      {
        requisito: "Garantía de Seriedad de Oferta",
        estado: "cumplido",
        observacion: "Póliza bancaria por $25,000"
      }
    ]
  },
  {
    id: "2",
    nombre: "Obras Civiles del Pacífico Ltda.",
    presupuestoOfertado: 1180000,
    plazoOfertado: "165 días",
    scoreCumplimiento: 78,
    nivelRiesgo: "medio",
    estadoLegal: "ACTIVO",
    capitalSuscrito: 300000,
    coherenciaActividad: true,
    ruc: "0992123456001",
    estadoSRI: "ACTIVO",
    estadoSupercias: "ACTIVO",
    objetoContrato: "Construcción de edificio administrativo de 5 plantas",
    actividadPrincipal: "F4100.10 - CONSTRUCCIÓN DE EDIFICIOS COMPLETOS Y DE PARTES DE EDIFICIOS",
    montoOfertado: 1180000,
    plazoEjecucion: "165 días",
    validezOferta: "90 días",
    requisitos: [
      {
        requisito: "Certificado de Capacidad Residual",
        estado: "cumplido",
        observacion: "Certificado vigente con capacidad de $1,800,000"
      },
      {
        requisito: "Experiencia mínima 5 años",
        estado: "inconsistente",
        observacion: "Presenta solo 3 proyectos, pero de mayor envergadura"
      },
      {
        requisito: "Garantía de Seriedad de Oferta",
        estado: "cumplido",
        observacion: "Póliza bancaria por $23,600"
      }
    ]
  },
  {
    id: "3",
    nombre: "Comercializadora Global S.A.",
    presupuestoOfertado: 1100000,
    plazoOfertado: "150 días",
    scoreCumplimiento: 45,
    nivelRiesgo: "alto",
    estadoLegal: "SUSPENDIDO",
    capitalSuscrito: 150000,
    coherenciaActividad: false,
    ruc: "1791234567001",
    estadoSRI: "PASIVO",
    estadoSupercias: "SUSPENDIDO",
    objetoContrato: "Construcción de edificio administrativo de 5 plantas",
    actividadPrincipal: "G4711.01 - VENTA AL POR MENOR EN COMERCIOS NO ESPECIALIZADOS",
    montoOfertado: 1100000,
    plazoEjecucion: "150 días",
    validezOferta: "60 días",
    requisitos: [
      {
        requisito: "Certificado de Capacidad Residual",
        estado: "faltante",
        observacion: "No presenta certificado"
      },
      {
        requisito: "Experiencia mínima 5 años",
        estado: "faltante",
        observacion: "No presenta experiencia en construcción"
      },
      {
        requisito: "Garantía de Seriedad de Oferta",
        estado: "inconsistente",
        observacion: "Presenta cheque certificado en lugar de póliza"
      }
    ]
  }
];