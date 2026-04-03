import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Console | Donut",
  description: "Management console for Donut AI",
};

export default function ConsoleLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}