"use client";

import { signOut, useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";

export default function Home() {
  const { data: session, status } = useSession();

  return (
    <main className="min-h-screen flex flex-col items-center justify-center gap-6 bg-scientific-dark text-white px-4 text-center">
      <h1 className="text-4xl font-bold">Hello, BioLab.Ai</h1>
      {status === "loading" ? (
        <p>Carregando informações...</p>
      ) : session?.user ? (
        <>
          <div className="text-lg">
            <p>
              <strong>Nome:</strong> {session.user.name}
            </p>
            <p>
              <strong>E-mail:</strong> {session.user.email}
            </p>
          </div>
          <Button
            onClick={() => signOut()}
            className="bg-scientific-highlight text-white hover:bg-scientific-success"
          >
            Logout
          </Button>
        </>
      ) : (
        <p>Você não está autenticado.</p>
      )}
    </main>
  );
}
