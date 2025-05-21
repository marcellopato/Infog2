from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

from app.routers import auth, clients, products, orders

app = FastAPI(
    title="Lu Estilo API",
    description="API para gerenciamento de vendas da Lu Estilo",
    version="1.0.0"
)

sentry_sdk.init(
    dsn="seu-dsn-do-sentry",
    traces_sample_rate=1.0,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(clients.router, prefix="/clients", tags=["clients"])
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])

@app.get("/")
async def root():
    return {"message": "Bem-vindo à API da Lu Estilo"}
