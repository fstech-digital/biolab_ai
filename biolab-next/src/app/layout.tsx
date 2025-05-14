import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Providers } from "./providers";
import { dbConnect } from "@/lib/mongoose";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";

export const metadata: Metadata = {
  title: "BioLab App",
  description: "Análise inteligente de exames laboratoriais",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  await dbConnect();
  const session = await getServerSession(authOptions);

  return (
    <html lang="pt-BR">
      <body>
        <Providers session={session}>{children}</Providers>
      </body>
    </html>
  );
}
