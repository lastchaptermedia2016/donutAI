import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { GradientMeshBackground, ParticleBackground } from "@/components/ui";
import { PWAInstallPrompt } from "@/components/PWAInstallPrompt";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Donut - Your Executive Function Co-Pilot",
  description:
    "A multi-modal agentic voice assistant that manages tasks, diary, calendar, and memories across business and personal contexts.",
  manifest: "/manifest.json",
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/icons/icon-192x192.png', type: 'image/png', sizes: '192x192' },
      { url: '/icons/icon-512x512.png', type: 'image/png', sizes: '512x512' },
    ],
    apple: [
      { url: '/icons/icon-180x180.png', sizes: '180x180' },
    ],
  },
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
      <body className={`${inter.className} antialiased billionaire-bg text-billionaire-platinum relative overflow-x-hidden`}>
        {/* Luxury Background Layers */}
        <GradientMeshBackground />
        <ParticleBackground particleCount={25} />
        
        {/* Main Content */}
        <div className="relative z-10">
          <Providers>{children}</Providers>
        </div>
        
        {/* PWA Install Prompt */}
        <PWAInstallPrompt />
      </body>
    </html>
  );
}
