import React from "react";

export const Container = ({ children, className = "", size = "default", ...props }) => {
  const sizes = {
    narrow: "max-w-4xl",
    default: "max-w-6xl",
    wide: "max-w-7xl",
  };

  return (
    <div
      className={`w-full mx-auto px-4 sm:px-6 lg:px-8 ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
