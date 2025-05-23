// /app/api/save-parsed-exam/route.ts
import { NextRequest, NextResponse } from "next/server";
import { dbConnect } from "@/lib/mongoose";

import Patient from "@/models/Patient";
import ExamGroup from "@/models/ExamGroup";
import BloodTest from "@/models/BloodTest";

async function saveBloodTestRecursively(
    examData: any,
    examGroupId: string,
    examBundleId: string,
    parentId: string | null = null
): Promise<string> {
    const {
        nome,
        resultado,
        unidade,
        data_coleta,
        data_liberacao,
        metodo,
        material,
        valor_referencia,
        subexames,
    } = examData;


    const referenceValues = Array.isArray(valor_referencia)
        ? valor_referencia
            .filter((v) => v && typeof v === "object")
            .map((v) => ({
                gender: v.sexo ?? "",
                age: v.idade ?? "",
                values: v.valores ?? "",
            }))
        : [];

    const bloodTest = new BloodTest({
        name: nome,
        result: resultado,
        unit: unidade,
        collectedAt: data_coleta,
        releasedAt: data_liberacao,
        method: metodo,
        material: material,
        referenceValues,
        examGroup: examGroupId,
        examBundle: examBundleId,
        subTests: [],
        parent: parentId || null,
    });

    await bloodTest.save();

    if (Array.isArray(subexames)) {
        for (const sub of subexames) {
            const subId = await saveBloodTestRecursively(sub, examGroupId, examBundleId, bloodTest._id);
            bloodTest.subTests.push(subId);
        }
        await bloodTest.save();
    }

    return bloodTest._id;
}

export async function POST(req: NextRequest) {
    try {
        await dbConnect();

        const { paciente, laboratorio, exames, examId } = await req.json();

        if (!paciente?.cpf || !paciente?.nome) {
            const missing = [
                !paciente?.nome && "nome",
                !paciente?.cpf && "cpf",
            ].filter(Boolean).join(" e ");

            return NextResponse.json(
                { message: `Paciente sem ${missing}.` },
                { status: 400 }
            );
        }

        let patient = await Patient.findOne({ cpf: paciente.cpf });

        if (!patient) {
            patient = await Patient.create({
                name: paciente.nome,
                cpf: paciente.cpf,
                birthDate: paciente.data_nascimento,
                gender: paciente.genero,
                rg: paciente.rg,
                insurance: paciente.convenio,
                osCode: paciente.codigo_os,
                appointmentDate: paciente.atendimento,
                doctor: paciente.medico,
            });
        }

        const examGroup = await ExamGroup.create({
            patient: patient._id,
            exam: examId,
            lab: {
                name: laboratorio.nome,
                crm: laboratorio.crm,
                cnes: laboratorio.cnes,
                responsible: laboratorio.responsavel_tecnico,
                address: laboratorio.endereco,
            },
        });

        for (const exam of exames) {
            await saveBloodTestRecursively(exam, examGroup._id, examId);
        }

        return NextResponse.json({ message: "Exame salvo com sucesso" }, { status: 201 });
    } catch (error: any) {
        console.error("Erro ao salvar exame:", error);
        return NextResponse.json({ message: "Erro interno", error: error.message }, { status: 500 });
    }
}
