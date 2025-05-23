import mongoose from "mongoose";

const ExamGroupSchema = new mongoose.Schema({
    patient: { type: mongoose.Schema.Types.ObjectId, ref: "Patient", required: true },
    exam: { type: mongoose.Schema.Types.ObjectId, ref: "Exam", required: true }, // <- link para origem
    lab: {
        name: String,
        crm: String,
        cnes: String,
        responsible: String,
        address: String,
    },
    createdAt: { type: Date, default: Date.now },
}, { timestamps: true });

export default mongoose.models.ExamGroup || mongoose.model("ExamGroup", ExamGroupSchema);
