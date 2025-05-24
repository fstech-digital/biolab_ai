"use client";

import React from "react";
import { Card, CardContent } from "../ui/card";

interface ValorReferencia {
  sexo: string;
  idade: string;
  valores: string;
}

interface Subexame {
  nome: string;
  resultado: string;
  unidade: string;
  valor_referencia?: ValorReferencia[] | null;
  subexames?: Subexame[] | null;
}

interface Exame {
  nome: string;
  resultado: string;
  unidade: string;
  metodo: string;
  material: string;
  data_coleta: string;
  data_liberacao: string;
  valor_referencia?: ValorReferencia[] | null;
  subexames?: Subexame[] | null;
}

interface Paciente {
  nome: string;
  cpf: string;
  data_nascimento: string;
  genero: string;
  rg: string;
  convenio: string;
  codigo_os: string;
  atendimento: string;
  medico: string;
}

interface Laboratorio {
  nome: string;
  crm: string;
  cnes: string;
  responsavel_tecnico: string;
  endereco: string;
}

interface AnalysisResult {
  paciente?: Paciente;
  laboratorio?: Laboratorio;
  exames?: Exame[];
}

interface Props {
  result: AnalysisResult;
}

export default function ExamResultDisplay({ result }: Props) {
  const renderSubexames = (subs?: Subexame[] | null, level = 1) => {
    if (!subs) return null;
    return subs.map((sub, idx) => (
      <div key={idx} className={`pl-${level * 4} mt-2`}>
        <p className="font-semibold text-sm">
          {sub.nome}:{" "}
          <span className="font-normal">
            {sub.resultado} {sub.unidade}
          </span>
        </p>
        {Array.isArray(sub.valor_referencia) &&
          sub.valor_referencia.length > 0 && (
            <ul className="text-xs text-muted-foreground ml-4 list-disc">
              {sub.valor_referencia.map((v, i) => (
                <li key={i}>
                  {v.sexo ? `${v.sexo}, ` : ""}
                  {v.idade ? `${v.idade}: ` : ""}
                  {v.valores}
                </li>
              ))}
            </ul>
          )}
        {renderSubexames(sub.subexames, level + 1)}
      </div>
    ));
  };

  return (
    <div className="mt-6 w-full max-w-4xl mx-auto space-y-6">
      {result.paciente && (
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-bold mb-2">Dados do Paciente</h2>
            <div className="grid grid-cols-2 text-sm gap-1">
              {Object.entries(result.paciente).map(([key, value]) => (
                <div key={key}>
                  <strong>{key.replace(/_/g, " ")}:</strong> {value}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {result.laboratorio && (
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-bold mb-2">Laboratório</h2>
            <div className="grid grid-cols-2 text-sm gap-1">
              {Object.entries(result.laboratorio).map(([key, value]) => (
                <div key={key}>
                  <strong>{key.replace(/_/g, " ")}:</strong> {value}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {Array.isArray(result.exames) &&
        result.exames.map((exame, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <h3 className="text-lg font-bold mb-2">{exame.nome}</h3>
              <div className="text-sm mb-2">
                {exame.resultado && (
                  <p>
                    <strong>Resultado:</strong> {exame.resultado}{" "}
                    {exame.unidade}
                  </p>
                )}
                <p>
                  <strong>Material:</strong> {exame.material}
                </p>
                <p>
                  <strong>Método:</strong> {exame.metodo}
                </p>
                <p>
                  <strong>Data Coleta:</strong> {exame.data_coleta}
                </p>
                <p>
                  <strong>Data Liberação:</strong> {exame.data_liberacao}
                </p>
                {Array.isArray(exame.valor_referencia) &&
                  exame.valor_referencia.length > 0 && (
                    <>
                      <strong>Valores de Referência:</strong>
                      <ul className="text-xs text-muted-foreground ml-4 list-disc">
                        {exame.valor_referencia.map((v, i) => (
                          <li key={i}>
                            {v.sexo ? `${v.sexo}, ` : ""}
                            {v.idade ? `${v.idade}: ` : ""}
                            {v.valores}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
              </div>
              {renderSubexames(exame.subexames)}
            </CardContent>
          </Card>
        ))}
    </div>
  );
}
