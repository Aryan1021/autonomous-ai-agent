from agent.config import settings

print("Model:", settings.MODEL_NAME)
print("API Key Loaded:", bool(settings.GEMINI_API_KEY))