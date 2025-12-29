import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from imports import *
from main.prometheus.app.generation import executeWorkflow

APIKey_Header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verifyAPIKey(APIKey: str = Depends(APIKey_Header)):
    if Config.PROMETHEUS['KEY.SYSTEM'] == 'FALSE':
        return None
    
    validKey = Config.PROMETHEUS['KEY']
    if not validKey:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    if APIKey is None or APIKey != validKey:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    return APIKey

class API:
    def __init__(self, service_name: str, port: int):
        self.service_name = service_name
        self.port = int(port)
        self.app = FastAPI(title=service_name, version="1.0.0")
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.setupRoutes()
    
    def setupRoutes(self):
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "service": self.service_name,
                "port": self.port,
                "timestamp": str(time.time())
            }
        
        @self.app.get("/")
        async def root():
            return {"message": "Prometheus API"}
        
        @self.app.get("/rag/key")
        async def APIKeyTest(api_key: str = Depends(verifyAPIKey)):
            return {"message": "API", "secured": True}
        
        @self.app.get("/rag")
        async def rag(text: str, api_key: str = Depends(verifyAPIKey)):
            try:
                response = executeWorkflow(text)
                
                return {
                    "success": True,
                    "response": response,
                    "timestamp": str(time.time())
                }
            except Exception as e:
                import traceback
                traceback.print_exc()
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": str(time.time())
                }

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="critical")