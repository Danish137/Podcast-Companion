# Submission Checklist

## Assignment Requirements

| Requirement | Repository File/Artifact | How Evaluator Runs It | Status |
| :--- | :--- | :--- | :--- |
| **1. Runnable source code** | `src/`, `frontend/` | `uvicorn src.api:app --port 8000` (backend) and `npm run dev` in `frontend/`. | ✅ Complete |
| **2. Short README** | `README.md` | Read standard Markdown file. Contains setup and run commands. | ✅ Complete |
| **3. Short Product Note** | `PRODUCT.md` | Read standard Markdown file. Defines the learner user, the problem, and the conversation-first design choice. | ✅ Complete |
| **4. Artifact Reproducibility** | `data/` | Artifacts (chunks, indexes, transcripts) are checked in. Can be regenerated via `python -m src.transcribe`, `src.metadata`, `src.chunker`, then `python -m src.retrieval build`. | ✅ Complete |
| **5. Evaluation System** | `src/evaluate.py`, `eval/` | `python -m src.evaluate --name final_evaluation` runs the automated programmatic suite. | ✅ Complete |
| **6. EVAL.md** | `EVAL.md` | Read standard Markdown file. Details criteria, sets, methodology, baseline vs improved, manual QA failures, and fix. | ✅ Complete |

## Assignment Constraints

| Constraint | Status | Details |
| :--- | :--- | :--- |
| **Starts from supplied raw audio** | ✅ Complete | Pipeline sends the supplied raw audio (split with ffmpeg) to Gemini 2.5 Flash for timestamped transcription into `data/transcripts`. |
| **No YouTube/closed captions** | ✅ Complete | Does not use external APIs for transcripts. Ground truth is purely derived from supplied audio files. |
| **Source-grounded responses** | ✅ Complete | System abstains if evidence is missing (`UNSUPPORTED`). Citations and chunks are provided. |
| **Timestamp/audio verification** | ✅ Complete | Frontend plays audio at the exact timestamp cited in the LLM response. |
| **Conversational interaction** | ✅ Complete | Follow-ups and pronouns (e.g. "what pattern did he notice?") are resolved against conversational state. |

## GitHub Readiness

| Check | Status | Details |
| :--- | :--- | :--- |
| **No Secrets in Repo** | ✅ Complete | Verified no API keys exist in source code or `.env.example`. |
| **Clean `.gitignore`** | ✅ Complete | Ignores `.env`, `node_modules`, `__pycache__`, `.venv`. Required JSON artifacts are preserved. |
| **Dependencies Documented** | ✅ Complete | `requirements.txt` and `package.json` accurately reflect the environment. |
