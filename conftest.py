import pytest
import tempfile
import os

@pytest.fixture(scope="session")
def temp_db_file():
    """Crea un archivo temporal para las pruebas que requieren persistencia"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    yield temp_file
    
    # Limpiar después de las pruebas
    if os.path.exists(temp_file):
        os.unlink(temp_file)

@pytest.fixture
def empleado_ejemplo():
    """Empleado de ejemplo para las pruebas"""
    from sistema_rrhh import Empleado
    return Empleado("12345678", "Juan", "Pérez", "Desarrollador", 
                   3000000, "indefinido", "300-123-4567", "juan@empresa.com", 8)
