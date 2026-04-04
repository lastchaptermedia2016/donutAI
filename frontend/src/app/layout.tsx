import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Donut - Your Executive Function Co-Pilot",
  description:
    "A multi-modal agentic voice assistant that manages tasks, diary, calendar, and memories across business and personal contexts.",
  manifest: "/manifest.json",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#FFBF00",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <body className={`${inter.className} antialiased billionaire-bg text-billionaire-platinum`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}