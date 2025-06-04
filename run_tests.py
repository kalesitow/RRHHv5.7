import subprocess
import sys
import os

def run_tests():
    """Ejecuta todas las pruebas con diferentes configuraciones"""
    
    print("=" * 60)
    print("EJECUTANDO PRUEBAS DEL SISTEMA DE RRHH")
    print("=" * 60)
    
    # Pruebas básicas con coverage
    print("\n1. Ejecutando pruebas unitarias...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "test_sistema_rrhh.py::TestEmpleado",
        "test_sistema_rrhh.py::TestNomina", 
        "-v", "--cov=sistema_rrhh"
    ])
    
    if result.returncode != 0:
        print("❌ Fallos en pruebas unitarias")
        return False
    
    # Pruebas de integración
    print("\n2. Ejecutando pruebas de integración...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "test_sistema_rrhh.py::TestSistemaRRHH",
        "test_sistema_rrhh.py::TestIntegracion",
        "-v"
    ])
    
    if result.returncode != 0:
        print("❌ Fallos en pruebas de integración")
        return False
    
    # Reporte completo
    print("\n3. Generando reporte completo...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "test_sistema_rrhh.py",
        "--cov=sistema_rrhh",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=60"
    ])
    
    if result.returncode == 0:
        print("\n✅ Todas las pruebas pasaron exitosamente!")
        return True
    else:
        print("\n❌ Algunas pruebas fallaron o coverage insuficiente")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)