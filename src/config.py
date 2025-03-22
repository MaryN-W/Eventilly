from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    print("Loading Config...")

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    print(" Config Loaded 1...2...3")
Config = Settings()  
