# Lu Estilo API

API RESTful para gerenciamento de vendas da Lu Estilo, desenvolvida com FastAPI.

## 🚀 Funcionalidades

- Autenticação e autorização com JWT
- Gerenciamento de clientes
- Catálogo de produtos
- Sistema de pedidos
- Integração com WhatsApp
- Documentação automática (Swagger)

## 🔧 Tecnologias

- Python 3.9+
- FastAPI
- PostgreSQL
- Docker
- Pytest
- Alembic (Migrações)
- Sentry (Monitoramento)

## 📋 Pré-requisitos

- Docker e Docker Compose
- Python 3.9+ (para desenvolvimento local)
- Git

## ⚙️ Instalação e Execução

1. Clone o repositório:
```bash
git clone https://github.com/marcellopato/Infog2
cd Infog2
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Execute com Docker:
```bash
docker-compose up --build
```

4. Acesse:
- API: http://localhost:8000
- Documentação: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔍 Estrutura do Projeto

```
lu-estilo-api/
├── app/
│   ├── core/           # Configurações principais
│   ├── models/         # Modelos SQLAlchemy
│   ├── schemas/        # Schemas Pydantic
│   ├── routers/        # Endpoints da API
│   ├── services/       # Lógica de negócios
│   └── utils/          # Utilitários
├── tests/              # Testes
├── alembic/            # Migrações
├── docker/             # Configurações Docker
└── docs/              # Documentação adicional
```

## 🧪 Testes

Execute os testes usando:

```bash
docker-compose exec web pytest
```

## 📚 Documentação da API

A documentação completa está disponível em:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Autenticação

A API utiliza JWT (JSON Web Token) para autenticação. Para acessar endpoints protegidos:

1. Faça login em `/auth/login`
2. Use o token retornado no header `Authorization: Bearer {token}`

## 👥 Níveis de Acesso

- **Admin**: Acesso total ao sistema
- **Usuário**: Acesso limitado a operações básicas

## 📦 Deploy

O projeto está configurado para deploy usando Docker. Consulte `docker-compose.yml` para mais detalhes.

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para suporte, envie um email para suporte@luestilo.com.br
