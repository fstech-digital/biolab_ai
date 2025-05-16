"use client";

import { signOut, useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";

export default function Home() {
  const { data: session, status } = useSession();

  return (
    <div className="min-h-[100vh] rounded-xl bg-muted/50 p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard do Usuário</h1>

      {status === "loading" ? (
        <p>Carregando informações...</p>
      ) : session?.user ? (
        <>
          <div className="text-lg space-y-1">
            <p>
              <strong>Nome:</strong> {session.user.name}
            </p>
            <p>
              <strong>E-mail:</strong> {session.user.email}
            </p>
            <p>
              <strong>Tipo:</strong> {session.user.role}
            </p>
          </div>
          <Button
            onClick={() => signOut()}
            className="mt-4 bg-scientific-highlight text-white hover:bg-scientific-success"
          >
            Logout
          </Button>
        </>
      ) : (
        <p>Você não está autenticado.</p>
      )}
    </div>
  );
}
