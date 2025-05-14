import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/biolab';

if (!MONGODB_URI) {
    throw new Error('A variável de ambiente MONGODB_URI não está definida.');
}

let cached = (global as any).mongoose || { conn: null, promise: null };

export async function dbConnect() {
    if (cached.conn) return cached.conn;

    if (!cached.promise) {
        cached.promise = mongoose.connect(MONGODB_URI, {
            bufferCommands: false,
        });
    }

    cached.conn = await cached.promise;
    return cached.conn;
}
