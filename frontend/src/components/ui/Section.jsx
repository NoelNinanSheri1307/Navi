import React from "react";

export const Section = ({ children, className = "", id, ...props }) => {
  return (
    <section
      id={id}
      className={`py-12 sm:py-16 md:py-20 border-b border-zinc-900/80 last:border-b-0 ${className}`}
      {...props}
    >
      {children}
    </section>
  );
};
