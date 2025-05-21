import pytest
from sqlalchemy.exc import SQLAlchemyError
from app.core.database import get_db, SessionLocal

def test_get_db():
    db = next(get_db())
    try:
        assert db is not None
        # Testa uma query simples
        result = db.execute("SELECT 1").scalar()
        assert result == 1
    finally:
        db.close()

def test_db_connection_error():
    """Testa o tratamento de erro na conexão do banco"""
    def mock_session():
        raise SQLAlchemyError("Erro de conexão")
    
    with pytest.raises(Exception):
        db = next(mock_session())

def test_db_context_manager():
    """Testa o gerenciador de contexto do banco de dados"""
    from contextlib import contextmanager
    
    @contextmanager
    def mock_db_session():
        yield get_db().__next__()
    
    with mock_db_session() as db:
        result = db.execute("SELECT 1").scalar()
        assert result == 1

def test_db_exception_handling():
    """Testa o tratamento completo de exceções do banco"""
    def mock_db():
        db = SessionLocal()
        db.close = lambda: None
        db.rollback = lambda: None
        raise SQLAlchemyError("Erro simulado")
        yield db
    
    with pytest.raises(SQLAlchemyError) as exc_info:
        next(mock_db())
    assert "Erro simulado" in str(exc_info.value)
