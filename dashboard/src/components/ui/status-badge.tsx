import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const isActive = status.toLowerCase() === "activo";
  
  return (
    <span className={cn(
      "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
      isActive 
        ? "bg-success text-success-foreground" 
        : "bg-danger text-danger-foreground",
      className
    )}>
      {status.toUpperCase()}
    </span>
  );
}