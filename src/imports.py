import os
import time
import requests
import json
import threading
from typing import Optional, Dict, Any

from datetime import datetime, timedelta
from dotenv import load_dotenv

import requests
import pandas as pd
import numpy as np

from sqlalchemy import create_engine, text
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

load_dotenv()

LOCALHOST_ADDRESSES = ['localhost', '127.0.0.1', '0.0.0.0', 'None', None]

class Config:
    MYSQL = {
        'USER': os.getenv('MYSQL_USER'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD'),
        'HOST': os.getenv('MYSQL_HOST'),
        'DATABASE': os.getenv('MYSQL_DATABASE'),
    }
    
    STOCKS_API = {
        'HOST': os.getenv('STOCKSAPI_HOST'),
        'PORT': os.getenv('STOCKSAPI_PORT'),

        'KEY': os.getenv('STOCKSAPI_PRIVATE.KEY'),
    }

    PROMETHEUS = {
        'ENABLED': os.getenv('PROMETHEUS_ENABLED'),

        'HOST': os.getenv('PROMETHEUS_HOST'),
        'PORT': os.getenv('PROMETHEUS_PORT'),

        'KEY.SYSTEM': os.getenv('PROMETHEUS_KEY.SYSTEM'),
        'KEY': os.getenv('PROMETHEUS_PRIVATE.KEY'),

        'LOCAL.AI': os.getenv('PROMETHEUS_LOCAL.AI'),
        'MODEL.NAME': os.getenv('PROMETHEUS_MODEL.NAME'),
        'MODEL.DEVICE': os.getenv('PROMETHEUS_MODEL.DEVICE'),
        'GEMINI_API.KEY': os.getenv('GEMINI_API.KEY'),
    }