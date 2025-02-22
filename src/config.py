# Configuration (API keys, DB, etc.)

import os

class Config:
    GOPHISH_API_URL = os.getenv("GOPHISH_API_URL", "http://localhost:3333")
    GOPHISH_API_KEY = "TA_CLE_API"  # Remplace par ta clé API GoPhish

    DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://user:password@localhost/smartphish")
