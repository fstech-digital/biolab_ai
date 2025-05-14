import { withAuth } from "next-auth/middleware";

export const authMiddleware = withAuth({
    pages: {
        signIn: "/login",
    },
});
