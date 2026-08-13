"use client";

import React from "react";

interface FirefliesLogoProps {
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  className?: string;
  darkText?: boolean;
}

export function FirefliesLogoMark({ className = "w-9 h-9" }: { className?: string }) {
  return (
    <div className={`bg-gradient-to-b from-[#282A36] via-[#1C1E28] to-[#12131A] border border-[#3A3D4E]/80 shadow-xl flex items-center justify-center shrink-0 ${className}`}>
      <svg className="w-[62%] h-[62%]" viewBox="0 0 24 24" fill="none">
        {/* Top-left purple tile */}
        <rect x="5.5" y="4.5" width="5" height="5" rx="1" fill="#A855F7" />
        {/* Top-right pink quarter-circle tile */}
        <path d="M11.5 4.5H13A4.5 4.5 0 0 1 17.5 9V9.5H11.5V4.5Z" fill="#EC4899" />
        {/* Middle-left magenta tile */}
        <rect x="5.5" y="10.5" width="5" height="5" rx="0.5" fill="#EC4899" />
        {/* Middle-right hot pink tile */}
        <rect x="11.5" y="10.5" width="5" height="5" rx="1" fill="#F43F5E" />
        {/* Bottom-left rounded stem tile */}
        <path d="M5.5 16.5H10.5V17A4.5 4.5 0 0 1 6 21.5H5.5V16.5Z" fill="#E11D48" />
      </svg>
    </div>
  );
}

export default function FirefliesLogo({ 
  size = "md", 
  showText = true, 
  className = "",
  darkText = true
}: FirefliesLogoProps) {
  const markDimensions = size === "sm" ? "w-6 h-6 rounded-lg" : size === "lg" ? "w-11 h-11 rounded-2xl" : "w-8 h-8 rounded-xl";
  const textStyle = size === "sm" ? "text-xs" : size === "lg" ? "text-xl" : "text-[15px]";

  return (
    <div className={`flex items-center gap-2 select-none ${className}`}>
      <FirefliesLogoMark className={markDimensions} />
      {showText && (
        <span className={`font-black tracking-tight ${textStyle} ${darkText ? "text-gray-900" : "text-white"}`}>
          fireflies<span className="text-[#9333EA] font-bold">.ai</span>
        </span>
      )}
    </div>
  );
}
