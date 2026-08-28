import os

from dotenv import load_dotenv
from groq import Groq


# Search for .env in current directory, backend directory, and root directory
load_dotenv()
backend_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if os.path.exists(backend_env):
    load_dotenv(backend_env)
root_env = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
if os.path.exists(root_env):
    load_dotenv(root_env)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment or .env file")


client = Groq(api_key=api_key)