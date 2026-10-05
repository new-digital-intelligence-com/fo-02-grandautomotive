import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// One font for Greek and English text.
const inter = Inter({
  variable: "--font-inter",
  subsets: ["greek", "latin"],
});

export const metadata: Metadata = {
  title: "Grand Automotive – Voice Assistant Demo",
  description: "Talk with Katerina, the Greek voice assistant for Renault and Dacia in Greece (NDI demo for Grand Automotive).",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="el" className={`${inter.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col font-sans">{children}</body>
    </html>
  );
}
