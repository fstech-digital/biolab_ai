import { Schema, model, models } from 'mongoose';

const ExamResultSchema = new Schema({
    examId: { type: Schema.Types.ObjectId, ref: 'Exam' },
    parameter: String,
    value: Number,
    unit: String,
    referenceMin: Number,
    referenceMax: Number,
    referenceNotes: String,
    aiObservation: String,
    comparisonWithPrevious: {
        previousValue: Number,
        delta: Number,
        possibleCauses: [String],
    },
}, { timestamps: true });

export default models.ExamResult || model('ExamResult', ExamResultSchema);