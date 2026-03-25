# Voice LLM — Qwen3-0.6B

Language model for the voice AI pipeline. Uses [Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF) in GGUF format via [llama.cpp](https://github.com/ggml-org/llama.cpp) for fast CPU inference.

## Model Details

| Property | Value |
|----------|-------|
| Base model | Qwen3-0.6B |
| Quantization | Q4_K_M |
| Size | ~400MB |
| Context | 4096 tokens |
| First token | <300ms (CPU) |
| Architecture | Dense transformer |

## KitOps Usage

```bash
# Pack (includes model, code, AND the system prompt)
kit pack . -t jozu.ml/voice-ai/voice-llm:v1.0.0

# Unpack just the prompt (for iteration)
kit unpack jozu.ml/voice-ai/voice-llm:v1.0.0 --filter=prompts -d ./output
```

## System Prompt

The call centre agent persona is defined in `prompts/system_prompt.md`. This file is packaged inside the ModelKit, so prompt changes are versioned alongside the model weights.

## Local Usage

```python
from src.llm_service import LLMService

llm = LLMService()
reply = llm.generate("Hi, I have a question about my bill.")
```
