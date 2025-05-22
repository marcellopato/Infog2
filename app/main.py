from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.routers import auth, products, categories, orders, reports, search, whatsapp
import logging

# Configurar logging mais detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lu Estilo API",
    description="""
    API para gerenciamento de vendas da Lu Estilo.
    
    ## Funcionalidades
    
    * Autenticação de usuários
    * Gerenciamento de produtos e categorias
    * Controle de pedidos
    * Relatórios e métricas
    * Busca avançada
    * Integração com WhatsApp Business API
    
    ## Integrações
    
    ### WhatsApp Business
    A API se integra com WhatsApp Business para:
    * Envio automático de confirmação de pedidos
    * Notificações de status do pedido
    * Catálogo de produtos
    * Atendimento ao cliente
    
    ## Requisitos Técnicos
    
    * Python 3.9+
    * PostgreSQL 13+
    * Docker e Docker Compose
    
    ## Como Usar
    
    1. Autentique-se usando `/auth/login`
    2. Use o token JWT retornado nos headers das requisições
    3. Explore os endpoints através desta documentação
    
    ## Suporte
    
    Para suporte técnico, contate:
    * Email: suporte@luestilo.com.br
    * WhatsApp: (XX) XXXXX-XXXX
    """,
    version="1.0.0",
    contact={
        "name": "Suporte Lu Estilo",
        "email": "suporte@luestilo.com.br"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
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
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])

# Adicionar log para debug
logger.info("Rotas registradas:")
for route in app.routes:
    logger.info(f"- {route.path}")

@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando aplicação...")
    try:
        # Testar conexão com banco
        Base.metadata.create_all(bind=engine)
        logger.info("Conexão com banco estabelecida")
    except Exception as e:
        logger.error(f"Erro ao iniciar: {str(e)}")
        raise e

# Rota de teste
@app.get("/")
async def root():
    logger.info("Acessando rota raiz")
    return {"message": "Lu Estilo API está funcionando!"}

@app.get("/health")
async def health_check():
    logger.info("Verificando saúde da API")
    return {"status": "ok"}
