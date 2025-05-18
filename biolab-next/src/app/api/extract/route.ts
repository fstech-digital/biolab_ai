// import { NextRequest, NextResponse } from "next/server";
// import { request } from "undici";
// import { Readable } from "stream";
// import { dbConnect } from "@/lib/mongoose";
// import Exam from "@/models/Exam";

// async function readableStreamToNode(stream: ReadableStream<Uint8Array> | null): Promise<Readable> {
//     const reader = stream?.getReader();
//     return new Readable({
//         async read() {
//             if (!reader) return this.push(null);
//             const { done, value } = await reader.read();
//             if (done) return this.push(null);
//             this.push(Buffer.from(value));
//         },
//     });
// }

// export async function POST(req: NextRequest) {
//     try {
//         // Clona a requisição antes de ler body (necessário para reuso)
//         const clone = req.clone();
//         const formData = await clone.formData();
//         const examId = formData.get("examId")?.toString();

//         if (!examId) {
//             return NextResponse.json({ message: "examId ausente" }, { status: 400 });
//         }

//         // Converte corpo para Readable (para enviar ao microserviço)
//         const nodeStream = await readableStreamToNode(req.body);

//         const headers: Record<string, string> = {};
//         req.headers.forEach((value, key) => {
//             if (typeof value === "string") {
//                 headers[key] = value;
//             }
//         });

//         const { body, statusCode } = await request(
//             `${process.env.NEXT_PUBLIC_API_URL}/extract`,
//             {
//                 method: "POST",
//                 headers,
//                 body: nodeStream,
//             }
//         );

//         const data = await body.json();
//         const extractedText = data?.text;

//         if (!extractedText) {
//             return NextResponse.json({ message: "Texto extraído vazio" }, { status: 500 });
//         }

//         // Salva no banco de dados
//         await dbConnect();
//         const exam = await Exam.findById(examId);
//         if (!exam) {
//             return NextResponse.json({ message: "Exame não encontrado" }, { status: 404 });
//         }

//         exam.textExtracted = extractedText;
//         exam.analyzedAt = new Date();
//         await exam.save();

//         return NextResponse.json({
//             message: "Texto extraído e salvo com sucesso",
//             text: extractedText,
//         }, { status: statusCode });

//     } catch (err: any) {
//         console.error("[ROTA EXTRACT] Erro ao redirecionar:", err);
//         return NextResponse.json(
//             { message: "Erro ao extrair texto", error: err.message },
//             { status: 500 }
//         );
//     }
// }
