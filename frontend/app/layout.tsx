import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Fireflies.ai",
  description: "AI Meeting Assistant & Transcripts",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}