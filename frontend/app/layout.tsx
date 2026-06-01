import type { Metadata } from "next";
import { Fraunces, Hanken_Grotesk, Space_Mono } from "next/font/google";
import "./globals.css";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";

/** Editorial display serif (optical sizing) — headlines and the wordmark. */
const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  axes: ["opsz"],
  style: ["normal", "italic"],
});

/** Warm humanist grotesk — body and UI. */
const hanken = Hanken_Grotesk({
  variable: "--font-hanken",
  subsets: ["latin"],
});

/** The "machine voice" — AI labels, scores, and the typewriter prompt. */
const spaceMono = Space_Mono({
  variable: "--font-space-mono",
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "Salon Atelier — Warsaw After-Hours",
  description:
    "An AI concierge for Warsaw's hair & beauty salons. Describe what you want in plain language; the atelier finds it.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${hanken.variable} ${spaceMono.variable} h-full`}
    >
      <body className="flex min-h-full flex-col">
        <SiteHeader />
        {children}
        <SiteFooter />
      </body>
    </html>
  );
}
