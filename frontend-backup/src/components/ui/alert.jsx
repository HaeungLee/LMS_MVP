import React from "react";

export const Alert = ({ 
  className = "", 
  variant = "default", 
  children, 
  ...props 
}) => {
  const variants = {
    default: "bg-background text-foreground",
    destructive: "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
    warning: "border-yellow-500/50 text-yellow-600 [&>svg]:text-yellow-600",
    success: "border-green-500/50 text-green-600 [&>svg]:text-green-600",
  };

  return (
    <div
      className={`relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const AlertDescription = ({ className = "", children, ...props }) => (
  <div
    className={`text-sm [&_p]:leading-relaxed ${className}`}
    {...props}
  >
    {children}
  </div>
);

export const AlertTitle = ({ className = "", children, ...props }) => (
  <h5
    className={`mb-1 font-medium leading-none tracking-tight ${className}`}
    {...props}
  >
    {children}
  </h5>
);
