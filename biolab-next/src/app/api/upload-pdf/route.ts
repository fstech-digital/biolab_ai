import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { MongoClient, GridFSBucket, ObjectId } from "mongodb";
import { dbConnect } from "@/lib/mongoose";
import Exam from "@/models/Exam";

const MONGODB_URI = process.env.MONGODB_URI!;
const DATABASE_NAME = process.env.MONGODB_DB || "biolab";

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

    // Conecte-se ao Mongo
    const client = await MongoClient.connect(MONGODB_URI);
    const db = client.db(DATABASE_NAME);
    const bucket = new GridFSBucket(db, { bucketName: "pdfs" });

    const buffer = Buffer.from(await file.arrayBuffer());

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
            await dbConnect();
            const newExam = new Exam({
                uploadedBy: userId,
                patientId,
                collectedAt,
                sourceFile: uploadStream.id,
            });
            await newExam.save();

            resolve(
                NextResponse.json({
                    message: "Upload concluído (GridFS)",
                    examId: newExam._id,
                })
            );
        });

        uploadStream.on("error", (err) => {
            reject(NextResponse.json({ message: "Erro ao salvar PDF", error: err }));
        });
    });
}
