# Configuration (API keys, DB, etc.)

import os

class Config:
    GOPHISH_API_URL = "http://127.0.0.1:3333/api"
    GOPHISH_API_KEY = os.getenv("GOPHISH_API_KEY", "TA_CLE_API")
    DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://user:password@localhost/smartphish")
