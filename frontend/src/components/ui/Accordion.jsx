import React, { useState } from "react";
import { ChevronDown } from "lucide-react";

export const AccordionItem = ({ title, children, isOpen, onToggle }) => {
  return (
    <div className="border-b border-zinc-900 last:border-b-0 py-4">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between text-left text-sm text-zinc-200 font-normal hover:text-white transition-colors gap-4"
      >
        <span>{title}</span>
        <ChevronDown
          size={16}
          className={`text-zinc-500 transition-transform duration-200 shrink-0 ${
            isOpen ? "rotate-180 text-zinc-300" : ""
          }`}
        />
      </button>
      {isOpen && (
        <div className="mt-3 text-xs sm:text-sm text-zinc-400 leading-relaxed max-w-3xl">
          {children}
        </div>
      )}
    </div>
  );
};

export const Accordion = ({ items = [], className = "" }) => {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <div className={`flex flex-col border-t border-b border-zinc-900 ${className}`}>
      {items.map((item, idx) => (
        <AccordionItem
          key={idx}
          title={item.title}
          isOpen={openIndex === idx}
          onToggle={() => setOpenIndex(openIndex === idx ? -1 : idx)}
        >
          {item.content}
        </AccordionItem>
      ))}
    </div>
  );
};
