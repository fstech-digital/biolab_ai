"use client";

import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "../ui/scroll-area";
import { Badge } from "../ui/badge";

interface TestItem {
  name: string;
  result: string;
  unit: string;
  status: "acima" | "abaixo" | "normal";
  referenceValues: { values: string }[];
}

interface AbnormalTestListProps {
  alteredTests: TestItem[];
}

export default function AbnormalTestList({
  alteredTests,
}: AbnormalTestListProps) {
  if (!alteredTests || alteredTests.length === 0) {
    return (
      <div className="text-center mt-6 text-gray-500 text-sm">
        Nenhum exame alterado foi identificado.
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mt-6">
      <h2 className="text-xl font-bold mb-4 text-scientific-highlight">
        Exames Alterados
      </h2>
      <ScrollArea className="h-64 pr-4">
        <div className="space-y-3">
          {alteredTests.map((test, index) => (
            <Card key={index} className="border-l-4 shadow-md bg-white">
              <CardContent className="p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold text-md">{test.name}</h3>
                    <p className="text-sm text-gray-600">
                      Resultado: <strong>{test.result}</strong> {test.unit}
                    </p>
                    {test.referenceValues?.length > 0 && (
                      <p className="text-xs text-gray-500">
                        Referência:{" "}
                        {test.referenceValues
                          .map((ref) => ref.values)
                          .join(" ou ")}
                      </p>
                    )}
                  </div>
                  <Badge
                    variant={
                      test.status === "acima" ? "destructive" : "warning"
                    }
                  >
                    {test.status === "acima" ? "Acima" : "Abaixo"}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
