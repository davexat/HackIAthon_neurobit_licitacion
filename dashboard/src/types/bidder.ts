export interface Bidder {
  id: string;
  nombre: string;
  presupuestoOfertado: number;
  plazoOfertado: string;
  scoreCumplimiento: number;
  nivelRiesgo: "bajo" | "medio" | "alto";
  estadoLegal: string;
  capitalSuscrito: number;
  coherenciaActividad: boolean;
  ruc: string;
  estadoSRI: string;
  estadoSupercias: string;
  objetoContrato: string;
  actividadPrincipal: string;
  montoOfertado: number;
  plazoEjecucion: string;
  validezOferta: string;
  requisitos: Requirement[];
}

export interface Requirement {
  requisito: string;
  estado: "cumplido" | "faltante" | "inconsistente";
  observacion: string;
}