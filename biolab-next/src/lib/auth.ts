import { AuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import GoogleProvider from 'next-auth/providers/google'
// import MicrosoftProvider from 'next-auth/providers/microsoft'
import { MongoDBAdapter } from '@auth/mongodb-adapter'
import clientPromise from './mongodb'
import LocalUser from '@/models/LocalUser'
import bcrypt from 'bcryptjs'

export const authOptions: AuthOptions = {
    adapter: MongoDBAdapter(clientPromise),
    session: {
        strategy: 'jwt',
    },
    providers: [
        // Login manual (email/senha)
        CredentialsProvider({
            name: 'credentials',
            credentials: {
                email: { label: 'Email', type: 'text' },
                password: { label: 'Senha', type: 'password' },
            },
            async authorize(credentials) {
                if (!credentials?.email || !credentials?.password) return null
                const user = await LocalUser.findOne({ email: credentials.email })
                if (!user) return null
                const isValid = await bcrypt.compare(credentials.password, user.password)
                if (!isValid) return null
                return { id: user._id.toString(), name: user.name, email: user.email }
            },
        }),

        // Login com Google
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        }),

        // Login com Microsoft (Outlook, Hotmail, etc)
        // MicrosoftProvider({
        //     clientId: process.env.MICROSOFT_CLIENT_ID!,
        //     clientSecret: process.env.MICROSOFT_CLIENT_SECRET!,
        // }),
    ],
    pages: {
        signIn: '/login',
    },
    secret: process.env.NEXTAUTH_SECRET,
}
