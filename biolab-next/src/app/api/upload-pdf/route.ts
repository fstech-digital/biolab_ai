import { NextRequest, NextResponse } from "next/server";
import { getToken } from "next-auth/jwt";
import { dbConnect } from "@/lib/mongoose";
import Exam from "@/models/Exam";
import fs from "fs/promises";
import path from "path";
import { v4 as uuidv4 } from "uuid";

export async function POST(req: NextRequest) {
    const token = await getToken({ req });
    const userId = token?.sub;

    if (!userId) {
        return NextResponse.json({ message: "Não autenticado" }, { status: 401 });
    }

    await dbConnect();

    const formData = await req.formData();
    const file = formData.get("pdf") as File;
    const patientId = formData.get("patientId")?.toString() || null;
    const collectedAtRaw = formData.get("collectedAt")?.toString();
    const collectedAt = collectedAtRaw ? new Date(collectedAtRaw) : undefined;

    if (!file || file.type !== "application/pdf") {
        return NextResponse.json({ message: "Arquivo inválido" }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());

    const uploadDir = path.join(process.cwd(), "public", "uploads");
    await fs.mkdir(uploadDir, { recursive: true });

    const filename = `${uuidv4()}.pdf`;
    const filepath = path.join(uploadDir, filename);
    await fs.writeFile(filepath, buffer);

    const newExam = new Exam({
        uploadedBy: userId,
        patientId,
        collectedAt,
        sourceFile: `/uploads/${filename}`,
    });

    await newExam.save();

    return NextResponse.json({ message: "Upload concluído", examId: newExam._id });
}
