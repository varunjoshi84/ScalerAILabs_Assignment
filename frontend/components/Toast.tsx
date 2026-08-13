"use client";

import React, { useEffect } from "react";
import { CheckCircle, AlertCircle, X } from "lucide-react";

interface ToastProps {
  message: string;
  type: "success" | "error";
  onClose: () => void;
}

export default function Toast({ message, type, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 4000); // Auto-dismiss after 4 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed top-5 right-5 z-[9999] flex items-center gap-3 px-4 py-3 rounded-xl shadow-2xl text-white font-sans animate-in slide-in-from-right-5 duration-200 border bg-gray-950 border-gray-800">
      
      {/* Icon based on success/error */}
      {type === "success" ? (
        <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0" />
      ) : (
        <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
      )}

      {/* Message Text */}
      <span className="text-xs font-bold tracking-wide">
        {message}
      </span>

      {/* Close button */}
      <button 
        onClick={onClose}
        className="p-0.5 rounded hover:bg-gray-800 text-gray-400 hover:text-white transition-colors cursor-pointer"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
