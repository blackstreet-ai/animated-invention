# AI Video Essay Pipeline (Google ADK Scaffold)

> _“Automate the storyteller.”_

This project is a **learning-focused, multi-agent system** that converts a topic idea into a finished video essay using Google’s **Agent Development Kit (ADK)**.

Pipeline highlights:
* **TopicGenerationAgent** – optional orchestrator that discovers & scores fresh video-essay topics (idea-discovery mode).
* Core production agents – Research, Scriptwriter, Visual, Audio, Editor, Quality-Control.
* ADK-style `WorkflowManager` with dependency graph, retries, and parallel layers.

The repo started as a stub scaffold but now contains *working orchestration logic* with extensible stubs you can gradually replace with real implementations.

---

## 1. Quick Start

```bash
# Install dependencies (ideally in a virtualenv)
python -m pip install -r requirements.txt

# Run the production pipeline (writes placeholder outputs for now)
python scripts/run_pipeline.py --topic "The Fermi Paradox"

# (Optional) Run *idea-discovery* mode – generates topic ideas first, then full pipeline
python scripts/run_pipeline.py --discover-topics --topic "The Fermi Paradox"
```

You should see log output showing each agent executing and a final JSON-like state.

---

## 2. Repository Structure

```
cc_pipeline_v1/
├── configs/          # YAML configuration files
│   └── default.yml
├── scripts/
│   └── run_pipeline.py
├── src/
│   └── video_pipeline/
│       ├── agents/   # Six stub agents (Research, Scriptwriter, ...)
│       ├── core/     # PipelineState + BaseAgent abstractions
│       └── workflows/manager.py
├── tests/            # Pytest suite (import sanity + smoke test)
├── .env.example      # API key placeholders
├── requirements.txt
└── README.md         # You are here
```

---

## 3. Extending the Scaffold

1. **Replace stubs with real logic** – e.g., have `ResearchAgent` call web search APIs or Wikipedia.
2. **Leverage ADK tools** – integrate LLMs (Gemini, etc.) via ADK-provided tool wrappers.
3. **Parallelism & advanced workflows** – swap the simple `WorkflowManager` for ADK’s graph orchestration primitives.
4. **Robust testing** – add unit tests for each agent, mock external calls, and use CI.

---

## 4. Environment Variables

Sensitive credentials (API keys, etc.) should **never** be committed.  Copy `.env.example` to `.env` and fill in values.  `python-dotenv` will load it automatically if present.

---

## 5. Documentation

* `docs/adk-docs.md` – local copy of Google ADK documentation
* Inline comments – every module follows the beginner-friendly commenting guidelines specified in `adk-agent-development-rules.md`.

---

## 6. License

MIT (see `LICENSE` – feel free to change).
