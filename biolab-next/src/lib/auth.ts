import { AuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import GoogleProvider from 'next-auth/providers/google'
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
                return { id: user._id.toString(), name: user.name, email: user.email, role: user.role }
            },
        }),

        // Login com Google
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        }),


    ],
    pages: {
        signIn: '/login',
    },
    callbacks: {
        async jwt({ token, user }) {
            if (user && "role" in user) {
                token.role = (user as any).role;
            }
            return token;
        },
        async session({ session, token }) {
            if (token && session.user) {
                session.user.role = token.role as "admin" | "user";
            }
            return session;
        },
        async redirect({ url, baseUrl }) {
            return baseUrl;
        },
    },



    secret: process.env.NEXTAUTH_SECRET,
}
