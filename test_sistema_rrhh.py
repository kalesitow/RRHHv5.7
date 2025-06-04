import pytest
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, mock_open
import sys

# Importar las clases del sistema (asumiendo que están en un archivo llamado sistema_rrhh.py)
from sistema_rrhh import Empleado, Nomina, SistemaRRHH

# Como el código está en el documento, lo copiamos aquí para las pruebas
# En un proyecto real, esto sería una importación normal

class TestEmpleado:
    """Pruebas para la clase Empleado"""
    
    def test_crear_empleado_basico(self):
        """Prueba la creación básica de un empleado"""
        empleado = Empleado("12345", "Juan", "Pérez", "Desarrollador", 3000000, "indefinido")
        
        assert empleado.cedula == "12345"
        assert empleado.nombre == "Juan"
        assert empleado.apellido == "Pérez"
        assert empleado.cargo == "Desarrollador"
        assert empleado.salario_base == 3000000
        assert empleado.tipo_contrato == "indefinido"
        assert empleado.activo == True
        assert empleado.valoracion == 5
        assert len(empleado.historial_nominas) == 0
        assert len(empleado.historial_valoraciones) == 1
    
    def test_crear_empleado_completo(self):
        """Prueba la creación de un empleado con todos los datos"""
        empleado = Empleado(
            "12345", "Juan", "Pérez", "Desarrollador", 3000000, "indefinido",
            "123-456-7890", "juan@email.com", 8
        )
        
        assert empleado.telefono == "123-456-7890"
        assert empleado.email == "juan@email.com"
        assert empleado.valoracion == 8
    
    def test_actualizar_valoracion_valida(self):
        """Prueba actualización de valoración con valor válido"""
        empleado = Empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        resultado = empleado.actualizar_valoracion(9)
        
        assert resultado == True
        assert empleado.valoracion == 9
        assert len(empleado.historial_valoraciones) == 2
    
    def test_actualizar_valoracion_invalida(self):
        """Prueba actualización de valoración con valor inválido"""
        empleado = Empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        resultado_alto = empleado.actualizar_valoracion(11)
        resultado_bajo = empleado.actualizar_valoracion(0)
        
        assert resultado_alto == False
        assert resultado_bajo == False
        assert empleado.valoracion == 5  # Valor original
        assert len(empleado.historial_valoraciones) == 1
    
    def test_agregar_nomina(self):
        """Prueba agregar nómina al historial"""
        empleado = Empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        nomina_data = {"periodo": "2024-01", "salario_neto": 2800000}
        
        empleado.agregar_nomina(nomina_data)
        
        assert len(empleado.historial_nominas) == 1
        assert empleado.historial_nominas[0] == nomina_data
    
    def test_desactivar_empleado(self):
        """Prueba desactivación de empleado"""
        empleado = Empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        empleado.desactivar()
        
        assert empleado.activo == False
    
    def test_activar_empleado(self):
        """Prueba reactivación de empleado"""
        empleado = Empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        empleado.desactivar()
        
        empleado.activar()
        
        assert empleado.activo == True
    
    def test_to_dict(self):
        """Prueba conversión a diccionario"""
        empleado = Empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        dict_empleado = empleado.to_dict()
        
        assert dict_empleado["cedula"] == "12345"
        assert dict_empleado["nombre"] == "Juan"
        assert dict_empleado["activo"] == True
        assert "historial_nominas" in dict_empleado
        assert "historial_valoraciones" in dict_empleado
    
    def test_from_dict(self):
        """Prueba creación desde diccionario"""
        data = {
            "cedula": "12345",
            "nombre": "Juan",
            "apellido": "Pérez",
            "cargo": "Dev",
            "salario_base": 3000000,
            "tipo_contrato": "indefinido",
            "telefono": "123-456",
            "email": "juan@email.com",
            "valoracion": 8,
            "activo": False,
            "historial_nominas": [{"periodo": "2024-01"}],
            "historial_valoraciones": [{"fecha": "2024-01-01", "valoracion": 8}]
        }
        
        empleado = Empleado.from_dict(data)
        
        assert empleado.cedula == "12345"
        assert empleado.activo == False
        assert len(empleado.historial_nominas) == 1
        assert len(empleado.historial_valoraciones) == 1
    
    def test_str_representation(self):
        """Prueba representación en string"""
        empleado = Empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        str_empleado = str(empleado)
        
        assert "Juan Pérez" in str_empleado
        assert "Dev" in str_empleado
        assert "Activo" in str_empleado


class TestNomina:
    """Pruebas para la clase Nomina"""
    
    @pytest.fixture
    def empleado_test(self):
        """Fixture que proporciona un empleado para las pruebas"""
        return Empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
    
    def test_crear_nomina_basica(self, empleado_test):
        """Prueba creación básica de nómina"""
        nomina = Nomina(empleado_test, "2024-01")
        
        assert nomina.empleado == empleado_test
        assert nomina.periodo == "2024-01"
        assert nomina.salario_base == 3000000
        assert nomina.horas_extra == 0
        assert nomina.bonificaciones == 0
        assert nomina.deducciones_adicionales == 0
        
        # Verificar cálculos básicos
        assert nomina.deduccion_salud == 3000000 * 0.04  # 4%
        assert nomina.deduccion_pension == 3000000 * 0.04  # 4%
        assert nomina.total_devengado == 3000000
        assert nomina.total_deducciones == (nomina.deduccion_salud + nomina.deduccion_pension)
        assert nomina.salario_neto == nomina.total_devengado - nomina.total_deducciones
    
    def test_agregar_horas_extra(self, empleado_test):
        """Prueba agregar horas extra"""
        nomina = Nomina(empleado_test, "2024-01")
        
        nomina.agregar_horas_extra(10, 25000)
        
        assert nomina.horas_extra == 10
        assert nomina.valor_hora_extra == 25000
        assert nomina.total_devengado == 3000000 + (10 * 25000)
    
    def test_agregar_bonificacion(self, empleado_test):
        """Prueba agregar bonificaciones"""
        nomina = Nomina(empleado_test, "2024-01")
        
        nomina.agregar_bonificacion(500000)
        
        assert nomina.bonificaciones == 500000
        assert nomina.total_devengado == 3000000 + 500000
        
        # Agregar otra bonificación
        nomina.agregar_bonificacion(200000)
        assert nomina.bonificaciones == 700000
    
    def test_agregar_deduccion(self, empleado_test):
        """Prueba agregar deducciones adicionales"""
        nomina = Nomina(empleado_test, "2024-01")
        deducciones_iniciales = nomina.total_deducciones
        
        nomina.agregar_deduccion(100000)
        
        assert nomina.deducciones_adicionales == 100000
        assert nomina.total_deducciones == deducciones_iniciales + 100000
    
    def test_calculo_completo(self, empleado_test):
        """Prueba cálculo completo de nómina"""
        nomina = Nomina(empleado_test, "2024-01")
        
        nomina.agregar_horas_extra(8, 30000)  # 240,000
        nomina.agregar_bonificacion(300000)
        nomina.agregar_deduccion(50000)
        
        devengado_esperado = 3000000 + 240000 + 300000  # 3,540,000
        deducciones_esperadas = (3000000 * 0.08) + 50000  # 240,000 + 50,000 = 290,000
        neto_esperado = devengado_esperado - deducciones_esperadas  # 3,250,000
        
        assert nomina.total_devengado == devengado_esperado
        assert nomina.total_deducciones == deducciones_esperadas
        assert nomina.salario_neto == neto_esperado
    
    def test_to_dict(self, empleado_test):
        """Prueba conversión a diccionario"""
        nomina = Nomina(empleado_test, "2024-01")
        
        dict_nomina = nomina.to_dict()
        
        assert dict_nomina["empleado_cedula"] == "12345"
        assert dict_nomina["empleado_nombre"] == "Juan Pérez"
        assert dict_nomina["periodo"] == "2024-01"
        assert "total_devengado" in dict_nomina
        assert "salario_neto" in dict_nomina
    
    def test_generar_reporte(self, empleado_test):
        """Prueba generación de reporte"""
        nomina = Nomina(empleado_test, "2024-01")
        
        reporte = nomina.generar_reporte()
        
        assert "Juan Pérez" in reporte
        assert "12345" in reporte
        assert "2024-01" in reporte
        assert "DEVENGADO" in reporte
        assert "DEDUCCIONES" in reporte
        assert "NETO A PAGAR" in reporte


class TestSistemaRRHH:
    """Pruebas para la clase SistemaRRHH"""
    
    @pytest.fixture
    def sistema_test(self):
        """Fixture que proporciona un sistema temporal para pruebas"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            archivo_temp = f.name
        
        sistema = SistemaRRHH(archivo_temp)
        yield sistema
        
        # Limpiar archivo temporal
        if os.path.exists(archivo_temp):
            os.unlink(archivo_temp)
    
    def test_inicializacion_sistema_sin_archivo(self, sistema_test):
        """Prueba inicialización sin archivo existente"""
        assert len(sistema_test.empleados) == 0
    
    def test_agregar_empleado_exitoso(self, sistema_test):
        """Prueba agregar empleado exitosamente"""
        resultado = sistema_test.agregar_empleado(
            "12345", "Juan", "Pérez", "Dev", 3000000, "indefinido",
            "123-456", "juan@email.com", 8
        )
        
        assert resultado == True
        assert "12345" in sistema_test.empleados
        assert sistema_test.empleados["12345"].nombre == "Juan"
    
    def test_agregar_empleado_cedula_duplicada(self, sistema_test):
        """Prueba agregar empleado con cédula duplicada"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        resultado = sistema_test.agregar_empleado("12345", "María", "García", "QA", 2500000, "indefinido")
        
        assert resultado == False
        assert sistema_test.empleados["12345"].nombre == "Juan"  # No debe cambiar
    
    def test_agregar_empleado_contrato_invalido(self, sistema_test):
        """Prueba agregar empleado con tipo de contrato inválido"""
        resultado = sistema_test.agregar_empleado(
            "12345", "Juan", "Pérez", "Dev", 3000000, "contrato_invalido"
        )
        
        assert resultado == False
        assert "12345" not in sistema_test.empleados
    
    def test_buscar_empleado_por_nombre(self, sistema_test):
        """Prueba búsqueda de empleado por nombre"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        sistema_test.agregar_empleado("67890", "María", "García", "QA", 2500000, "indefinido")
        
        resultados = sistema_test.buscar_empleado("Juan")
        
        assert len(resultados) == 1
        assert resultados[0].nombre == "Juan"
    
    def test_buscar_empleado_por_cedula(self, sistema_test):
        """Prueba búsqueda de empleado por cédula"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        resultados = sistema_test.buscar_empleado("12345")
        
        assert len(resultados) == 1
        assert resultados[0].cedula == "12345"
    
    def test_buscar_empleado_no_encontrado(self, sistema_test):
        """Prueba búsqueda de empleado no existente"""
        resultados = sistema_test.buscar_empleado("NoExiste")
        
        assert len(resultados) == 0
    
    def test_obtener_empleado_existente(self, sistema_test):
        """Prueba obtener empleado existente"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        empleado = sistema_test.obtener_empleado("12345")
        
        assert empleado is not None
        assert empleado.nombre == "Juan"
    
    def test_obtener_empleado_no_existente(self, sistema_test):
        """Prueba obtener empleado no existente"""
        empleado = sistema_test.obtener_empleado("99999")
        
        assert empleado is None
    
    def test_actualizar_empleado_exitoso(self, sistema_test):
        """Prueba actualización exitosa de empleado"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        resultado = sistema_test.actualizar_empleado("12345", nombre="Juan Carlos", salario_base=3500000)
        
        assert resultado == True
        empleado = sistema_test.obtener_empleado("12345")
        assert empleado.nombre == "Juan Carlos"
        assert empleado.salario_base == 3500000
    
    def test_actualizar_empleado_no_existente(self, sistema_test):
        """Prueba actualización de empleado no existente"""
        resultado = sistema_test.actualizar_empleado("99999", nombre="Nuevo Nombre")
        
        assert resultado == False
    
    def test_eliminar_empleado_exitoso(self, sistema_test):
        """Prueba eliminación lógica exitosa"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        resultado = sistema_test.eliminar_empleado("12345")
        
        assert resultado == True
        empleado = sistema_test.obtener_empleado("12345")
        assert empleado.activo == False
    
    def test_eliminar_empleado_no_existente(self, sistema_test):
        """Prueba eliminación de empleado no existente"""
        resultado = sistema_test.eliminar_empleado("99999")
        
        assert resultado == False
    
    def test_calcular_nomina_empleado_activo(self, sistema_test):
        """Prueba cálculo de nómina para empleado activo"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        nomina = sistema_test.calcular_nomina("12345", "2024-01")
        
        assert nomina is not None
        assert nomina.empleado.cedula == "12345"
        assert nomina.periodo == "2024-01"
    
    def test_calcular_nomina_empleado_inactivo(self, sistema_test):
        """Prueba cálculo de nómina para empleado inactivo"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        sistema_test.eliminar_empleado("12345")
        
        nomina = sistema_test.calcular_nomina("12345", "2024-01")
        
        assert nomina is None
    
    def test_calcular_nomina_empleado_no_existente(self, sistema_test):
        """Prueba cálculo de nómina para empleado no existente"""
        nomina = sistema_test.calcular_nomina("99999", "2024-01")
        
        assert nomina is None
    
    def test_procesar_nomina_completa(self, sistema_test):
        """Prueba procesamiento de nómina completa"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        sistema_test.agregar_empleado("67890", "María", "García", "QA", 2500000, "indefinido")
        sistema_test.eliminar_empleado("67890")  # Inactivo, no debe procesarse
        sistema_test.agregar_empleado("11111", "Pedro", "López", "PM", 4000000, "indefinido")
        
        horas_extra = {"12345": 5, "11111": 3}
        bonificaciones = {"12345": 200000}
        
        nominas = sistema_test.procesar_nomina_completa("2024-01", horas_extra, bonificaciones)
        
        assert len(nominas) == 2  # Solo empleados activos
        
        # Verificar que se guardaron en el historial
        empleado1 = sistema_test.obtener_empleado("12345")
        assert len(empleado1.historial_nominas) == 1
    
    def test_listar_empleados_solo_activos(self, sistema_test):
        """Prueba listar solo empleados activos"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        sistema_test.agregar_empleado("67890", "María", "García", "QA", 2500000, "indefinido")
        sistema_test.eliminar_empleado("67890")
        
        empleados = sistema_test.listar_empleados(incluir_inactivos=False)
        
        assert len(empleados) == 1
        assert empleados[0].nombre == "Juan"
    
    def test_listar_empleados_incluir_inactivos(self, sistema_test):
        """Prueba listar incluyendo empleados inactivos"""
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        sistema_test.agregar_empleado("67890", "María", "García", "QA", 2500000, "indefinido")
        sistema_test.eliminar_empleado("67890")
        
        empleados = sistema_test.listar_empleados(incluir_inactivos=True)
        
        assert len(empleados) == 2
    
    def test_guardar_y_cargar_datos(self, sistema_test):
        """Prueba guardar y cargar datos"""
        # Agregar datos de prueba
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        
        # Guardar
        resultado = sistema_test.guardar_datos()
        assert resultado == True
        
        # Crear nuevo sistema con el mismo archivo
        nuevo_sistema = SistemaRRHH(sistema_test.archivo_datos)
        
        # Verificar que los datos se cargaron
        assert len(nuevo_sistema.empleados) == 1
        assert "12345" in nuevo_sistema.empleados
        assert nuevo_sistema.empleados["12345"].nombre == "Juan"
    
    @patch('builtins.open', side_effect=IOError("Error de archivo"))
    def test_error_al_guardar_datos(self, mock_file, sistema_test):
        """Prueba manejo de error al guardar datos"""
        resultado = sistema_test.guardar_datos()
        assert resultado == False
    
    def test_generar_reporte_nomina_periodo(self, sistema_test):
        """Prueba generación de reporte de nómina por período"""
        # Agregar empleados y procesar nómina
        sistema_test.agregar_empleado("12345", "Juan", "Pérez", "Dev", 3000000, "indefinido")
        sistema_test.agregar_empleado("67890", "María", "García", "QA", 2500000, "indefinido")
        
        sistema_test.procesar_nomina_completa("2024-01")
        
        reporte = sistema_test.generar_reporte_nomina_periodo("2024-01")
        
        assert "2024-01" in reporte
        assert "Juan Pérez" in reporte
        assert "María García" in reporte
        assert "TOTALES" in reporte


class TestIntegracion:
    """Pruebas de integración del sistema completo"""
    
    def test_flujo_completo_empleado(self):
        """Prueba flujo completo: crear empleado, calcular nómina, generar reporte"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            archivo_temp = f.name
        
        try:
            # Crear sistema
            sistema = SistemaRRHH(archivo_temp)
            
            # Agregar empleado
            sistema.agregar_empleado("12345", "Juan", "Pérez", "Desarrollador", 
                                   3000000, "indefinido", "123-456", "juan@email.com")
            
            # Calcular nómina
            nomina = sistema.calcular_nomina("12345", "2024-01")
            nomina.agregar_horas_extra(8, 25000)
            nomina.agregar_bonificacion(300000)
            
            # Guardar nómina en historial
            nomina.empleado.agregar_nomina(nomina.to_dict())
            
            # Actualizar valoración
            empleado = sistema.obtener_empleado("12345")
            empleado.actualizar_valoracion(9)
            
            # Guardar datos
            sistema.guardar_datos()
            
            # Crear nuevo sistema para verificar persistencia
            nuevo_sistema = SistemaRRHH(archivo_temp)
            empleado_cargado = nuevo_sistema.obtener_empleado("12345")
            
            # Verificaciones finales
            assert empleado_cargado is not None
            assert empleado_cargado.nombre == "Juan"
            assert empleado_cargado.valoracion == 9
            assert len(empleado_cargado.historial_nominas) == 1
            assert len(empleado_cargado.historial_valoraciones) == 2
            
            # Generar reporte
            reporte = nuevo_sistema.generar_reporte_nomina_periodo("2024-01")
            assert "Juan Pérez" in reporte
            
        finally:
            if os.path.exists(archivo_temp):
                os.unlink(archivo_temp)


# Configuración para ejecutar las pruebas
if __name__ == "__main__":
    pytest.main([__file__, "-v"])