import React from "react";

export const Label = React.forwardRef(({ 
  className = "", 
  children,
  htmlFor,
  ...props 
}, ref) => {
  return (
    <label
      ref={ref}
      className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${className}`}
      htmlFor={htmlFor}
      {...props}
    >
      {children}
    </label>
  );
});

Label.displayName = "Label";
