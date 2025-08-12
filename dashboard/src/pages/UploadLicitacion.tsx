import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { FileText, Upload, ArrowLeft } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const UploadLicitacion = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [pliegoFile, setPliegoFile] = useState<File | null>(null);
  const [contratoFile, setContratoFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handlePliegoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === "application/pdf") {
      setPliegoFile(file);
    } else {
      toast({
        title: "Error",
        description: "Por favor selecciona un archivo PDF válido",
        variant: "destructive",
      });
    }
  };

  const handleContratoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === "application/pdf") {
      setContratoFile(file);
    } else {
      toast({
        title: "Error",
        description: "Por favor selecciona un archivo PDF válido",
        variant: "destructive",
      });
    }
  };

  const handleSubmit = async () => {
    if (!pliegoFile || !contratoFile) {
      toast({
        title: "Error",
        description: "Por favor carga ambos archivos PDF",
        variant: "destructive",
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const formData = new FormData();
      formData.append("pliego", pliegoFile);
      formData.append("contrato", contratoFile);

      // Simulated API call - replace with actual endpoint
      await fetch("/api/process-new-bid", {
        method: "POST",
        body: formData,
      });

      toast({
        title: "Éxito",
        description: "Documentos cargados correctamente. Procesando licitación...",
      });

      // Redirect back to dashboard
      navigate("/");
    } catch (error) {
      toast({
        title: "Error",
        description: "Hubo un problema al cargar los documentos",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
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
                  Cargar Nueva Licitación
                </h1>
                <p className="text-muted-foreground">
                  Sube los documentos base para iniciar el análisis
                </p>
              </div>
            </div>
            <Button 
              variant="outline" 
              onClick={() => navigate("/")}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Volver al Dashboard</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Documentos de la Licitación</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Pliego Upload */}
              <div className="space-y-2">
                <Label htmlFor="pliego" className="text-base font-medium">
                  Paso 1: Cargar Pliego de Condiciones (PDF)
                </Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="pliego"
                    type="file"
                    accept=".pdf"
                    onChange={handlePliegoChange}
                    className="flex-1"
                  />
                  {pliegoFile && (
                    <div className="flex items-center text-green-600">
                      <Upload className="w-4 h-4 mr-1" />
                      <span className="text-sm">{pliegoFile.name}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Contrato Upload */}
              <div className="space-y-2">
                <Label htmlFor="contrato" className="text-base font-medium">
                  Paso 2: Cargar Contrato Modelo (PDF)
                </Label>
                <div className="flex items-center space-x-2">
                  <Input
                    id="contrato"
                    type="file"
                    accept=".pdf"
                    onChange={handleContratoChange}
                    className="flex-1"
                  />
                  {contratoFile && (
                    <div className="flex items-center text-green-600">
                      <Upload className="w-4 h-4 mr-1" />
                      <span className="text-sm">{contratoFile.name}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <div className="pt-4">
                <Button
                  onClick={handleSubmit}
                  disabled={!pliegoFile || !contratoFile || isSubmitting}
                  className="w-full h-12 text-base"
                  size="lg"
                >
                  {isSubmitting ? (
                    "Procesando..."
                  ) : (
                    "Cargar y Analizar Licitación"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UploadLicitacion;