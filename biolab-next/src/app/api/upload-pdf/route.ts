import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { MongoClient, GridFSBucket } from "mongodb";
import { dbConnect } from "@/lib/mongoose";
import Exam from "@/models/Exam";
import { request } from "undici";
import { Readable } from "stream";
import FormData from "form-data";


const MONGODB_URI = process.env.MONGODB_URI!;
const DATABASE_NAME = process.env.MONGODB_DB || "biolab";
const EXTRACT_API = process.env.NEXT_PUBLIC_API_URL + "/extract";

async function bufferToReadable(buffer: Buffer): Promise<Readable> {
    return new Readable({
        read() {
            this.push(buffer);
            this.push(null);
        },
    });
}

export async function POST(req: NextRequest) {
    const token = await getToken({ req });
    const userId = token?.sub;

    if (!userId) {
        return NextResponse.json({ message: "Não autenticado" }, { status: 401 });
    }

    const formData = await req.formData();
    const file = formData.get("pdf") as File;
    const patientId = formData.get("patientId")?.toString() || null;
    const collectedAtRaw = formData.get("collectedAt")?.toString();
    const collectedAt = collectedAtRaw ? new Date(collectedAtRaw) : undefined;

    if (!file || file.type !== "application/pdf") {
        return NextResponse.json({ message: "Arquivo inválido" }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());

    // Conecte-se ao Mongo
    const client = await MongoClient.connect(MONGODB_URI);
    const db = client.db(DATABASE_NAME);
    const bucket = new GridFSBucket(db, { bucketName: "pdfs" });

    const uploadStream = bucket.openUploadStream(file.name, {
        metadata: {
            uploadedBy: userId,
            patientId,
            collectedAt,
        },
    });

    uploadStream.end(buffer);

    return new Promise((resolve, reject) => {
        uploadStream.on("finish", async () => {
            try {
                await dbConnect();
                const newExam = new Exam({
                    uploadedBy: userId,
                    patientId,
                    collectedAt,
                    sourceFile: uploadStream.id,
                });
                await newExam.save();

                const form = new FormData();
                form.append("pdf", buffer, {
                    filename: file.name,
                    contentType: "application/pdf",
                });

                const { body, statusCode } = await request(EXTRACT_API, {
                    method: "POST",
                    body: form,
                    headers: form.getHeaders(),
                });

                const json: unknown = await body.json();

                if (
                    typeof json === "object" &&
                    json !== null &&
                    "text" in json &&
                    typeof (json as any).text === "string"
                ) {
                    const extractedText = (json as any).text;
                    newExam.textExtracted = extractedText;
                    newExam.analyzedAt = new Date();
                    await newExam.save();

                    return resolve(
                        NextResponse.json(
                            {
                                message: "Upload e extração concluídos com sucesso",
                                examId: newExam._id,
                                extractedText,
                            },
                            { status: statusCode || 200 }
                        )
                    );
                } else {
                    return resolve(
                        NextResponse.json({ message: "Resposta inválida da API externa" }, { status: 422 })
                    );
                }
            } catch (err: any) {
                reject(
                    NextResponse.json({ message: "Erro durante o processo", error: err.message }, { status: 500 })
                );
            }
        });

        uploadStream.on("error", (err) => {
            reject(NextResponse.json({ message: "Erro ao salvar PDF", error: err }));
        });
    });
}
