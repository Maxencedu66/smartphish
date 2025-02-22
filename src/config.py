# Configuration (API keys, DB, etc.)

import os

class Config:
    GOPHISH_API_URL = os.getenv("GOPHISH_API_URL", "https://localhost:3333")
    GOPHISH_API_KEY = "d9e065112905c9b7b4446db1fce6183a0b087e05badaf327850d70a64d18f722"  # Remplace par ta clé API GoPhish

    #DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://user:password@localhost/smartphish")
