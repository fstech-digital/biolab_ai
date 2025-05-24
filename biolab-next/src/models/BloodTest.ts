// models/BloodTest.ts
import mongoose from "mongoose";

const ReferenceValueSchema = new mongoose.Schema({
    gender: String,
    age: String,
    values: String,
}, { _id: false });

const BloodTestSchema = new mongoose.Schema({
    examBundle: { type: mongoose.Schema.Types.ObjectId, ref: "ExamBundle", required: true },
    name: String,
    result: String,
    unit: String,
    collectedAt: String,
    releasedAt: String,
    method: String,
    material: String,
    referenceValues: [ReferenceValueSchema],
    subTests: [{ type: mongoose.Schema.Types.ObjectId, ref: "BloodTest" }],
}, { timestamps: true });

export default mongoose.models.BloodTest || mongoose.model("BloodTest", BloodTestSchema);
