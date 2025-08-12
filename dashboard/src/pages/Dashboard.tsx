import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ProgressBar } from "@/components/ui/progress-bar";
import { RiskIndicator } from "@/components/ui/risk-indicator";
import { StatusBadge } from "@/components/ui/status-badge";
import { CoherenceIndicator } from "@/components/ui/coherence-indicator";
import { Plus, FileText } from "lucide-react";
import { mockBidders } from "@/data/mockData";

const Dashboard = () => {
  const navigate = useNavigate();
  const [bidders] = useState(mockBidders);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-EC', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const handleVerDetalles = (bidderId: string) => {
    navigate(`/oferente/${bidderId}`);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="w-8 h-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold text-foreground">
                  Dashboard Comparativo
                </h1>
                <p className="text-muted-foreground">
                  Análisis de propuestas de licitación
                </p>
              </div>
            </div>
            <Button 
              className="flex items-center space-x-2"
              onClick={() => navigate("/cargar-licitacion")}
            >
              <Plus className="w-4 h-4" />
              <span>Cargar Nueva Licitación</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Oferentes Registrados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                      Nombre del Oferente
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                      Presupuesto Ofertado
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                      Plazo Ofertado
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                      Score de Cumplimiento
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                      Nivel de Riesgo
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                      Estado Legal
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                      Capital Suscrito
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                      Coherencia de Actividad
                    </th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">
                      Acción
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {bidders.map((bidder) => (
                    <tr 
                      key={bidder.id}
                      className="border-b border-border hover:bg-muted/50 transition-colors"
                    >
                      <td className="py-4 px-4">
                        <div className="font-medium text-foreground">
                          {bidder.nombre}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className="font-semibold text-primary">
                          {formatCurrency(bidder.presupuestoOfertado)}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-foreground">
                        {bidder.plazoOfertado}
                      </td>
                      <td className="py-4 px-4">
                        <ProgressBar value={bidder.scoreCumplimiento} />
                      </td>
                      <td className="py-4 px-4">
                        <RiskIndicator level={bidder.nivelRiesgo} />
                      </td>
                      <td className="py-4 px-4">
                        <StatusBadge status={bidder.estadoLegal} />
                      </td>
                      <td className="py-4 px-4 text-foreground">
                        {formatCurrency(bidder.capitalSuscrito)}
                      </td>
                      <td className="py-4 px-4">
                        <CoherenceIndicator isCoherent={bidder.coherenciaActividad} />
                      </td>
                      <td className="py-4 px-4">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleVerDetalles(bidder.id)}
                        >
                          Ver Detalles
                        </Button>
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
  );
};

export default Dashboard;