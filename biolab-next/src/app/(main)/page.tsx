"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import { FileText, Loader2, Upload } from "lucide-react";
import { Toaster } from "@/components/ui/toaster";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (selected.type !== "application/pdf") {
      toast({
        title: "Arquivo inválido",
        description: "Somente arquivos PDF são permitidos.",
        variant: "destructive",
      });
      e.target.value = "";
      setFile(null);
      return;
    }

    setFile(selected);
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("pdf", file);

    try {
      const res = await fetch("/api/upload-pdf", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.message || "Erro inesperado.");
      }

      toast({
        title: "Upload realizado",
        description: "Exame enviado com sucesso!",
        variant: "success",
      });

      setFile(null);
      const input = document.getElementById("pdf-upload") as HTMLInputElement;
      if (input) input.value = "";
    } catch (err: any) {
      toast({
        title: "Erro ao enviar",
        description: err.message || "Erro inesperado.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-scientific-dark flex items-center justify-center px-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md space-y-6 border border-scientific-subtle">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-scientific-highlight">
            Enviar Exame
          </h1>
          <p className="text-sm text-gray-600">
            Apenas arquivos <strong>PDF</strong> são aceitos.
          </p>
        </div>

        <div className="space-y-4">
          <label
            htmlFor="pdf-upload"
            className="flex items-center justify-between px-4 py-3 rounded-lg border border-dashed border-scientific-highlight cursor-pointer hover:bg-scientific-highlight/10 transition"
          >
            <div className="flex items-center gap-2 text-scientific-dark">
              <FileText className="w-5 h-5 text-scientific-subtle" />
              <span className="text-sm">
                {file ? file.name : "Selecionar arquivo PDF"}
              </span>
            </div>
            <Upload className="w-4 h-4 text-scientific-subtle" />
          </label>

          <Input
            id="pdf-upload"
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            className="hidden"
          />

          <Button
            onClick={handleUpload}
            disabled={loading || !file}
            className={`w-full ${
              loading || !file
                ? "bg-scientific-success/50 cursor-not-allowed"
                : "bg-scientific-success hover:bg-scientific-highlight"
            } text-white`}
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Enviando...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Enviar PDF
              </>
            )}
          </Button>
        </div>

        <Toaster />
      </div>
    </main>
  );
}
