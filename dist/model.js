// Open-source model layer, run fully inside the browser with Transformers.js (ONNX + WebAssembly).
// No API key, no server, and the text you paste never leaves your device.
// ---- Change these two lines to try a different open model ----
export const MODEL_ID = "Xenova/mobilebert-uncased-mnli";
export const MODEL_TASK = "zero-shot-classification";
// --------------------------------------------------------------
const TRANSFORMERS_URL = "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.0";
// Zero-shot labels: the model scores how well the message fits each description.
const SCAM_LABEL = "a banking scam or phishing attempt";
const SAFE_LABEL = "a genuine bank notification";
// Used only when MODEL_TASK is "text-classification" (a fine-tuned scam model).
// Check the model card for real label names and edit this pattern if needed.
const RISKY_LABEL_PATTERN = /phish|scam|spam|fraud|malicious/i;
let classifierPromise = null;
export function loadModel(onProgress) {
    if (!classifierPromise) {
        classifierPromise = (async () => {
            // Loaded from a URL at run time, so TypeScript treats it as untyped.
            const lib = await import(/* webpackIgnore: true */ TRANSFORMERS_URL);
            const files = {};
            return await lib.pipeline(MODEL_TASK, MODEL_ID, {
                progress_callback: (p) => {
                    if (p.status === "progress" && p.file) {
                        files[p.file] = p.progress ?? 0;
                        const values = Object.values(files);
                        const avg = values.reduce((a, b) => a + b, 0) / values.length;
                        onProgress(`Downloading open-source model… ${Math.round(avg)}% (first visit only)`);
                    }
                },
            });
        })();
        // If loading fails, allow a retry on the next call.
        classifierPromise.catch(() => { classifierPromise = null; });
    }
    return classifierPromise;
}
/** Returns the model's confidence (0 to 100) that the text is a scam. */
export async function scoreWithModel(text, onProgress) {
    const classify = await loadModel(onProgress);
    if (MODEL_TASK === "zero-shot-classification") {
        const out = await classify(text, [SCAM_LABEL, SAFE_LABEL]);
        const i = out.labels.indexOf(SCAM_LABEL);
        return Math.round(out.scores[i] * 100);
    }
    const raw = await classify(text, undefined);
    const items = Array.isArray(raw[0]) ? raw[0] : raw;
    const risky = items
        .filter((it) => RISKY_LABEL_PATTERN.test(it.label))
        .reduce((sum, it) => sum + it.score, 0);
    return Math.round(Math.min(1, risky) * 100);
}
