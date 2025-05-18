import { NextRequest, NextResponse } from "next/server";
import OpenAI from "openai";
import { dbConnect } from "@/lib/mongoose";
import Exam from "@/models/Exam";

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

const assistantId = "asst_jHCHmh76WebWpVpFaIH2Z37K";

export async function POST(req: NextRequest) {
    try {
        const { text, examId } = await req.json();

        console.log("🔹 Requisição recebida");
        console.log("📝 Texto:", text?.slice(0, 100) + "...");
        console.log("📄 examId:", examId);

        if (!text || !examId) {
            console.warn("⚠️ Texto ou ID do exame ausente");
            return NextResponse.json({ message: "Texto ou ID do exame não fornecido" }, { status: 400 });
        }

        console.log("🧠 Criando thread com OpenAI...");
        const thread = await openai.beta.threads.create();

        await openai.beta.threads.messages.create(thread.id, {
            role: "user",
            content: `Analise o seguinte texto extraído de um exame de sangue e me forneça um resumo clínico em linguagem simples: \n\n${text}`,
        });

        console.log("▶️ Iniciando execução do assistente...");
        const run = await openai.beta.threads.runs.create(thread.id, {
            assistant_id: assistantId,
        });

        let completed = false;
        let result: string | null = null;

        const maxTries = 36; // 36 tentativas × 5s = 180s = 3 minutos
        const delay = 5000; // 5 segundos

        for (let i = 0; i < maxTries; i++) {
            console.log(`⏳ Verificando status da execução (${i + 1}/${maxTries})...`);
            const runStatus = await openai.beta.threads.runs.retrieve(thread.id, run.id);

            if (runStatus.status === "completed") {
                console.log("✅ Execução concluída");
                const messages = await openai.beta.threads.messages.list(thread.id);
                result = messages.data[0].content
                    .map((c) => ("text" in c ? c.text.value : ""))
                    .join("\n");
                completed = true;
                break;
            }

            await new Promise((r) => setTimeout(r, delay));
        }

        if (!completed) {
            console.error("⏱️ Execução demorou demais");
            return NextResponse.json({ message: "Análise demorou demais" }, { status: 408 });
        }

        console.log("🌐 Conectando ao banco de dados...");
        await dbConnect();
        const exam = await Exam.findById(examId);

        if (!exam) {
            console.error("❌ Exame não encontrado no banco");
            return NextResponse.json({ message: "Exame não encontrado" }, { status: 404 });
        }

        console.log("💾 Salvando resultado no banco...");
        exam.analysisResult = result;
        await exam.save();

        console.log("🎉 Resultado salvo com sucesso!");

        return NextResponse.json({ result });
    } catch (error: any) {
        console.error("🚨 Erro geral:", error.message);
        return NextResponse.json({ message: "Erro ao analisar", error: error.message }, { status: 500 });
    }
}
