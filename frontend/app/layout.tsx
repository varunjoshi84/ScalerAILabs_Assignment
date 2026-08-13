import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Fireflies.ai — AI Meeting Assistant & Transcripts",
  description: "Transcribe, summarize, search, and analyze your team interactions automatically with AskFred AI.",
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