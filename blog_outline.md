---

## 📝 Blog Outline: "Multi-Model Voice AI Pipeline with KitOps and Jozu Hub"

---

**Intro — The Problem Nobody Talks About**
- Voice AI is having a moment, but everyone focuses on the models, not the ops
- When you have 3 models (STT + LLM + TTS) updating on different schedules — things get messy fast
- What happens when the wrong model version hits production on a live call centre?

---

**Section 1 — What We're Building**
- High level: a self-hosted call centre voice agent
- The 3-stage pipeline: caller speaks → AI understands → AI responds
- Quick architecture diagram (phone → STT → LLM → TTS → phone)
- Why open source? Control, cost, and no vendor lock-in

---

**Section 2 — Picking the Right Open Models**
- STT: why Faster-Whisper hits the sweet spot for telephony
- LLM: why a MoE model like Qwen3 makes sense for real-time (only 3B params active)
- TTS: why Kokoro at 82M params sounds better than models 10x its size
- Latency breakdown — how you actually get under 500ms

---

**Section 3 — Packaging Models with KitOps**
- What is a ModelKit and why it's like a Dockerfile for AI
- Walking through a real Kitfile (weights + prompts + configs + test data, all in one)
- `kit pack` → `kit push` — that's it
- The selective unpack trick: devs get code, ops get weights, nobody gets everything they don't need

---

**Section 4 — Jozu Hub as the Model Registry**
- Why a generic container registry isn't enough for AI models
- What Jozu Hub adds: version diffs, security scanning, signed artifacts
- The champion/challenger pattern for safe model updates
- Rollback in one command

---

**Section 5 — Wiring Up the Telephony Layer**
- Jambonz for SIP → WebSocket bridging (open source, self-hosted)
- Pipecat for pipeline orchestration
- How the three models stream in parallel (not sequentially)

---

**Closing — Why This Matters Beyond the Demo**
- The real win isn't the voice AI — it's having a repeatable, auditable way to ship and update models
- This pattern works for any multi-model pipeline, not just voice
- What we'd build next: fine-tuning on domain data, A/B testing challenger models, scaling to concurrent calls

---

target WC :  **2,0000–2,500 words** 