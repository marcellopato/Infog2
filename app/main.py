from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(
    title="Lu Estilo API",
    description="API para gerenciamento de vendas da Lu Estilo",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Lu Estilo API está funcionando!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
