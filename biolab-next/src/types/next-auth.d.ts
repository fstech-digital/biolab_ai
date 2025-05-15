import NextAuth, { DefaultSession, DefaultUser } from "next-auth";

declare module "next-auth" {
    interface Session {
        user: {
            id?: string;
            name?: string | null;
            email?: string | null;
            image?: string | null;
            role?: "admin" | "user";
        } & DefaultSession["user"];
    }

    interface User extends DefaultUser {
        role?: "admin" | "user";
    }
}
