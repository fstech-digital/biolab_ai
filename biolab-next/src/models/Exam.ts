import { Schema, model, models } from 'mongoose';

const ExamSchema = new Schema({
    patientId: { type: Schema.Types.ObjectId, ref: 'Patient' },
    uploadedBy: { type: Schema.Types.ObjectId, ref: 'LocalUser' },
    sourceFile: { type: Schema.Types.ObjectId, required: true },
    analyzedAt: Date,
    jsonExtract: Schema.Types.Mixed,
    aiSummary: String,
}, { timestamps: true });

export default models.Exam || model('Exam', ExamSchema);