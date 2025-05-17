import { NextRequest } from "next/server";
import { getToken } from "next-auth/jwt";
import { MongoClient, ObjectId, GridFSBucket } from "mongodb";
import { dbConnect } from "@/lib/mongoose";
import Exam from "@/models/Exam";

const MONGODB_URI = process.env.MONGODB_URI!;

export async function GET(req: NextRequest) {
    const token = await getToken({ req });
    if (!token?.sub) {
        return new Response("Não autenticado", { status: 401 });
    }

    const url = new URL(req.url);
    const fileId = url.searchParams.get("id");

    if (!fileId || !ObjectId.isValid(fileId)) {
        return new Response("ID inválido", { status: 400 });
    }

    await dbConnect();

    const exam = await Exam.findOne({ sourceFile: fileId });
    if (!exam) return new Response("Exame não encontrado", { status: 404 });

    if (exam.uploadedBy.toString() !== token.sub) {
        return new Response("Acesso negado", { status: 403 });
    }

    const client = await MongoClient.connect(MONGODB_URI);
    const db = client.db();
    const bucket = new GridFSBucket(db, { bucketName: "pdfs" });

    const stream = bucket.openDownloadStream(new ObjectId(fileId));

    return new Response(stream as any, {
        headers: {
            "Content-Type": "application/pdf",
            "Content-Disposition": "inline; filename=exame.pdf",
        },
    });
}
