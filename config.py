from dotenv import load_dotenv
load_dotenv()

import os
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")