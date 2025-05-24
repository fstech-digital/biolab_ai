// models/Patient.ts
import mongoose, { Document } from "mongoose";

export interface IPatient extends Document {
    name: string;
    cpf: string;
    birthDate?: string;
    gender?: string;
    rg?: string;
    insurance?: string;
    osCode?: string;
    appointmentDate?: string;
    doctor?: string;
    createdAt: Date;
    updatedAt: Date;
}

const PatientSchema = new mongoose.Schema<IPatient>({
    name: {
        type: String,
        required: [true, "Nome é obrigatório"],
        trim: true,
    },
    cpf: {
        type: String,
        required: [true, "CPF é obrigatório"],
        unique: true,
        trim: true,
    },
    birthDate: String,
    gender: String,
    rg: String,
    insurance: String,
    osCode: String,
    appointmentDate: String,
    doctor: String,
}, { timestamps: true });

export default mongoose.models.Patient || mongoose.model<IPatient>("Patient", PatientSchema);
