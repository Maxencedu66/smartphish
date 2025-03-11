# Configuration (API keys, DB, etc.)

import os

class Config:
    GOPHISH_API_URL = os.getenv("GOPHISH_API_URL", "https://localhost:3333")
    GOPHISH_API_KEY = "262b24728ee5ae90ac1e10df898cb07292efc6b00feea4c28f222cb2f09921b0" # Pas oublier de la remplacer si on change de compte

    #DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://user:password@localhost/smartphish")
