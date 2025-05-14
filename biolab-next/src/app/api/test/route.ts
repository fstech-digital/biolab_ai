import { dbConnect } from '@/lib/mongoose'
import { NextResponse } from 'next/server'
import mongoose from 'mongoose'

const TestSchema = new mongoose.Schema({ name: String })
const Test = mongoose.models.Test || mongoose.model('Test', TestSchema)

export async function GET() {
    try {
        await dbConnect()

        await Test.create({ name: 'Registro de teste' })

        return NextResponse.json({ message: 'Inserido no MongoDB!' })
    } catch (error) {
        return NextResponse.json({ error: 'Erro ao inserir no MongoDB' }, { status: 500 })
    }
}
