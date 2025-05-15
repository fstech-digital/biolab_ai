// app/admin/page.tsx
"use client";
import { useSession } from "next-auth/react";

export default function AdminDashboard() {
  const { data: session } = useSession();

  return (
    <div>
      <h1 className="text-2xl font-bold">Painel do Administrador</h1>
      <p>Bem-vindo, {session?.user?.name}!</p>
    </div>
  );
}
