import { Schema, model, models } from 'mongoose'

const LocalUserSchema = new Schema({
    name: String,
    email: { type: String, unique: true },
    password: String,
}, { timestamps: true })

export default models.LocalUser || model('LocalUser', LocalUserSchema)
