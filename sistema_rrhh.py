import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class Empleado:
    """Clase que representa un empleado del sistema"""
    
    def __init__(self, cedula: str, nombre: str, apellido: str, cargo: str, 
                 salario_base: float, tipo_contrato: str, telefono: str = "", 
                 email: str = "", valoracion: int = 5):
        self.cedula = cedula
        self.nombre = nombre
        self.apellido = apellido
        self.cargo = cargo
        self.salario_base = salario_base
        self.tipo_contrato = tipo_contrato
        self.telefono = telefono
        self.email = email
        self.valoracion = valoracion
        self.activo = True
        self.historial_nominas = []
        self.historial_valoraciones = [{"fecha": datetime.now().isoformat(), "valoracion": valoracion}]
    
    def actualizar_valoracion(self, nueva_valoracion: int):
        """Actualiza la valoración del empleado y mantiene historial"""
        if 1 <= nueva_valoracion <= 10:
            self.valoracion = nueva_valoracion
            self.historial_valoraciones.append({
                "fecha": datetime.now().isoformat(),
                "valoracion": nueva_valoracion
            })
            return True
        return False
    
    def agregar_nomina(self, nomina_data: Dict):
        """Agrega una nómina al historial del empleado"""
        self.historial_nominas.append(nomina_data)
    
    def desactivar(self):
        """Realiza eliminación lógica del empleado"""
        self.activo = False
    
    def activar(self):
        """Reactiva un empleado desactivado"""
        self.activo = True
    
    def to_dict(self) -> Dict:
        """Convierte el empleado a diccionario para serialización JSON"""
        return {
            "cedula": self.cedula,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "cargo": self.cargo,
            "salario_base": self.salario_base,
            "tipo_contrato": self.tipo_contrato,
            "telefono": self.telefono,
            "email": self.email,
            "valoracion": self.valoracion,
            "activo": self.activo,
            "historial_nominas": self.historial_nominas,
            "historial_valoraciones": self.historial_valoraciones
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crea un empleado desde un diccionario"""
        empleado = cls(
            cedula=data["cedula"],
            nombre=data["nombre"],
            apellido=data["apellido"],
            cargo=data["cargo"],
            salario_base=data["salario_base"],
            tipo_contrato=data["tipo_contrato"],
            telefono=data.get("telefono", ""),
            email=data.get("email", ""),
            valoracion=data.get("valoracion", 5)
        )
        empleado.activo = data.get("activo", True)
        empleado.historial_nominas = data.get("historial_nominas", [])
        empleado.historial_valoraciones = data.get("historial_valoraciones", [])
        return empleado
    
    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.nombre} {self.apellido} - {self.cargo} ({estado})"

class Nomina:
    """Clase que maneja los cálculos de nómina"""
    
    def __init__(self, empleado: Empleado, periodo: str):
        self.empleado = empleado
        self.periodo = periodo  # Formato: "YYYY-MM"
        self.fecha_calculo = datetime.now().isoformat()
        self.salario_base = empleado.salario_base
        self.horas_extra = 0
        self.valor_hora_extra = 20000  # Valor por defecto
        self.bonificaciones = 0
        self.deducciones_adicionales = 0
        
        # Deducciones legales colombianas
        self.deduccion_salud = self.salario_base * 0.04  # 4%
        self.deduccion_pension = self.salario_base * 0.04  # 4%
        
        # Cálculos
        self.total_devengado = 0
        self.total_deducciones = 0
        self.salario_neto = 0
        
        self._calcular_nomina()
    
    def agregar_horas_extra(self, horas: int, valor_por_hora: float = None):
        """Agrega horas extra al cálculo de nómina"""
        self.horas_extra = horas
        if valor_por_hora:
            self.valor_hora_extra = valor_por_hora
        self._calcular_nomina()
    
    def agregar_bonificacion(self, monto: float):
        """Agrega bonificaciones al cálculo"""
        self.bonificaciones += monto
        self._calcular_nomina()
    
    def agregar_deduccion(self, monto: float):
        """Agrega deducciones adicionales"""
        self.deducciones_adicionales += monto
        self._calcular_nomina()
    
    def _calcular_nomina(self):
        """Realiza todos los cálculos de la nómina"""
        # Total devengado
        valor_horas_extra = self.horas_extra * self.valor_hora_extra
        self.total_devengado = self.salario_base + valor_horas_extra + self.bonificaciones
        
        # Total deducciones
        self.total_deducciones = (self.deduccion_salud + self.deduccion_pension + 
                                self.deducciones_adicionales)
        
        # Salario neto
        self.salario_neto = self.total_devengado - self.total_deducciones
    
    def to_dict(self) -> Dict:
        """Convierte la nómina a diccionario"""
        return {
            "empleado_cedula": self.empleado.cedula,
            "empleado_nombre": f"{self.empleado.nombre} {self.empleado.apellido}",
            "periodo": self.periodo,
            "fecha_calculo": self.fecha_calculo,
            "salario_base": self.salario_base,
            "horas_extra": self.horas_extra,
            "valor_hora_extra": self.valor_hora_extra,
            "bonificaciones": self.bonificaciones,
            "deduccion_salud": self.deduccion_salud,
            "deduccion_pension": self.deduccion_pension,
            "deducciones_adicionales": self.deducciones_adicionales,
            "total_devengado": self.total_devengado,
            "total_deducciones": self.total_deducciones,
            "salario_neto": self.salario_neto
        }
    
    def generar_reporte(self) -> str:
        """Genera un reporte detallado de la nómina"""
        reporte = f"""
=== LIQUIDACIÓN DE NÓMINA ===
Empleado: {self.empleado.nombre} {self.empleado.apellido}
Cédula: {self.empleado.cedula}
Cargo: {self.empleado.cargo}
Período: {self.periodo}
Fecha de cálculo: {self.fecha_calculo[:10]}

DEVENGADO:
Salario Base: ${self.salario_base:,.2f}
Horas Extra ({self.horas_extra}h): ${self.horas_extra * self.valor_hora_extra:,.2f}
Bonificaciones: ${self.bonificaciones:,.2f}
TOTAL DEVENGADO: ${self.total_devengado:,.2f}

DEDUCCIONES:
Salud (4%): ${self.deduccion_salud:,.2f}
Pensión (4%): ${self.deduccion_pension:,.2f}
Otras deducciones: ${self.deducciones_adicionales:,.2f}
TOTAL DEDUCCIONES: ${self.total_deducciones:,.2f}

NETO A PAGAR: ${self.salario_neto:,.2f}
================================
        """
        return reporte

class SistemaRRHH:
    """Clase principal que maneja todo el sistema de RRHH"""
    
    def __init__(self, archivo_datos: str = "empleados.json"):
        self.archivo_datos = archivo_datos
        self.empleados: Dict[str, Empleado] = {}
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los datos desde el archivo JSON"""
        if os.path.exists(self.archivo_datos):
            try:
                with open(self.archivo_datos, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    for emp_data in data.get("empleados", []):
                        empleado = Empleado.from_dict(emp_data)
                        self.empleados[empleado.cedula] = empleado
                print(f"Datos cargados exitosamente. {len(self.empleados)} empleados encontrados.")
            except Exception as e:
                print(f"Error al cargar datos: {e}")
                self.empleados = {}
        else:
            print("Archivo de datos no encontrado. Iniciando con base de datos vacía.")
    
    def guardar_datos(self):
        """Guarda los datos en el archivo JSON"""
        try:
            data = {
                "sistema_info": {
                    "version": "1.0",
                    "ultima_actualizacion": datetime.now().isoformat(),
                    "total_empleados": len(self.empleados)
                },
                "empleados": [emp.to_dict() for emp in self.empleados.values()]
            }
            with open(self.archivo_datos, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            print("Datos guardados exitosamente.")
            return True
        except Exception as e:
            print(f"Error al guardar datos: {e}")
            return False
    
    def agregar_empleado(self, cedula: str, nombre: str, apellido: str, cargo: str,
                        salario_base: float, tipo_contrato: str, telefono: str = "",
                        email: str = "", valoracion: int = 5) -> bool:
        """Agrega un nuevo empleado al sistema"""
        if cedula in self.empleados:
            print("Error: Ya existe un empleado con esta cédula.")
            return False
        
        # Validación de tipo de contrato
        contratos_validos = ["indefinido", "termino_fijo", "prestacion_servicios"]
        if tipo_contrato.lower() not in contratos_validos:
            print("Tipo de contrato inválido. Use: indefinido, termino_fijo, prestacion_servicios")
            return False
        
        empleado = Empleado(cedula, nombre, apellido, cargo, salario_base,
                          tipo_contrato, telefono, email, valoracion)
        self.empleados[cedula] = empleado
        print(f"Empleado {nombre} {apellido} agregado exitosamente.")
        return True
    
    def buscar_empleado(self, criterio: str) -> List[Empleado]:
        """Busca empleados por nombre, apellido o cédula"""
        resultados = []
        criterio = criterio.lower()
        
        for empleado in self.empleados.values():
            if (criterio in empleado.nombre.lower() or
                criterio in empleado.apellido.lower() or
                criterio in empleado.cedula):
                resultados.append(empleado)
        
        return resultados
    
    def obtener_empleado(self, cedula: str) -> Optional[Empleado]:
        """Obtiene un empleado por su cédula"""
        return self.empleados.get(cedula)
    
    def actualizar_empleado(self, cedula: str, **kwargs) -> bool:
        """Actualiza los datos de un empleado"""
        if cedula not in self.empleados:
            print("Empleado no encontrado.")
            return False
        
        empleado = self.empleados[cedula]
        campos_actualizables = ['nombre', 'apellido', 'cargo', 'salario_base',
                              'tipo_contrato', 'telefono', 'email']
        
        for campo, valor in kwargs.items():
            if campo in campos_actualizables and valor:
                setattr(empleado, campo, valor)
        
        print("Empleado actualizado exitosamente.")
        return True
    
    def eliminar_empleado(self, cedula: str) -> bool:
        """Realiza eliminación lógica del empleado"""
        if cedula not in self.empleados:
            print("Empleado no encontrado.")
            return False
        
        self.empleados[cedula].desactivar()
        print("Empleado desactivado exitosamente.")
        return True
    
    def calcular_nomina(self, cedula: str, periodo: str) -> Optional[Nomina]:
        """Calcula la nómina de un empleado para un período específico"""
        empleado = self.obtener_empleado(cedula)
        if not empleado:
            print("Empleado no encontrado.")
            return None
        
        if not empleado.activo:
            print("No se puede calcular nómina para empleado inactivo.")
            return None
        
        nomina = Nomina(empleado, periodo)
        return nomina
    
    def procesar_nomina_completa(self, periodo: str, horas_extra: Dict[str, int] = None,
                               bonificaciones: Dict[str, float] = None) -> List[Nomina]:
        """Procesa nómina para todos los empleados activos"""
        nominas = []
        horas_extra = horas_extra or {}
        bonificaciones = bonificaciones or {}
        
        for empleado in self.empleados.values():
            if empleado.activo:
                nomina = Nomina(empleado, periodo)
                
                # Agregar horas extra si las hay
                if empleado.cedula in horas_extra:
                    nomina.agregar_horas_extra(horas_extra[empleado.cedula])
                
                # Agregar bonificaciones si las hay
                if empleado.cedula in bonificaciones:
                    nomina.agregar_bonificacion(bonificaciones[empleado.cedula])
                
                # Guardar en el historial del empleado
                empleado.agregar_nomina(nomina.to_dict())
                nominas.append(nomina)
        
        return nominas
    
    def generar_reporte_nomina_periodo(self, periodo: str) -> str:
        """Genera reporte consolidado de nómina por período"""
        total_devengado = 0
        total_deducciones = 0
        total_neto = 0
        count_empleados = 0
        
        reporte = f"\n=== REPORTE DE NÓMINA - PERÍODO {periodo} ===\n"
        reporte += f"{'EMPLEADO':<30} {'CARGO':<20} {'DEVENGADO':<15} {'DEDUCCIONES':<15} {'NETO':<15}\n"
        reporte += "-" * 95 + "\n"
        
        for empleado in self.empleados.values():
            if empleado.activo:
                # Buscar nómina del período en el historial
                nomina_periodo = None
                for nomina_data in empleado.historial_nominas:
                    if nomina_data.get("periodo") == periodo:
                        nomina_periodo = nomina_data
                        break
                
                if nomina_periodo:
                    nombre_completo = f"{empleado.nombre} {empleado.apellido}"
                    devengado = nomina_periodo["total_devengado"]
                    deducciones = nomina_periodo["total_deducciones"]
                    neto = nomina_periodo["salario_neto"]
                    
                    reporte += f"{nombre_completo[:29]:<30} {empleado.cargo[:19]:<20} "
                    reporte += f"${devengado:>12,.0f} ${deducciones:>12,.0f} ${neto:>12,.0f}\n"
                    
                    total_devengado += devengado
                    total_deducciones += deducciones
                    total_neto += neto
                    count_empleados += 1
        
        reporte += "-" * 95 + "\n"
        reporte += f"{'TOTALES':<50} ${total_devengado:>12,.0f} ${total_deducciones:>12,.0f} ${total_neto:>12,.0f}\n"
        reporte += f"\nEmpleados procesados: {count_empleados}\n"
        reporte += "=" * 95 + "\n"
        
        return reporte
    
    def listar_empleados(self, incluir_inactivos: bool = False) -> List[Empleado]:
        """Lista todos los empleados del sistema"""
        empleados_lista = []
        for empleado in self.empleados.values():
            if incluir_inactivos or empleado.activo:
                empleados_lista.append(empleado)
        return sorted(empleados_lista, key=lambda x: f"{x.apellido} {x.nombre}")

def mostrar_menu():
    """Muestra el menú principal del sistema"""
    print("\n" + "="*50)
    print("    SISTEMA DE GESTIÓN DE RECURSOS HUMANOS")
    print("="*50)
    print("1. Agregar empleado")
    print("2. Buscar empleado")
    print("3. Listar empleados")
    print("4. Actualizar empleado")
    print("5. Desactivar empleado")
    print("6. Calcular nómina individual")
    print("7. Procesar nómina masiva")
    print("8. Generar reporte de nómina")
    print("9. Actualizar valoración empleado")
    print("0. Salir")
    print("="*50)

def main():
    """Función principal del programa"""
    sistema = SistemaRRHH()
    
    while True:
        mostrar_menu()
        try:
            opcion = input("Seleccione una opción: ").strip()
            
            if opcion == "1":
                # Agregar empleado
                print("\n--- AGREGAR EMPLEADO ---")
                cedula = input("Cédula: ").strip()
                nombre = input("Nombre: ").strip()
                apellido = input("Apellido: ").strip()
                cargo = input("Cargo: ").strip()
                salario_base = float(input("Salario base: "))
                print("Tipos de contrato: indefinido, termino_fijo, prestacion_servicios")
                tipo_contrato = input("Tipo de contrato: ").strip()
                telefono = input("Teléfono (opcional): ").strip()
                email = input("Email (opcional): ").strip()
                
                sistema.agregar_empleado(cedula, nombre, apellido, cargo, 
                                       salario_base, tipo_contrato, telefono, email)
                sistema.guardar_datos()
            
            elif opcion == "2":
                # Buscar empleado
                print("\n--- BUSCAR EMPLEADO ---")
                criterio = input("Ingrese nombre, apellido o cédula: ").strip()
                resultados = sistema.buscar_empleado(criterio)
                
                if resultados:
                    print(f"\nSe encontraron {len(resultados)} resultado(s):")
                    for i, emp in enumerate(resultados, 1):
                        print(f"{i}. {emp} - ${emp.salario_base:,.0f}")
                else:
                    print("No se encontraron empleados.")
            
            elif opcion == "3":
                # Listar empleados
                print("\n--- LISTA DE EMPLEADOS ---")
                incluir_inactivos = input("¿Incluir empleados inactivos? (s/n): ").lower() == 's'
                empleados = sistema.listar_empleados(incluir_inactivos)
                
                if empleados:
                    print(f"\n{'#':<3} {'NOMBRE':<25} {'CARGO':<20} {'SALARIO':<15} {'ESTADO':<10}")
                    print("-" * 73)
                    for i, emp in enumerate(empleados, 1):
                        estado = "Activo" if emp.activo else "Inactivo"
                        nombre_completo = f"{emp.nombre} {emp.apellido}"
                        print(f"{i:<3} {nombre_completo[:24]:<25} {emp.cargo[:19]:<20} "
                              f"${emp.salario_base:>12,.0f} {estado:<10}")
                else:
                    print("No hay empleados registrados.")
            
            elif opcion == "4":
                # Actualizar empleado
                print("\n--- ACTUALIZAR EMPLEADO ---")
                cedula = input("Cédula del empleado: ").strip()
                empleado = sistema.obtener_empleado(cedula)
                
                if empleado:
                    print(f"Empleado encontrado: {empleado}")
                    print("Deje en blanco los campos que no desea modificar:")
                    
                    nombre = input(f"Nombre ({empleado.nombre}): ").strip()
                    apellido = input(f"Apellido ({empleado.apellido}): ").strip()
                    cargo = input(f"Cargo ({empleado.cargo}): ").strip()
                    salario = input(f"Salario ({empleado.salario_base}): ").strip()
                    telefono = input(f"Teléfono ({empleado.telefono}): ").strip()
                    email = input(f"Email ({empleado.email}): ").strip()
                    
                    kwargs = {}
                    if nombre: kwargs['nombre'] = nombre
                    if apellido: kwargs['apellido'] = apellido
                    if cargo: kwargs['cargo'] = cargo
                    if salario: kwargs['salario_base'] = float(salario)
                    if telefono: kwargs['telefono'] = telefono
                    if email: kwargs['email'] = email
                    
                    sistema.actualizar_empleado(cedula, **kwargs)
                    sistema.guardar_datos()
                else:
                    print("Empleado no encontrado.")
            
            elif opcion == "5":
                # Desactivar empleado
                print("\n--- DESACTIVAR EMPLEADO ---")
                cedula = input("Cédula del empleado: ").strip()
                sistema.eliminar_empleado(cedula)
                sistema.guardar_datos()
            
            elif opcion == "6":
                # Calcular nómina individual
                print("\n--- CALCULAR NÓMINA INDIVIDUAL ---")
                cedula = input("Cédula del empleado: ").strip()
                periodo = input("Período (YYYY-MM): ").strip()
                
                nomina = sistema.calcular_nomina(cedula, periodo)
                if nomina:
                    # Preguntar por variables adicionales
                    horas_extra = input("Horas extra (0 si no hay): ").strip()
                    if horas_extra and horas_extra != "0":
                        nomina.agregar_horas_extra(int(horas_extra))
                    
                    bonificacion = input("Bonificaciones (0 si no hay): ").strip()
                    if bonificacion and bonificacion != "0":
                        nomina.agregar_bonificacion(float(bonificacion))
                    
                    print(nomina.generar_reporte())
                    
                    # Guardar en historial
                    nomina.empleado.agregar_nomina(nomina.to_dict())
                    sistema.guardar_datos()
            
            elif opcion == "7":
                # Procesar nómina masiva
                print("\n--- PROCESAR NÓMINA MASIVA ---")
                periodo = input("Período (YYYY-MM): ").strip()
                
                nominas = sistema.procesar_nomina_completa(periodo)
                print(f"\nNómina procesada para {len(nominas)} empleados.")
                
                for nomina in nominas:
                    print(f"- {nomina.empleado.nombre} {nomina.empleado.apellido}: "
                          f"${nomina.salario_neto:,.0f}")
                
                sistema.guardar_datos()
            
            elif opcion == "8":
                # Generar reporte de nómina
                print("\n--- REPORTE DE NÓMINA ---")
                periodo = input("Período (YYYY-MM): ").strip()
                reporte = sistema.generar_reporte_nomina_periodo(periodo)
                print(reporte)
            
            elif opcion == "9":
                # Actualizar valoración
                print("\n--- ACTUALIZAR VALORACIÓN ---")
                cedula = input("Cédula del empleado: ").strip()
                empleado = sistema.obtener_empleado(cedula)
                
                if empleado:
                    print(f"Empleado: {empleado}")
                    print(f"Valoración actual: {empleado.valoracion}")
                    nueva_valoracion = int(input("Nueva valoración (1-10): "))
                    
                    if empleado.actualizar_valoracion(nueva_valoracion):
                        print("Valoración actualizada exitosamente.")
                        sistema.guardar_datos()
                    else:
                        print("Valoración inválida. Debe ser entre 1 y 10.")
                else:
                    print("Empleado no encontrado.")
            
            elif opcion == "0":
                # Salir
                print("Guardando datos...")
                sistema.guardar_datos()
                print("¡Hasta luego!")
                break
            
            else:
                print("Opción inválida. Por favor seleccione una opción válida.")
        
        except ValueError as e:
            print(f"Error en el formato de datos: {e}")
        except KeyboardInterrupt:
            print("\n\nSaliendo del sistema...")
            sistema.guardar_datos()
            break
        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()