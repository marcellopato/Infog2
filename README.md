# Lu Estilo API

API de gerenciamento de vendas para a loja Lu Estilo, desenvolvida com FastAPI e PostgreSQL.

## 🚀 Tecnologias

- Python 3.9+
- FastAPI
- PostgreSQL 13
- Docker & Docker Compose
- WhatsApp Business API

## 📋 Pré-requisitos

- Docker Desktop (Windows/Mac) ou Docker Engine + Compose (Linux)
- Git
- Editor de código (VS Code recomendado)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/marcellopato/Infog2.git
cd Infog2
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

3. Inicie os containers:
```bash
docker-compose up -d
```

4. Execute as migrações:
```bash
docker-compose exec web alembic upgrade head
```

5. Crie um usuário admin:
```bash
docker-compose exec web python scripts/create_admin.py
```

## 📦 Estrutura do Projeto

```
lu-estilo-api/
├── app/
│   ├── core/         # Configurações e funcionalidades core
│   ├── models/       # Modelos SQLAlchemy
│   ├── routers/      # Rotas da API
│   ├── schemas/      # Schemas Pydantic
│   └── services/     # Serviços (WhatsApp, etc)
├── tests/            # Testes unitários
├── alembic/          # Migrações do banco
└── docker/           # Arquivos Docker
```

## 🔑 Autenticação

A API usa autenticação JWT. Para obter um token:

```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=sua-senha"
```

## 📱 Integração WhatsApp

Para usar a integração com WhatsApp:

1. Crie uma conta no Meta Business
2. Configure o WhatsApp Business API
3. Atualize as variáveis no .env:
```
WHATSAPP_API_URL=
WHATSAPP_TOKEN=
WHATSAPP_PHONE_ID=
```

## 🧪 Testes

Execute os testes com:

```bash
docker-compose exec web pytest -v
```

Para ver a cobertura:

```bash
docker-compose exec web pytest --cov
```

## 📚 Documentação

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🛠️ Desenvolvimento

Para desenvolvimento local:

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure pre-commit:
```bash
pre-commit install
```

3. Rode os testes antes de cada commit:
```bash
pytest
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ✨ Funcionalidades

- Gestão de produtos e categorias
- Controle de pedidos
- Sistema de busca avançado
- Relatórios e métricas
- Integração com WhatsApp
- Autenticação e autorização
- Documentação completa
- Testes automatizados (95%+ cobertura)

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request
