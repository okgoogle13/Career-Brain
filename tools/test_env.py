import os
import sys
val = os.environ.get("GEMINI_API_KEY", "NOT_SET")
print("Length:", len(val))
print("Starts with op:// ?", val.startswith("op://"))
print("Value:", val[:10] + "..." if len(val) > 10 else val)
