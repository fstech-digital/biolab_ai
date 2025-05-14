"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Toaster } from "@/components/ui/toaster";
import { toast } from "@/hooks/use-toast";
import Image from "next/image";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !password) {
      toast({
        title: "Erro",
        description: "Preencha todos os campos",
        variant: "destructive",
      });
      return;
    }

    const res = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await res.json();
    if (!res.ok) {
      toast({
        title: "Erro ao cadastrar",
        description: data.message || "Erro inesperado",
        variant: "destructive",
      });
    } else {
      toast({
        title: "Conta criada",
        description: "Redirecionando para login...",
      });
      setTimeout(() => router.push("/login"), 2000);
    }
  };

  return (
    <main className="min-h-screen bg-scientific-dark flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white text-scientific-dark p-8 rounded-xl shadow-lg w-full max-w-md space-y-6 border border-scientific-subtle"
      >
        <div className="text-center space-y-2">
          <Image
            src="/iconPNG.png"
            alt="Logo"
            width={96}
            height={96}
            className="mx-auto bg-scientific-dark rounded-full p-2"
          />
          <h1 className="text-3xl font-bold">Criar Conta</h1>
          <p className="text-sm text-gray-600">
            Preencha os dados para se cadastrar
          </p>
        </div>

        <div className="space-y-4">
          <Input
            placeholder="Nome"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="submit"
            className="w-full bg-scientific-success hover:bg-scientific-highlight"
          >
            Cadastrar
          </Button>
        </div>

        <p className="text-sm text-center text-gray-600">
          Já tem uma conta?{" "}
          <Link
            href="/login"
            className="text-scientific-highlight hover:underline"
          >
            Entrar
          </Link>
        </p>

        <Toaster />
      </form>
    </main>
  );
}
