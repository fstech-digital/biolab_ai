"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import { FileText, Loader2, Upload } from "lucide-react";
import { Toaster } from "@/components/ui/toaster";
import ExamResultDisplay from "@/components/main/ExamResultDisplay";
import PatientDataDialog from "@/components/main/modals/PatientDataDialog";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [sessionLocked, setSessionLocked] = useState(false);
  const [loadingUpload, setLoadingUpload] = useState(false);
  const [loadingAnalyze, setLoadingAnalyze] = useState(false);

  const [extractedText, setExtractedText] = useState<string | null>(null);
  const [examId, setExamId] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);

  const [showPatientModal, setShowPatientModal] = useState(false);
  const [missingPatientFields, setMissingPatientFields] = useState<{
    nome: string;
    cpf: string;
  }>({ nome: "", cpf: "" });
  const [parsedExamResult, setParsedExamResult] = useState<any | null>(null);

  const [analysisResult, setAnalysisResult] = useState<any | null>(null);

  const interactionDisabled = loadingUpload || loadingAnalyze || sessionLocked;

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

    setLoadingUpload(true);
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

      setExtractedText(data.extractedText || null);
      setExamId(data.examId);
      setFile(null);

      const input = document.getElementById("pdf-upload") as HTMLInputElement;
      if (input) input.value = "";

      toast({
        title: "Upload concluído",
        description: "Iniciando análise com IA...",
        variant: "info",
      });

      setLoadingAnalyze(true);

      const analysisRes = await fetch("/api/analyze-exam", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: data.extractedText, examId: data.examId }),
      });

      const analysisData = await analysisRes.json();

      if (!analysisRes.ok)
        throw new Error(analysisData.message || "Erro na análise");

      const parsedResult = JSON.parse(analysisData.result);
      parsedResult.examId = data.examId;

      setAnalysisResult(parsedResult);
      setParsedExamResult(parsedResult);
      setShowResult(false);

      const hasName = !!parsedResult?.paciente?.nome;
      const hasCpf = !!parsedResult?.paciente?.cpf;

      if (!hasName || !hasCpf) {
        setShowPatientModal(true);
        setMissingPatientFields({
          nome: parsedResult.paciente?.nome || "",
          cpf: parsedResult.paciente?.cpf || "",
        });
      } else {
        await sendToMiner({ ...parsedResult, examId: data.examId });
      }

      toast({
        title: "Análise concluída",
        description: "Análise realizada com sucesso.",
        variant: "success",
      });
    } catch (err: any) {
      toast({
        title: "Erro",
        description: err.message || "Erro inesperado durante envio ou análise.",
        variant: "destructive",
      });
    } finally {
      setLoadingUpload(false);
      setLoadingAnalyze(false);
      setSessionLocked(true);
    }
  };

  async function sendToMiner(data: any) {
    try {
      const saveRes = await fetch("/api/save-parsed-exam", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      const saveData = await saveRes.json();

      if (!saveRes.ok)
        throw new Error(saveData.message || "Erro ao minerar exame.");

      toast({
        title: "Exame minerado com sucesso",
        description: "Dados clínicos estruturados salvos.",
        variant: "success",
      });
    } catch (err: any) {
      toast({
        title: "Erro ao minerar exame",
        description: err.message || "Falha na estruturação dos dados.",
        variant: "destructive",
      });
    }
  }

  const handleMock = () => {
    const mockResult = require("@/mocks/mock-analysis.json");
    setAnalysisResult(mockResult);
    setShowResult(true);
    setSessionLocked(true);
  };

  return (
    <main className="min-h-screen bg-scientific-dark flex flex-col items-center justify-center px-4">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-xl space-y-5 border border-scientific-subtle">
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
            className={`flex items-center justify-between px-4 py-3 rounded-lg border border-dashed transition ${
              interactionDisabled
                ? "border-gray-300 bg-gray-100 cursor-not-allowed text-gray-400"
                : "border-scientific-highlight hover:bg-scientific-highlight/10 cursor-pointer text-black"
            }`}
          >
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              <span className="text-sm">
                {interactionDisabled
                  ? "Exame sendo analisado..."
                  : file
                  ? file.name
                  : "Selecionar arquivo PDF"}
              </span>
            </div>
            <Upload className="w-4 h-4 text-scientific-subtle" />
          </label>

          <Input
            id="pdf-upload"
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            disabled={interactionDisabled}
            className="hidden"
          />

          <Button
            onClick={handleUpload}
            disabled={interactionDisabled || !file}
            className={`w-full ${
              interactionDisabled || !file
                ? "bg-scientific-success/50 cursor-not-allowed"
                : "bg-scientific-success hover:bg-scientific-highlight"
            } text-white`}
          >
            {loadingUpload || loadingAnalyze ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Enviando e analisando...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Enviar PDF
              </>
            )}
          </Button>
        </div>

        {analysisResult && (
          <div className="text-center">
            <Button
              variant="blue"
              className="w-full"
              onClick={() => setShowResult((prev) => !prev)}
            >
              {showResult ? "Ocultar dados do exame" : "Revisar dados do exame"}
            </Button>
          </div>
        )}

        {analysisResult && showResult && (
          <div className="w-full max-w-5xl mt-8">
            <ExamResultDisplay result={analysisResult} />
          </div>
        )}

        <Toaster />
      </div>

      {sessionLocked && (
        <div className="mt-6 text-center">
          <Button
            variant="secondary"
            onClick={() => {
              setFile(null);
              setExamId(null);
              setExtractedText(null);
              setSessionLocked(false);
              setAnalysisResult(null);

              const input = document.getElementById(
                "pdf-upload"
              ) as HTMLInputElement;
              if (input) input.value = "";
            }}
          >
            Nova Análise
          </Button>
        </div>
      )}

      <Button className="mt-24" variant="secondary" onClick={handleMock}>
        Mockar dados do exame
      </Button>

      <PatientDataDialog
        open={showPatientModal}
        defaultName={missingPatientFields.nome}
        defaultCpf={missingPatientFields.cpf}
        onClose={() => setShowPatientModal(false)}
        onSubmit={async (filled) => {
          if (!parsedExamResult) return;

          parsedExamResult.paciente.nome = filled.nome;
          parsedExamResult.paciente.cpf = filled.cpf;

          await sendToMiner(parsedExamResult);
        }}
      />
    </main>
  );
}
