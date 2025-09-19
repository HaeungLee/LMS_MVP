import React from "react";

export const Card = ({ className = "", children, style = {}, ...props }) => {
  const fallbackStyle = {
    backgroundColor: `hsl(var(--card, 0 0% 100%))`,
    color: `hsl(var(--card-foreground, 222 20% 10%))`,
    borderColor: `hsl(var(--border, 210 16% 96%))`,
  };
  const combinedStyle = { ...fallbackStyle, ...style };

  return (
    <div
      className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}
      style={combinedStyle}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader = ({ className = "", children, ...props }) => (
  <div className={`flex flex-col space-y-1.5 p-6 ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle = ({ className = "", children, ...props }) => (
  <h3
    className={`text-2xl font-semibold leading-none tracking-tight ${className}`}
    {...props}
  >
    {children}
  </h3>
);

export const CardDescription = ({ className = "", children, ...props }) => (
  <p className={`text-sm text-muted-foreground ${className}`} {...props}>
    {children}
  </p>
);

export const CardContent = ({ className = "", children, ...props }) => (
  <div className={`p-6 pt-0 ${className}`} {...props}>
    {children}
  </div>
);

export const CardFooter = ({ className = "", children, ...props }) => (
  <div className={`flex items-center p-6 pt-0 ${className}`} {...props}>
    {children}
  </div>
);
