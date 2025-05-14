import { NextResponse } from 'next/server'
import bcrypt from 'bcryptjs'
import LocalUser from '@/models/LocalUser'

export async function POST(req: Request) {
    try {
        const { name, email, password } = await req.json()

        if (!name || !email || !password) {
            return NextResponse.json({ message: 'Campos obrigatórios não preenchidos' }, { status: 400 })
        }

        const existing = await LocalUser.findOne({ email })
        if (existing) {
            return NextResponse.json({ message: 'E-mail já registrado' }, { status: 409 })
        }

        const hashedPassword = await bcrypt.hash(password, 10)
        const newUser = await LocalUser.create({ name, email, password: hashedPassword })

        return NextResponse.json({ message: 'Usuário criado com sucesso', userId: newUser._id })
    } catch (error) {
        console.error('Erro ao registrar:', error)
        return NextResponse.json({ message: 'Erro interno do servidor' }, { status: 500 })
    }
}
