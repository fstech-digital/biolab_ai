import { model, models, Schema } from "mongoose";

const UserSchema = new Schema({
    name: String,
    email: String,
}, { timestamps: true });

export default models.User || model('User', UserSchema);