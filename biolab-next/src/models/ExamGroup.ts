import mongoose from "mongoose";


export interface IExamGroup extends Document {
    patient: mongoose.Types.ObjectId;
    exam: mongoose.Types.ObjectId;
    lab: {
        name: string;
        crm: string;
        cnes: string;
        responsible: string;
        address: string;
    };
    createdAt: Date;
    updatedAt: Date;
}


const ExamGroupSchema = new mongoose.Schema({
    patient: { type: mongoose.Schema.Types.ObjectId, ref: "Patient", required: true },
    exam: { type: mongoose.Schema.Types.ObjectId, ref: "Exam", required: true },
    lab: {
        name: String,
        crm: String,
        cnes: String,
        responsible: String,
        address: String,
    },
    createdAt: { type: Date, default: Date.now },
}, { timestamps: true });

export default mongoose.models.ExamGroup || mongoose.model<IExamGroup>("ExamGroup", ExamGroupSchema);
