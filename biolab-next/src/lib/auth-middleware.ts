import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

interface AuthenticatedRequest extends NextRequest {
    nextauth: {
        token: {
            role?: "admin" | "user";
        };
    };
}

export const authMiddleware = withAuth(
    async function middleware(req: NextRequest) {
        const authReq = req as AuthenticatedRequest;

        const token = authReq.nextauth.token;
        const isAdminRoute = req.nextUrl.pathname.startsWith("/admin");

        if (isAdminRoute && token?.role !== "admin") {
            return NextResponse.redirect(new URL("/", req.url));
        }

        return NextResponse.next();
    },
    {
        callbacks: {
            authorized: ({ token }) => !!token,
        },
        pages: {
            signIn: "/login",
        },
    }
);
