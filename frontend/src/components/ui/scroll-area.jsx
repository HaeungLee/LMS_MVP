import React from "react";

export const ScrollArea = React.forwardRef(({ 
  className = "", 
  children,
  style,
  ...props 
}, ref) => {
  return (
    <div
      ref={ref}
      className={`relative overflow-auto ${className}`}
      style={{ 
        maxHeight: "400px", 
        ...style 
      }}
      {...props}
    >
      <div className="w-full">
        {children}
      </div>
    </div>
  );
});

export const ScrollBar = ({ 
  className = "",
  orientation = "vertical",
  ...props 
}) => {
  return (
    <div 
      className={`flex touch-none select-none transition-colors ${
        orientation === "vertical" 
          ? "h-full w-2.5 border-l border-l-transparent p-[1px]" 
          : "h-2.5 w-full border-t border-t-transparent p-[1px]"
      } ${className}`}
      {...props}
    />
  );
};

ScrollArea.displayName = "ScrollArea";
ScrollBar.displayName = "ScrollBar";
