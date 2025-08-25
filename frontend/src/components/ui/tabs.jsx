import React from "react";

export const Tabs = ({ 
  defaultValue, 
  value, 
  onValueChange, 
  className = "", 
  children, 
  ...props 
}) => {
  const [internalValue, setInternalValue] = React.useState(defaultValue);
  const currentValue = value !== undefined ? value : internalValue;
  
  const handleValueChange = (newValue) => {
    if (value === undefined) {
      setInternalValue(newValue);
    }
    if (onValueChange) {
      onValueChange(newValue);
    }
  };

  return (
    <div className={`${className}`} {...props}>
      {React.Children.map(children, child =>
        React.cloneElement(child, { 
          currentValue: currentValue, 
          onValueChange: handleValueChange 
        })
      )}
    </div>
  );
};

export const TabsList = ({ className = "", children, currentValue, onValueChange, ...props }) => (
  <div
    className={`inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground ${className}`}
    {...props}
  >
    {React.Children.map(children, child =>
      React.cloneElement(child, { currentValue, onValueChange })
    )}
  </div>
);

export const TabsTrigger = ({ 
  className = "", 
  children, 
  value: tabValue, 
  currentValue,
  onValueChange,
  ...props 
}) => {
  const isActive = currentValue === tabValue;
  
  return (
    <button
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 ${
        isActive 
          ? "bg-background text-foreground shadow-sm" 
          : "hover:bg-background/80"
      } ${className}`}
      onClick={() => onValueChange && onValueChange(tabValue)}
      {...props}
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ 
  className = "", 
  children, 
  value: tabValue,
  currentValue,
  ...props 
}) => {
  if (currentValue !== tabValue) return null;
  
  return (
    <div
      className={`mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${className}`}
    >
      {children}
    </div>
  );
};
