// models/Patient.ts
import mongoose from "mongoose";

const PatientSchema = new mongoose.Schema({
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

export default mongoose.models.Patient || mongoose.model("Patient", PatientSchema);
