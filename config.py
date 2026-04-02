import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
CHROMA_DIR = PROJECT_ROOT / "chroma_db"

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200
MIN_CHUNK_SIZE = 100

# Retrieval
TOP_K = 15

# ── LLM Provider Configuration (Multi-Provider Fallback) ──
# Priority: Groq (fastest) → Gemini (highest token limits) → Cerebras (fast + generous)

# Provider 1: Groq (Primary — fastest inference ~1-3s)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Provider 2: Google Gemini (Fallback — highest free-tier token limits)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Provider 3: Cerebras (Fallback — fast wafer-scale inference)
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
CEREBRAS_MODEL = "llama-3.3-70b"
CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1"

# ChromaDB collection name
COLLECTION_NAME = "iic_knowledge_base"

# Category display names
CATEGORY_NAMES = {
    "01_IIC_MIC_National": "IIC National Framework",
    "02_SINE_Incubation": "SINE Incubation",
    "03_ASPIRE_Research_Park": "ASPIRE Research Park",
    "04_DSSE_Entrepreneurship": "DSSE Courses & Programs",
    "05_IPR_Patents_IRCC": "IP & Patents (IRCC)",
    "06_Startup_Policy": "Startup Policy",
    "07_ECell_Entrepreneurship": "E-Cell & Eureka",
    "08_Tinkerers_Lab_MakerSpace": "Labs & MakerSpace",
    "09_Techfest": "Techfest",
    "10_TIH_SemiX": "TIH & SemiX",
    "11_Annual_Reports": "Annual Reports",
    "12_Govt_Schemes_SIH_NIDHI_BIRAC": "Government Funding Schemes",
    "13_NCETIS": "NCETIS Defence Tech",
    "14_IoE_Funding": "IoE Funding",
    "15_Insight_IITB_Articles": "Insight IIT Bombay",
    "16_IITB_Main_Site": "IIT Bombay Official",
    "17_Additional_Govt_Schemes": "Additional Govt Schemes",
    "18_IITB_Professors": "IIT Bombay Faculty & Professors",
    "19_IITB_Courses": "IIT Bombay Course Catalog",
}
