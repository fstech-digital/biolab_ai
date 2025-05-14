import { Schema, model, models } from 'mongoose';

const PatientSchema = new Schema({
    name: String,
    cpf: String,
    birthDate: Date,
    gender: { type: String, enum: ['M', 'F'] },
    createdBy: { type: Schema.Types.ObjectId, ref: 'User' },
}, { timestamps: true });

export default models.Patient || model('Patient', PatientSchema);