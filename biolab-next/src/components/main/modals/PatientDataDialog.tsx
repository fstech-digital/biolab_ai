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
  defaultDob?: string;
  defaultGender?: string;
  onClose: () => void;
  onSubmit: (data: {
    nome: string;
    cpf: string;
    data_nascimento: string;
    genero: string;
  }) => void;
}

function formatCpf(value: string) {
  const numbers = value.replace(/\D/g, "");
  return numbers
    .replace(/^(\d{3})(\d)/, "$1.$2")
    .replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/\.(\d{3})\.(\d{3})(\d)/, ".$1.$2-$3")
    .slice(0, 14);
}

function formatDate(value: string) {
  const numbers = value.replace(/\D/g, "");
  return numbers
    .replace(/^(\d{2})(\d)/, "$1/$2")
    .replace(/^(\d{2})\/(\d{2})(\d)/, "$1/$2/$3")
    .slice(0, 10);
}

export default function PatientDataDialog({
  open,
  defaultName = "",
  defaultCpf = "",
  defaultDob = "",
  defaultGender = "Masculino",
  onClose,
  onSubmit,
}: PatientDataDialogProps) {
  const [nome, setNome] = useState(defaultName);
  const [cpf, setCpf] = useState(formatCpf(defaultCpf));
  const [dataNascimento, setDataNascimento] = useState(formatDate(defaultDob));
  const [genero, setGenero] = useState(defaultGender);

  useEffect(() => {
    setNome(defaultName);
    setCpf(formatCpf(defaultCpf));
    setDataNascimento(formatDate(defaultDob));
    setGenero(defaultGender);
  }, [defaultName, defaultCpf, defaultDob, defaultGender]);

  const isValidCpf = cpf.length === 14;
  const isValidDate = /^\d{2}\/\d{2}\/\d{4}$/.test(dataNascimento);
  const isValidGender = genero === "Masculino" || genero === "Feminino";
  const isValid =
    nome.trim().length > 0 && isValidCpf && isValidDate && isValidGender;

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
          />

          <Input
            placeholder="CPF"
            value={cpf}
            onChange={(e) => setCpf(formatCpf(e.target.value))}
            inputMode="numeric"
            maxLength={14}
          />

          <Input
            placeholder="Data de nascimento (DD/MM/AAAA)"
            value={dataNascimento}
            onChange={(e) => setDataNascimento(formatDate(e.target.value))}
            inputMode="numeric"
            maxLength={10}
          />

          <select
            value={genero}
            onChange={(e) => setGenero(e.target.value)}
            className="flex h-10 w-full rounded-md border border-[#6FCF97] bg-white px-3 py-2 text-base text-[#0F1C2E] placeholder-[#666] focus:outline-none focus:ring-2 focus:ring-[#6FCF97] focus:border-[#6FCF97] focus:ring-offset-0 transition disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
          >
            <option value="Masculino">Masculino</option>
            <option value="Feminino">Feminino</option>
          </select>

          <Button
            onClick={() => {
              if (!isValid) return;
              onSubmit({ nome, cpf, data_nascimento: dataNascimento, genero });
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
