"""Qwen3 LLM Service for the voice AI pipeline.

Handles conversational response generation with streaming,
maintaining conversation history for multi-turn calls.
"""

import yaml
from pathlib import Path
from llama_cpp import Llama


class LLMService:
    """LLM service using llama.cpp for GGUF model inference."""

    def __init__(self, model_path: str = None, config_path: str = None):
        config, config_dir = self._load_config(config_path)
        model_path = model_path or config.get("model_path")
        if not model_path:
            raise ValueError(
                "LLM model_path must be set in config.yaml or passed directly"
            )
        # Resolve model_path relative to config file directory
        if not Path(model_path).is_absolute():
            model_path = str((config_dir / model_path).resolve())

        prompt_path = config.get(
            "system_prompt_path",
            str(Path(__file__).parent.parent / "prompts" / "system_prompt.md"),
        )
        if not Path(prompt_path).is_absolute():
            prompt_path = str((config_dir / prompt_path).resolve())

        self.llm = Llama(
            model_path=model_path,
            n_ctx=config.get("context_length", 4096),
            n_threads=config.get("n_threads", 4),
            verbose=False,
        )
        self.system_prompt = self._load_prompt(prompt_path)
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 0.9)
        self.max_tokens = config.get("max_tokens", 256)
        self.conversation_history = []

    def _load_config(self, config_path: str = None) -> tuple[dict, Path]:
        path = Path(config_path or Path(__file__).parent.parent / "config.yaml")
        if path.exists():
            with open(path) as f:
                return yaml.safe_load(f) or {}, path.parent
        return {}, Path(__file__).parent.parent

    def _load_prompt(self, prompt_path: str) -> str:
        path = Path(prompt_path)
        if path.exists():
            return path.read_text().strip()
        return "You are a helpful call centre agent."

    def generate(self, user_message: str) -> str:
        """Generate a complete response to the user message."""
        self.conversation_history.append({"role": "user", "content": user_message})

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history[-10:],  # Keep last 10 turns for context
        ]

        response = self.llm.create_chat_completion(
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
        )

        reply = response["choices"][0]["message"]["content"]
        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def generate_stream(self, user_message: str):
        """Stream response tokens as they're generated.

        Yields individual tokens, allowing the TTS to start
        synthesizing before the full response is ready.
        """
        self.conversation_history.append({"role": "user", "content": user_message})

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history[-10:],
        ]

        full_reply = []
        try:
            stream = self.llm.create_chat_completion(
                messages=messages,
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                stream=True,
            )

            for chunk in stream:
                delta = chunk["choices"][0].get("delta", {})
                token = delta.get("content", "")
                if token:
                    full_reply.append(token)
                    yield token
        except Exception:
            # Remove the orphaned user message on stream failure
            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()
            raise

        self.conversation_history.append(
            {"role": "assistant", "content": "".join(full_reply)}
        )

    def reset_conversation(self):
        """Clear conversation history — call this when a new caller connects."""
        self.conversation_history = []
