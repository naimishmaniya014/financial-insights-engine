"""
summarizer.py
Simple helper to run one-off summaries using your configured provider.
"""

from typing import Optional, Dict, Any
from pathlib import Path
import yaml

# import the provider(s)
from fin_summarizer.providers.stub_provider import StubProvider
try:
    from fin_summarizer.providers.openai_provider import OpenAIProvider
except ImportError:
    OpenAIProvider = None


class Summarizer:
    def __init__(self, provider: str = "stub", model: Optional[str] = None):
        """
        provider: "stub" or "openai"
        model: optional model name for OpenAIProvider
        """
        if provider == "stub":
            self.provider = StubProvider()
        elif provider == "openai":
            if OpenAIProvider is None:
                raise RuntimeError("OpenAI provider not implemented yet.")
            self.provider = OpenAIProvider(model=model or "gpt-4o-mini")
        else:
            raise ValueError(f"Unknown provider: {provider}")

        self._load_prompts()

    def _load_prompts(self):
        prompts_path = Path(__file__).resolve().parents[1] / "data" / "prompts.yaml"
        if prompts_path.exists():
            data = yaml.safe_load(prompts_path.read_text())
            self.prompts = [p["template"] for p in data.get("prompts", [])]
        else:
            self.prompts = []

    def summarize(self, context: str, prompt_index: int = 0, **kwargs) -> Dict[str, Any]:
        """
        Summarize a context using one of the stored prompt templates.
        Returns a dict with 'text', 'latency_ms', and optionally 'raw'.
        """
        if not self.prompts:
            raise RuntimeError("No prompts loaded. Check data/prompts.yaml.")
        template = self.prompts[prompt_index]
        return self.provider.summarize(template, context, **kwargs)


if __name__ == "__main__":
    # quick manual test
    context = (
        "Company A reported Q2 revenue growth of 12% y/y driven by subscription gains. "
        "Gross margin expanded 180 bps to 64%. Operating expenses rose 8% due to R&D hiring. "
        "Guidance raised: FY revenue +10-12% with margin discipline. "
        "Risks include churn in SMB segment and FX headwinds in EMEA."
    )
    s = Summarizer(provider="stub")
    result = s.summarize(context)
    print("Summary:", result["text"])
    print("Latency (ms):", result["latency_ms"])
