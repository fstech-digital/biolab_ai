import { Schema, model, models } from 'mongoose';

const VariationCauseSchema = new Schema({
    parameter: String,
    condition: { type: String, enum: ['aumento', 'queda'] },
    deltaMin: Number,
    deltaMax: Number,
    causes: [String],
});

export default models.VariationCause || model('VariationCause', VariationCauseSchema);