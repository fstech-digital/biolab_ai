import { NextResponse } from "next/server";
import { dbConnect } from "@/lib/mongoose";
import Exam from "@/models/Exam";
import "@/models/LocalUser";

export async function GET() {
    try {
        await dbConnect();

        const exams = await Exam.find()
            .sort({ createdAt: -1 })
            .populate("uploadedBy", "name email");


        return NextResponse.json(exams);
    } catch (error: any) {
        console.error("[GET /api/exam] Erro ao buscar exames:", error);
        return NextResponse.json(
            { message: "Erro interno", error: error.message },
            { status: 500 }
        );
    }
}
