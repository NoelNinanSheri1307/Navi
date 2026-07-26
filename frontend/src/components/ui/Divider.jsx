import React from "react";

export const Divider = ({ className = "" }) => {
  return <hr className={`border-t border-zinc-800/80 my-8 sm:my-12 ${className}`} />;
};
