import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number;
  className?: string;
}

export function ProgressBar({ value, className }: ProgressBarProps) {
  const getColorClass = (value: number) => {
    if (value > 85) return "bg-success";
    if (value >= 60) return "bg-warning";
    return "bg-danger";
  };

  return (
    <div className={cn("flex items-center space-x-2", className)}>
      <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
        <div 
          className={cn("h-full transition-all duration-300", getColorClass(value))}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
      <span className="text-sm font-medium text-foreground min-w-[3rem]">
        {value}%
      </span>
    </div>
  );
}