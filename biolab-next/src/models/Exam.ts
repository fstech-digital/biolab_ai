import { Schema, model, models } from 'mongoose';

const ExamSchema = new Schema({
    patientId: { type: Schema.Types.ObjectId, ref: 'Patient' },
    uploadedBy: { type: Schema.Types.ObjectId, ref: 'User' },
    sourceFile: String,
    collectedAt: Date,
    analyzedAt: Date,
    jsonExtract: Schema.Types.Mixed,
    aiSummary: String,
}, { timestamps: true });

export default models.Exam || model('Exam', ExamSchema);