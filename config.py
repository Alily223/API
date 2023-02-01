import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "1123435534342345654AEWA"