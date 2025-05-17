export const runtime = "nodejs";

import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { dbConnect } from "@/lib/mongoose";
import Exam from "@/models/Exam";
import { MongoClient, GridFSBucket, ObjectId } from "mongodb";
import fs from "fs";
import os from "os";
import path from "path";
import { openai } from "@/lib/openai";

const MONGODB_URI = process.env.MONGODB_URI!;
const DATABASE_NAME = process.env.MONGODB_DB || "biolab";

export async function POST(req: NextRequest) {
    try {
        console.log("[API] Início da análise via GPT-4 com PDF");

        const token = await getToken({ req });
        if (!token?.sub) {
            console.log("[API] Token inválido ou ausente");
            return NextResponse.json({ message: "Não autenticado" }, { status: 401 });
        }

        const { examId } = await req.json();
        if (!examId) {
            console.log("[API] examId ausente");
            return NextResponse.json({ message: "ID do exame não fornecido" }, { status: 400 });
        }

        console.log(`[API] ID do exame recebido: ${examId}`);

        const client = await MongoClient.connect(MONGODB_URI);
        const db = client.db(DATABASE_NAME);
        const bucket = new GridFSBucket(db, { bucketName: "pdfs" });

        await dbConnect();
        const exam = await Exam.findById(examId);
        if (!exam) {
            console.log("[API] Exame não encontrado no banco");
            return NextResponse.json({ message: "Exame não encontrado" }, { status: 404 });
        }

        const tempPath = path.join(os.tmpdir(), `exam-${examId}.pdf`);
        const writeStream = fs.createWriteStream(tempPath);
        const downloadStream = bucket.openDownloadStream(new ObjectId(exam.sourceFile));

        console.log("[API] Baixando arquivo do GridFS...");
        await new Promise<void>((resolve, reject) => {
            downloadStream.pipe(writeStream);
            downloadStream.on("error", reject);
            writeStream.on("finish", () => resolve());
        });
        console.log("[API] Arquivo salvo temporariamente:", tempPath);

        const file = await openai.files.create({
            file: fs.createReadStream(tempPath),
            purpose: "assistants",
        });
        console.log("[API] Arquivo enviado à OpenAI. ID:", file.id);

        const assistant = await openai.beta.assistants.create({
            name: "Analista de Exames Médicos",
            instructions: "Você é um médico que interpreta exames laboratoriais.",
            model: "gpt-4-1106-preview",
            tools: [{ type: "file_search" }],
        });
        console.log("[API] Assistant criado:", assistant.id);

        const thread = await openai.beta.threads.create();
        console.log("[API] Thread criada:", thread.id);

        await openai.beta.threads.messages.create(thread.id, {
            role: "user",
            content: "Analise o exame médico em PDF e forneça um parecer clínico.",
            attachments: [{ file_id: file.id, tools: [{ type: "file_search" }] }],
        });
        console.log("[API] Mensagem enviada com o PDF");

        const run = await openai.beta.threads.runs.create(thread.id, {
            assistant_id: assistant.id,
        });
        console.log("[API] Run iniciado:", run.id);

        let status = "queued";
        while (status !== "completed" && status !== "failed") {
            await new Promise((r) => setTimeout(r, 1500));
            const runCheck = await openai.beta.threads.runs.retrieve(thread.id, run.id);
            status = runCheck.status;
            console.log(`[API] Status do run: ${status}`);
        }

        if (status === "failed") {
            throw new Error("A execução da IA falhou.");
        }

        const messages = await openai.beta.threads.messages.list(thread.id);
        const assistantMessage = messages.data.find((m) => m.role === "assistant");

        const gptResponse =
            assistantMessage?.content
                .map((c) => ("text" in c ? c.text.value : ""))
                .join("\n") || "Sem resposta.";

        console.log("[API] Resposta da IA recebida");

        fs.unlinkSync(tempPath);
        console.log("[API] Arquivo temporário removido");

        exam.textExtracted = gptResponse;
        exam.analyzedAt = new Date();
        await exam.save();
        console.log("[API] Exame atualizado no banco");

        return NextResponse.json({
            message: "Análise concluída com sucesso",
            gptResponse,
        });
    } catch (err: any) {
        console.error("[API] Erro ao processar análise:", err);
        return NextResponse.json(
            { message: "Erro ao processar PDF com GPT", error: err.message },
            { status: 500 }
        );
    }
}
