import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/ui/status-badge";
import { ArrowLeft, Building, AlertTriangle, CheckCircle, X } from "lucide-react";
import { mockBidders } from "@/data/mockData";
import { cn } from "@/lib/utils";

const BidderDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const bidder = mockBidders.find(b => b.id === id);

  if (!bidder) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-foreground mb-4">
            Oferente no encontrado
          </h2>
          <Button onClick={() => navigate("/")}>
            Volver al Dashboard
          </Button>
        </div>
      </div>
    );
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-EC', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const getRequirementIcon = (estado: string) => {
    switch (estado) {
      case "cumplido":
        return <CheckCircle className="w-5 h-5 text-success" />;
      case "faltante":
        return <X className="w-5 h-5 text-danger" />;
      case "inconsistente":
        return <AlertTriangle className="w-5 h-5 text-warning" />;
      default:
        return null;
    }
  };

  const getRequirementBadge = (estado: string) => {
    const configs = {
      cumplido: { text: "CUMPLIDO", className: "bg-success text-success-foreground" },
      faltante: { text: "FALTANTE", className: "bg-danger text-danger-foreground" },
      inconsistente: { text: "INCONSISTENTE", className: "bg-warning text-warning-foreground" }
    };
    
    const config = configs[estado as keyof typeof configs];
    return (
      <Badge className={config.className}>
        {config.text}
      </Badge>
    );
  };

  const isCoherenceAlertHigh = !bidder.coherenciaActividad;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate("/")}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Volver al Dashboard</span>
            </Button>
            <div className="flex items-center space-x-3">
              <Building className="w-8 h-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  {bidder.nombre}
                </h1>
                <p className="text-muted-foreground">
                  Análisis detallado del oferente
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8 space-y-8">
        {/* Sección 1: Perfil del Contratista */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Building className="w-5 h-5" />
              <span>Perfil del Contratista</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Nombre / Razón Social
              </label>
              <p className="text-foreground font-medium">{bidder.nombre}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                RUC
              </label>
              <p className="text-foreground font-medium">{bidder.ruc}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Estado en SRI
              </label>
              <div className="mt-1">
                <StatusBadge status={bidder.estadoSRI} />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Estado Legal en Supercias
              </label>
              <div className="mt-1">
                <StatusBadge status={bidder.estadoSupercias} />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Capital Suscrito
              </label>
              <p className="text-foreground font-medium">
                {formatCurrency(bidder.capitalSuscrito)}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Sección 2: Análisis de Coherencia de Actividad */}
        <Card className={cn(
          "border-2",
          isCoherenceAlertHigh 
            ? "border-danger bg-danger-light" 
            : "border-success bg-success-light"
        )}>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              {isCoherenceAlertHigh ? (
                <AlertTriangle className="w-5 h-5 text-danger" />
              ) : (
                <CheckCircle className="w-5 h-5 text-success" />
              )}
              <span>Análisis de Coherencia de Actividad</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Objeto del Contrato
              </label>
              <p className="text-foreground">{bidder.objetoContrato}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Actividad Principal Registrada
              </label>
              <p className="text-foreground">{bidder.actividadPrincipal}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-muted-foreground">
                Diagnóstico de la IA
              </label>
              <div className={cn(
                  "p-4 rounded-lg",
                  isCoherenceAlertHigh ? "bg-danger-light" : "bg-success-light"
                )}>
                  {isCoherenceAlertHigh ? (
                    <p className="text-gray-800"> {/* <-- CAMBIO AQUÍ */}
                      ⚠️ <strong>ALERTA DE RIESGO ALTO:</strong> La actividad económica principal del oferente 
                      ({bidder.actividadPrincipal}) no corresponde con el objeto del contrato de construcción. 
                      Esta empresa se dedica principalmente a actividades comerciales, no a construcción, 
                      lo que representa un riesgo significativo para la ejecución del proyecto.
                    </p>
                  ) : (
                    <p className="text-gray-800"> {/* <-- Y CAMBIO AQUÍ */}
                      ✅ <strong>COHERENCIA CONFIRMADA:</strong> La actividad económica principal del oferente 
                      está alineada con el objeto del contrato. La empresa tiene registro como constructora 
                      y cuenta con la experiencia necesaria en el sector de la construcción.
                    </p>
                  )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Sección 3: Análisis de la Propuesta */}
        <div className="space-y-6">
          <h2 className="text-xl font-semibold text-foreground">
            Análisis de la Propuesta
          </h2>

          {/* Resumen de la Oferta */}
          <Card>
            <CardHeader>
              <CardTitle>Resumen de la Oferta</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Monto Ofertado
                </label>
                <p className="text-2xl font-bold text-primary">
                  {formatCurrency(bidder.montoOfertado)}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Plazo de Ejecución
                </label>
                <p className="text-lg font-medium text-foreground">
                  {bidder.plazoEjecucion}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-muted-foreground">
                  Validez de la Oferta
                </label>
                <p className="text-lg font-medium text-foreground">
                  {bidder.validezOferta}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Checklist de Cumplimiento */}
          <Card>
            <CardHeader>
              <CardTitle>Checklist de Cumplimiento de Requisitos</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                        Requisito del Pliego
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                        Estado en la Propuesta
                      </th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                        Observación / Texto Extraído
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {bidder.requisitos.map((req, index) => (
                      <tr 
                        key={index}
                        className="border-b border-border hover:bg-muted/50 transition-colors"
                      >
                        <td className="py-4 px-4 font-medium text-foreground">
                          {req.requisito}
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center space-x-2">
                            {getRequirementIcon(req.estado)}
                            {getRequirementBadge(req.estado)}
                          </div>
                        </td>
                        <td className="py-4 px-4 text-muted-foreground">
                          {req.observacion}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default BidderDetail;