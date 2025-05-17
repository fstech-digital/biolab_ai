"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Toaster } from "@/components/ui/toaster";
import { toast } from "@/hooks/use-toast";
import GoogleIcon from "@/components/icons/GoogleIcon";
import Image from "next/image";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      setError("Preencha todos os campos");
      toast({
        title: "Erro",
        description: "Preencha todos os campos.",
        variant: "destructive",
      });
      return;
    }

    const res = await signIn("credentials", {
      email,
      password,
      redirect: false,
    });

    if (res?.error) {
      setError("Credenciais inválidas");
      toast({
        title: "Erro",
        description: "Credenciais inválidas",
        variant: "destructive",
      });
    } else {
      toast({ title: "Login realizado", description: "Bem-vindo de volta!" });
      router.push("/");
    }
  };

  return (
    <main className="min-h-screen bg-scientific-dark flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md space-y-6 border border-scientific-subtle"
      >
        <div className="text-center space-y-2">
          <Image
            src="/iconPNG.png"
            alt="Logo BioLab.Ai"
            width={96}
            height={96}
            className="mx-auto bg-scientific-dark rounded-full p-2"
          />

          <h1 className="text-3xl font-bold text-scientific-dark">Entrar</h1>
          <p className="text-sm text-gray-600">
            Acesse sua conta para continuar
          </p>
        </div>

        <div className="space-y-4">
          <Input
            type="email"
            placeholder="E-mail"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="bg-white"
          />
          <Input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="bg-white"
          />
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          <Button
            type="submit"
            className="w-full bg-scientific-success hover:bg-scientific-highlight"
          >
            Entrar
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => signIn("google", { callbackUrl: "/" })}
            className="w-full flex items-center justify-center gap-2 border-scientific-highlight text-scientific-highlight hover:bg-scientific-highlight/10 bg-white"
          >
            <GoogleIcon />
            Entrar com Google
          </Button>
        </div>

        <p className="text-sm text-center text-gray-600">
          Não tem uma conta?{" "}
          <Link
            href="/register"
            className="text-scientific-highlight hover:underline"
          >
            Criar conta
          </Link>
        </p>

        <Toaster />
      </form>
    </main>
  );
}
