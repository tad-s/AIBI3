import os
from dotenv import load_dotenv

# Load environment variables from the root .env file
# Assuming .env is in the parent directory of backend/
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    @classmethod
    def is_weather_api_configured(cls):
        return bool(cls.OPENWEATHER_API_KEY)

    @classmethod
    def is_maps_api_configured(cls):
        return bool(cls.GOOGLE_MAPS_API_KEY)
