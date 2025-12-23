import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

CHROMA_DIR = Path(os.getenv("CHROMA_PERSIST_PATH"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")

# Helper to get env vars
def require_env(name: str):
    val = os.getenv(name)
    if not val:
        raise EnvironmentError(f"Required env var {name} not set")
    return val

if not GROQ_API_KEY:
    # don't raise here; allow local testing without Groq but warn
    print("[WARN] GROQ_API_KEY not set. Groq calls will fail until you set it.")