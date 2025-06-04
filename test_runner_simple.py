import os
import sys

# Agregar el directorio actual al path para importar el módulo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import pytest
    
    # Ejecutar pruebas con configuración básica
    exit_code = pytest.main([
        "test_sistema_rrhh.py",
        "-v",
        "--tb=short"
    ])
    
    sys.exit(exit_code)