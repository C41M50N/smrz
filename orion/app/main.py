import sys

from dotenv import load_dotenv
from fastapi import FastAPI

sys.dont_write_bytecode = True  # Disable .pyc file generation
load_dotenv()  # Load environment variables from .env file

from app.routes import router  # noqa: E402

app = FastAPI(title="readr API", version="0.1.0")
app.include_router(router)
