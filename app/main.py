from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import auth, products, categories, orders, reports, search
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

# Configurar CORS
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
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(search.router, prefix="/search", tags=["search"])

# Rota de teste
@app.get("/")
async def root():
    logger.info("Acessando rota raiz")
    return {"message": "Lu Estilo API está funcionando!"}

@app.get("/health")
async def health_check():
    logger.info("Verificando saúde da API")
    return {"status": "ok"}
