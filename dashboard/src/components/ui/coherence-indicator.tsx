import { Check, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface CoherenceIndicatorProps {
  isCoherent: boolean;
  className?: string;
}

export function CoherenceIndicator({ isCoherent, className }: CoherenceIndicatorProps) {
  return (
    <div className={cn("flex items-center space-x-2", className)}>
      {isCoherent ? (
        <>
          <Check className="w-4 h-4 text-success" />
          <span className="text-sm text-success">Coincide</span>
        </>
      ) : (
        <>
          <AlertTriangle className="w-4 h-4 text-warning" />
          <span className="text-sm text-warning">No Coincide</span>
        </>
      )}
    </div>
  );
}