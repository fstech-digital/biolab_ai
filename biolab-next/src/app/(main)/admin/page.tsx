"use client";

import { useEffect, useState } from "react";

type Exam = {
  _id: string;
  sourceFile: string;
  createdAt: string;
  collectedAt?: string;
  patientId?: string;
  uploadedBy?: {
    _id: string;
    name: string;
    email: string;
  };
};

export default function AdminDashboard() {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadExams = async () => {
      try {
        const res = await fetch("/api/exam");
        const data = await res.json();
        setExams(data);
      } catch (err) {
        console.error("Erro ao carregar exames:", err);
      } finally {
        setLoading(false);
      }
    };

    loadExams();
  }, []);

  return (
    <div className="min-h-[100vh] rounded-xl bg-muted/50 p-6">
      <h1 className="text-2xl font-bold mb-4 text-white">
        Painel do Administrador
      </h1>
      {loading ? (
        <p>Carregando exames...</p>
      ) : exams.length === 0 ? (
        <p>Nenhum exame encontrado.</p>
      ) : (
        <ul className="space-y-4">
          {exams.map((exam) => (
            <li key={exam._id} className="bg-white p-4 rounded-md shadow">
              <p>
                <strong>ID:</strong> {exam._id}
              </p>
              <p>
                <strong>Data:</strong>{" "}
                {new Date(exam.createdAt).toLocaleString("pt-BR")}
              </p>
              <p>
                <strong>Enviado por:</strong> {exam.uploadedBy?.name} (
                {exam.uploadedBy?.email})
              </p>

              <p>
                <strong>Arquivo:</strong>{" "}
                <a
                  href={`/api/exam/view?id=${exam.sourceFile}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline"
                >
                  Visualizar PDF
                </a>
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
