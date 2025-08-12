import { cn } from "@/lib/utils";

interface RiskIndicatorProps {
  level: "bajo" | "medio" | "alto";
  className?: string;
}

export function RiskIndicator({ level, className }: RiskIndicatorProps) {
  const getConfig = (level: string) => {
    switch (level.toLowerCase()) {
      case "bajo":
        return { 
          color: "bg-success", 
          text: "Bajo",
          textColor: "text-gray-800"
        };
      case "medio":
        return { 
          color: "bg-warning", 
          text: "Medio",
          textColor: "text-gray-800"
        };
      case "alto":
        return { 
          color: "bg-danger", 
          text: "Alto",
          textColor: "text-gray-800"
        };
      default:
        return { 
          color: "bg-neutral", 
          text: "N/A",
          textColor: "text-gray-800"
        };
    }
  };

  const config = getConfig(level);

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <div className={cn("w-3 h-3 rounded-full", config.color)} />
      <span className={cn("text-sm font-medium", config.textColor)}>
        {config.text}
      </span>
    </div>
  );
}