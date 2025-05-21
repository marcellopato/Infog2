from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import auth, products
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar tabelas
Base.metadata.create_all(bind=engine)

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

# Registrar rotas
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(products.router, prefix="/products", tags=["products"])

# Rota de teste
@app.get("/")
async def root():
    logger.info("Acessando rota raiz")
    return {"message": "Lu Estilo API está funcionando!"}

@app.get("/health")
async def health_check():
    logger.info("Verificando saúde da API")
    return {"status": "ok"}
