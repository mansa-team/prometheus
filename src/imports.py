import os
import time
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

class Config:
    MYSQL = {
        'USER': os.getenv('MYSQL_USER'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD'),
        'HOST': os.getenv('MYSQL_HOST'),
        'DATABASE': os.getenv('MYSQL_DATABASE'),
    }
    
    STOCKS_API = {
        'ENABLED': os.getenv('STOCKSAPI_ENABLED'),
        'HOST': os.getenv('STOCKSAPI_HOST'),
        'PORT': os.getenv('STOCKSAPI_PORT'),
        'KEY.SYSTEM': os.getenv('STOCKSAPI_KEY.SYSTEM'),
        'KEY': os.getenv('STOCKSAPI_PRIVATE.KEY'),
    }

    PROMETHEUS = {
        'GEMINI_API.KEY': os.getenv('GEMINI_API.KEY'),
    }