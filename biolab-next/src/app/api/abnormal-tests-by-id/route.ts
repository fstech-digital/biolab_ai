import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "@/lib/mongoose";
import BloodTest from "@/models/BloodTest";
import ExamGroup, { IExamGroup } from "@/models/ExamGroup";
import Patient, { IPatient } from "@/models/Patient";

type ReferenceValue = {
    gender: string;
    age: string;
    values: string;
};

type TestWithStatus = any & {
    status: "normal" | "acima" | "abaixo";
};

function sanitizeNumber(raw: string): number {
    return parseFloat(raw.replace(/\./g, "").replace(",", "."));
}

function parseReferenceRange(range: string): [number, number] | null {
    const match = range.match(/([\d.,]+)\s*(?:a|-)\s*([\d.,]+)/i);
    if (!match) return null;
    const [, minRaw, maxRaw] = match;
    const min = sanitizeNumber(minRaw);
    const max = sanitizeNumber(maxRaw);
    return isNaN(min) || isNaN(max) ? null : [min, max];
}

function analyzeResult(result: string, refRanges: string[]): "normal" | "acima" | "abaixo" {
    const numericResult = sanitizeNumber(result);
    if (isNaN(numericResult)) return "normal";
    for (const range of refRanges) {
        const parsed = parseReferenceRange(range);
        if (!parsed) continue;
        const [min, max] = parsed;
        if (numericResult < min) return "abaixo";
        if (numericResult > max) return "acima";
        return "normal";
    }
    return "normal";
}

function calcularIdade(dataNascimento: string): number {
    const [dia, mes, ano] = dataNascimento.split("/").map(Number);
    const nascimento = new Date(ano, mes - 1, dia);
    const hoje = new Date();
    let idade = hoje.getFullYear() - nascimento.getFullYear();
    const m = hoje.getMonth() - nascimento.getMonth();
    if (m < 0 || (m === 0 && hoje.getDate() < nascimento.getDate())) {
        idade--;
    }
    return idade;
}

function getMatchingRangeByAgeAndGender(
    references: ReferenceValue[],
    gender: string,
    birthDate: string
): string[] {
    const idade = calcularIdade(birthDate);
    const normalizedGender = gender.trim().toLowerCase();

    const genderMap: Record<string, string[]> = {
        masculino: ["masculino", "homem", "homens", "h", "m", "masc"],
        feminino: ["feminino", "mulher", "mulheres", "f", "fem"]
    };

    const ageMatch = references.find((ref) => {
        const tag = ref.gender?.toLowerCase() || "";
        return (
            (idade < 13 && tag.includes("crianç")) ||
            (idade >= 70 && tag.includes("70")) ||
            (idade >= 13 && idade < 70 && tag.includes("adult"))
        );
    });

    if (ageMatch) return [ageMatch.values];

    const genderMatches = references
        .filter((ref) => {
            const refGender = ref.gender?.toLowerCase() || "";
            return genderMap[normalizedGender]?.some((alias) =>
                refGender.includes(alias)
            );
        })
        .map((ref) => ref.values);

    if (genderMatches.length > 0) return genderMatches;

    return references.map((ref) => ref.values);
}

export async function POST(req: NextRequest) {
    try {
        await dbConnect();

        const { examId } = await req.json();
        if (!examId) {
            return NextResponse.json({ message: "examId obrigatório" }, { status: 400 });
        }

        const examGroup = await ExamGroup.findOne({ exam: examId }).lean<IExamGroup>();
        if (!examGroup) {
            return NextResponse.json({ message: "ExamGroup não encontrado" }, { status: 404 });
        }

        const patient = await Patient.findById(examGroup.patient).lean<IPatient>();
        if (!patient) {
            return NextResponse.json({ message: "Paciente não encontrado" }, { status: 404 });
        }

        const patientGender = patient.gender?.toLowerCase() || "";

        if (!patient.birthDate) {
            return NextResponse.json(
                { message: "Data de nascimento do paciente ausente." },
                { status: 400 }
            );
        }

        const patientBirthDate = patient.birthDate;

        const tests = await BloodTest.find({ examBundle: examId }).lean();

        const altered: TestWithStatus[] = [];

        for (const test of tests) {
            const result = test.result;
            const unit = test.unit;
            const refValues: ReferenceValue[] = test.referenceValues || [];

            if (!result || !refValues.length) continue;

            const refRanges = getMatchingRangeByAgeAndGender(refValues, patientGender, patientBirthDate);
            const status = analyzeResult(result, refRanges);

            if (status !== "normal") {
                altered.push({ ...test, status });
            }
        }

        return NextResponse.json({ altered }, { status: 200 });
    } catch (err: any) {
        console.error("Erro:", err);
        return NextResponse.json({ message: "Erro interno", error: err.message }, { status: 500 });
    }
}
