import os
import sys

key = os.environ.get("GEMINI_API_KEY", "")
print(f"RAW REPR: {repr(key)}")
