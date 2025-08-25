import React from "react";

export const Select = ({ children, value, onValueChange, ...props }) => {
  return (
    <div className="relative">
      {React.Children.map(children, child => 
        React.cloneElement(child, { value, onValueChange })
      )}
    </div>
  );
};

export const SelectTrigger = React.forwardRef(({ 
  className = "", 
  children, 
  ...props 
}, ref) => (
  <button
    ref={ref}
    className={`flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
    {...props}
  >
    {children}
  </button>
));

export const SelectValue = ({ placeholder, value }) => (
  <span>{value || placeholder}</span>
);

export const SelectContent = ({ children, ...props }) => (
  <div
    className="relative z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md"
    {...props}
  >
    {children}
  </div>
);

export const SelectItem = ({ children, value, onValueChange, ...props }) => (
  <div
    className="relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none hover:bg-accent hover:text-accent-foreground"
    onClick={() => onValueChange && onValueChange(value)}
    {...props}
  >
    {children}
  </div>
);

SelectTrigger.displayName = "SelectTrigger";
