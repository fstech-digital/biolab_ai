import { Schema, model, models } from "mongoose";

const LocalUserSchema = new Schema(
    {
        name: String,
        email: { type: String, unique: true },
        password: String,
        role: {
            type: String,
            enum: ["user", "admin"],
            default: "user",
        },
    },
    { timestamps: true }
);

export default models.LocalUser || model("LocalUser", LocalUserSchema);
