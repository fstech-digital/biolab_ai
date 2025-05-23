"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";

interface PatientDataDialogProps {
  open: boolean;
  defaultName?: string;
  defaultCpf?: string;
  onClose: () => void;
  onSubmit: (data: { nome: string; cpf: string }) => void;
}

// Função para aplicar a máscara de CPF
function formatCpf(value: string) {
  const numbers = value.replace(/\D/g, "");
  return numbers
    .replace(/^(\d{3})(\d)/, "$1.$2")
    .replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/\.(\d{3})\.(\d{3})(\d)/, ".$1.$2-$3")
    .slice(0, 14);
}

export default function PatientDataDialog({
  open,
  defaultName = "",
  defaultCpf = "",
  onClose,
  onSubmit,
}: PatientDataDialogProps) {
  const [nome, setNome] = useState(defaultName);
  const [cpf, setCpf] = useState(formatCpf(defaultCpf));

  useEffect(() => {
    setNome(defaultName);
    setCpf(formatCpf(defaultCpf));
  }, [defaultName, defaultCpf]);

  const isValidCpf = cpf.length === 14;
  const isValid = nome.trim().length > 0 && isValidCpf;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-white text-[#0F1C2E]">
        <DialogHeader>
          <DialogTitle className="text-[#0F1C2E]">
            Preencher dados do paciente
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Input
            placeholder="Nome completo"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            className="focus-visible:ring-0 focus-visible:ring-offset-0 focus:ring-0 focus:ring-offset-0"
          />

          <Input
            placeholder="CPF"
            value={cpf}
            onChange={(e) => setCpf(formatCpf(e.target.value))}
            inputMode="numeric"
            maxLength={14}
            className="focus-visible:ring-0 focus-visible:ring-offset-0 focus:ring-0 focus:ring-offset-0"
          />

          <Button
            onClick={() => {
              if (!isValid) return;
              onSubmit({ nome, cpf });
              onClose();
            }}
            disabled={!isValid}
            className={`w-full text-white ${
              isValid
                ? "bg-[#2F80ED] hover:bg-[#2563eb]"
                : "bg-[#2F80ED]/50 cursor-not-allowed"
            }`}
          >
            Confirmar e salvar exame
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
