import uuid
import datetime
import json
import os
from typing import List, Dict, Optional

# Constantes
TIPOS_ID = ["CC", "TI", "CE"]
ESTADOS_ENVIO = [
    "Recibido", 
    "En Tránsito", 
    "En Ciudad Destino", 
    "En Bodega De La Transportadora", 
    "En Reparto", 
    "Entregado"
]

# Clase para manejar los clientes (remitentes)
class Cliente:
    def __init__(self, nombres: str, apellidos: str, id_numero: str, 
                 tipo_id: str, direccion: str, telefono_fijo: str, 
                 celular: str, barrio: str):
        self.nombres = nombres
        self.apellidos = apellidos
        self.id_numero = id_numero
        
        # Validar que el tipo de ID sea válido
        if tipo_id not in TIPOS_ID:
            raise ValueError(f"Tipo de ID inválido. Debe ser uno de {TIPOS_ID}")
        self.tipo_id = tipo_id
        
        self.direccion = direccion
        self.telefono_fijo = telefono_fijo
        self.celular = celular
        self.barrio = barrio
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para almacenamiento"""
        return {
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "id_numero": self.id_numero,
            "tipo_id": self.tipo_id,
            "direccion": self.direccion,
            "telefono_fijo": self.telefono_fijo,
            "celular": self.celular,
            "barrio": self.barrio
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Cliente':
        """Crea un objeto Cliente desde un diccionario"""
        return cls(
            nombres=data["nombres"],
            apellidos=data["apellidos"],
            id_numero=data["id_numero"],
            tipo_id=data["tipo_id"],
            direccion=data["direccion"],
            telefono_fijo=data["telefono_fijo"],
            celular=data["celular"],
            barrio=data["barrio"]
        )
    
    def actualizar_informacion(self, direccion: str = None, telefono_fijo: str = None, 
                              celular: str = None, barrio: str = None) -> None:
        """Permite actualizar la información del cliente"""
        if direccion:
            self.direccion = direccion
        if telefono_fijo:
            self.telefono_fijo = telefono_fijo
        if celular:
            self.celular = celular
        if barrio:
            self.barrio = barrio

# Clase para manejar los destinatarios
class Destinatario:
    def __init__(self, nombre: str, direccion: str, telefono: str, 
                 ciudad: str, barrio: str):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.ciudad = ciudad
        self.barrio = barrio
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para almacenamiento"""
        return {
            "nombre": self.nombre,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "ciudad": self.ciudad,
            "barrio": self.barrio
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Destinatario':
        """Crea un objeto Destinatario desde un diccionario"""
        return cls(
            nombre=data["nombre"],
            direccion=data["direccion"],
            telefono=data["telefono"],
            ciudad=data["ciudad"],
            barrio=data["barrio"]
        )

# Clase para manejar los envíos
class Envio:
    def __init__(self, fecha_envio: datetime.datetime, 
                 destinatario: Destinatario, id_remitente: str):
        self.fecha_envio = fecha_envio
        self.hora_envio = fecha_envio.time()
        self.destinatario = destinatario
        self.id_remitente = id_remitente
        # Generar número de guía único automáticamente
        self.numero_guia = str(uuid.uuid4())
        # Inicializar el estado como "Recibido"
        self.estado = ESTADOS_ENVIO[0]
        # Historial de cambios de estado
        self.historial_estados = [{
            "estado": self.estado,
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "descripcion": "Paquete recibido en la oficina"
        }]
    
    def actualizar_estado(self, nuevo_estado: str, descripcion: str = "") -> None:
        """Actualiza el estado del envío y registra en el historial"""
        if nuevo_estado not in ESTADOS_ENVIO:
            raise ValueError(f"Estado inválido. Debe ser uno de {ESTADOS_ENVIO}")
        
        self.estado = nuevo_estado
        self.historial_estados.append({
            "estado": nuevo_estado,
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "descripcion": descripcion
        })
    
    def to_dict(self) -> Dict:
        """Convierte el objeto a un diccionario para almacenamiento"""
        return {
            "fecha_envio": self.fecha_envio.strftime("%Y-%m-%d"),
            "hora_envio": self.hora_envio.strftime("%H:%M:%S"),
            "destinatario": self.destinatario.to_dict(),
            "id_remitente": self.id_remitente,
            "numero_guia": self.numero_guia,
            "estado": self.estado,
            "historial_estados": self.historial_estados
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Envio':
        """Crea un objeto Envio desde un diccionario"""
        fecha_envio = datetime.datetime.strptime(
            f"{data['fecha_envio']} {data['hora_envio']}", 
            "%Y-%m-%d %H:%M:%S"
        )
        envio = cls(
            fecha_envio=fecha_envio,
            destinatario=Destinatario.from_dict(data["destinatario"]),
            id_remitente=data["id_remitente"]
        )
        envio.numero_guia = data["numero_guia"]
        envio.estado = data["estado"]
        envio.historial_estados = data["historial_estados"]
        return envio

# Clase principal del sistema
class SistemaGestionEnvios:
    def __init__(self):
        self.clientes = {}  # Diccionario de clientes {id_numero: Cliente}
        self.envios = {}  # Diccionario de envíos {numero_guia: Envio}
        
        # Crear directorio de datos si no existe
        os.makedirs("datos", exist_ok=True)
        
        # Cargar datos si existen
        self.cargar_datos()
    
    def cargar_datos(self) -> None:
        """Carga los datos del sistema desde archivos JSON"""
        try:
            # Cargar clientes
            if os.path.exists("datos/clientes.json"):
                with open("datos/clientes.json", "r", encoding="utf-8") as f:
                    clientes_data = json.load(f)
                    for id_numero, cliente_data in clientes_data.items():
                        self.clientes[id_numero] = Cliente.from_dict(cliente_data)
            
            # Cargar envíos
            if os.path.exists("datos/envios.json"):
                with open("datos/envios.json", "r", encoding="utf-8") as f:
                    envios_data = json.load(f)
                    for numero_guia, envio_data in envios_data.items():
                        self.envios[numero_guia] = Envio.from_dict(envio_data)
        except Exception as e:
            print(f"Error al cargar datos: {e}")
    
    def guardar_datos(self) -> None:
        """Guarda los datos del sistema en archivos JSON"""
        try:
            # Guardar clientes
            clientes_data = {id_numero: cliente.to_dict() for id_numero, cliente in self.clientes.items()}
            with open("datos/clientes.json", "w", encoding="utf-8") as f:
                json.dump(clientes_data, f, indent=4, ensure_ascii=False)
            
            # Guardar envíos
            envios_data = {envio.numero_guia: envio.to_dict() for envio in self.envios.values()}
            with open("datos/envios.json", "w", encoding="utf-8") as f:
                json.dump(envios_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar datos: {e}")
    
    def registrar_cliente(self, nombres: str, apellidos: str, id_numero: str, 
                         tipo_id: str, direccion: str, telefono_fijo: str, 
                         celular: str, barrio: str) -> Cliente:
        """Registra un nuevo cliente en el sistema"""
        if id_numero in self.clientes:
            raise ValueError(f"Ya existe un cliente con el ID {id_numero}")
        
        cliente = Cliente(
            nombres=nombres,
            apellidos=apellidos,
            id_numero=id_numero,
            tipo_id=tipo_id,
            direccion=direccion,
            telefono_fijo=telefono_fijo,
            celular=celular,
            barrio=barrio
        )
        
        self.clientes[id_numero] = cliente
        self.guardar_datos()
        return cliente
    
    def actualizar_cliente(self, id_numero: str, **kwargs) -> Cliente:
        """Actualiza la información de un cliente existente"""
        if id_numero not in self.clientes:
            raise ValueError(f"No existe un cliente con el ID {id_numero}")
        
        cliente = self.clientes[id_numero]
        cliente.actualizar_informacion(**kwargs)
        self.guardar_datos()
        return cliente
    
    def buscar_cliente(self, id_numero: str) -> Optional[Cliente]:
        """Busca un cliente por su número de identificación"""
        return self.clientes.get(id_numero)
    
    def registrar_envio(self, fecha_envio: datetime.datetime, 
                       destinatario_nombre: str, destinatario_direccion: str,
                       destinatario_telefono: str, destinatario_ciudad: str,
                       destinatario_barrio: str, id_remitente: str) -> Envio:
        """Registra un nuevo envío en el sistema"""
        # Verificar que el remitente esté registrado
        if id_remitente not in self.clientes:
            raise ValueError(f"No existe un cliente con el ID {id_remitente}")
        
        # Crear el destinatario
        destinatario = Destinatario(
            nombre=destinatario_nombre,
            direccion=destinatario_direccion,
            telefono=destinatario_telefono,
            ciudad=destinatario_ciudad,
            barrio=destinatario_barrio
        )
        
        # Crear el envío
        envio = Envio(
            fecha_envio=fecha_envio,
            destinatario=destinatario,
            id_remitente=id_remitente
        )
        
        # Guardar el envío
        self.envios[envio.numero_guia] = envio
        self.guardar_datos()
        return envio
    
    def buscar_envio(self, numero_guia: str) -> Optional[Envio]:
        """Busca un envío por su número de guía"""
        return self.envios.get(numero_guia)
    
    def buscar_envios_por_remitente(self, id_remitente: str) -> List[Envio]:
        """Busca todos los envíos realizados por un remitente"""
        return [envio for envio in self.envios.values() if envio.id_remitente == id_remitente]
    
    def buscar_multiple_envios(self, numeros_guia: List[str]) -> Dict[str, Optional[Envio]]:
        """Busca múltiples envíos por sus números de guía"""
        return {numero_guia: self.buscar_envio(numero_guia) for numero_guia in numeros_guia}
    
    def actualizar_estado_envio(self, numero_guia: str, nuevo_estado: str, descripcion: str = "") -> Envio:
        """Actualiza el estado de un envío existente"""
        envio = self.buscar_envio(numero_guia)
        if not envio:
            raise ValueError(f"No existe un envío con el número de guía {numero_guia}")
        
        envio.actualizar_estado(nuevo_estado, descripcion)
        self.guardar_datos()
        return envio
    
    def generar_informe_envios(self, fecha_inicio: datetime.date, fecha_fin: datetime.date) -> Dict:
        """Genera un informe de envíos en un período de tiempo"""
        envios_periodo = [
            envio for envio in self.envios.values()
            if datetime.datetime.strptime(envio.fecha_envio.strftime("%Y-%m-%d"), "%Y-%m-%d").date() >= fecha_inicio
            and datetime.datetime.strptime(envio.fecha_envio.strftime("%Y-%m-%d"), "%Y-%m-%d").date() <= fecha_fin
        ]
        
        # Contadores por estado
        conteo_estados = {estado: 0 for estado in ESTADOS_ENVIO}
        for envio in envios_periodo:
            conteo_estados[envio.estado] += 1
        
        # Contadores por ciudad destino
        conteo_ciudades = {}
        for envio in envios_periodo:
            ciudad = envio.destinatario.ciudad
            if ciudad not in conteo_ciudades:
                conteo_ciudades[ciudad] = 0
            conteo_ciudades[ciudad] += 1
        
        # Tiempo promedio de entrega (para envíos entregados)
        envios_entregados = [
            envio for envio in envios_periodo
            if envio.estado == "Entregado"
        ]
        
        tiempos_entrega = []
        for envio in envios_entregados:
            fecha_recibido = datetime.datetime.strptime(envio.historial_estados[0]["fecha"], "%Y-%m-%d %H:%M:%S")
            fecha_entregado = None
            for estado in envio.historial_estados:
                if estado["estado"] == "Entregado":
                    fecha_entregado = datetime.datetime.strptime(estado["fecha"], "%Y-%m-%d %H:%M:%S")
                    break
            
            if fecha_entregado:
                tiempo_entrega = (fecha_entregado - fecha_recibido).total_seconds() / 3600  # En horas
                tiempos_entrega.append(tiempo_entrega)
        
        tiempo_promedio = sum(tiempos_entrega) / len(tiempos_entrega) if tiempos_entrega else 0
        
        return {
            "total_envios": len(envios_periodo),
            "conteo_estados": conteo_estados,
            "conteo_ciudades": conteo_ciudades,
            "envios_entregados": len(envios_entregados),
            "tiempo_promedio_entrega_horas": tiempo_promedio
        }

# Interfaz de usuario en consola
class InterfazConsola:
    def __init__(self):
        self.sistema = SistemaGestionEnvios()
    
    def mostrar_menu_principal(self):
        print("\n===== SISTEMA DE GESTIÓN DE ENVÍOS =====")
        print("1. Gestión de Clientes")
        print("2. Gestión de Envíos")
        print("3. Seguimiento de Paquetes")
        print("4. Informes")
        print("5. Salir")
        return input("Seleccione una opción: ")
    
    def menu_gestion_clientes(self):
        while True:
            print("\n===== GESTIÓN DE CLIENTES =====")
            print("1. Registrar nuevo cliente")
            print("2. Actualizar información de cliente")
            print("3. Buscar cliente")
            print("4. Ver todos los clientes")
            print("5. Volver al menú principal")
            opcion = input("Seleccione una opción: ")
            
            if opcion == "1":
                self.registrar_cliente()
            elif opcion == "2":
                self.actualizar_cliente()
            elif opcion == "3":
                self.buscar_cliente()
            elif opcion == "4":
                self.ver_todos_clientes()
            elif opcion == "5":
                break
            else:
                print("Opción inválida. Inténtelo de nuevo.")
    
    def registrar_cliente(self):
        print("\n----- Registrar Nuevo Cliente -----")
        try:
            nombres = input("Nombres: ")
            apellidos = input("Apellidos: ")
            id_numero = input("Número de identificación: ")
            
            print(f"Tipos de identificación disponibles: {', '.join(TIPOS_ID)}")
            tipo_id = input("Tipo de identificación: ").upper()
            
            direccion = input("Dirección: ")
            telefono_fijo = input("Teléfono fijo: ")
            celular = input("Número celular: ")
            barrio = input("Barrio de residencia: ")
            
            cliente = self.sistema.registrar_cliente(
                nombres=nombres,
                apellidos=apellidos,
                id_numero=id_numero,
                tipo_id=tipo_id,
                direccion=direccion,
                telefono_fijo=telefono_fijo,
                celular=celular,
                barrio=barrio
            )
            
            print(f"Cliente registrado exitosamente con ID: {cliente.id_numero}")
        except Exception as e:
            print(f"Error al registrar cliente: {e}")
    
    def actualizar_cliente(self):
        print("\n----- Actualizar Información de Cliente -----")
        id_numero = input("Ingrese el número de identificación del cliente: ")
        
        cliente = self.sistema.buscar_cliente(id_numero)
        if not cliente:
            print(f"No se encontró un cliente con ID: {id_numero}")
            return
        
        print(f"Cliente actual: {cliente.nombres} {cliente.apellidos}")
        print("Deje en blanco los campos que no desea modificar")
        
        direccion = input(f"Nueva dirección [{cliente.direccion}]: ")
        telefono_fijo = input(f"Nuevo teléfono fijo [{cliente.telefono_fijo}]: ")
        celular = input(f"Nuevo número celular [{cliente.celular}]: ")
        barrio = input(f"Nuevo barrio de residencia [{cliente.barrio}]: ")
        
        kwargs = {}
        if direccion:
            kwargs["direccion"] = direccion
        if telefono_fijo:
            kwargs["telefono_fijo"] = telefono_fijo
        if celular:
            kwargs["celular"] = celular
        if barrio:
            kwargs["barrio"] = barrio
        
        try:
            cliente = self.sistema.actualizar_cliente(id_numero, **kwargs)
            print("Información del cliente actualizada exitosamente")
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
    
    def buscar_cliente(self):
        print("\n----- Buscar Cliente -----")
        id_numero = input("Ingrese el número de identificación del cliente: ")
        
        cliente = self.sistema.buscar_cliente(id_numero)
        if cliente:
            print(f"\nInformación del cliente:")
            print(f"Nombres: {cliente.nombres}")
            print(f"Apellidos: {cliente.apellidos}")
            print(f"ID: {cliente.id_numero} ({cliente.tipo_id})")
            print(f"Dirección: {cliente.direccion}")
            print(f"Teléfono fijo: {cliente.telefono_fijo}")
            print(f"Celular: {cliente.celular}")
            print(f"Barrio: {cliente.barrio}")
        else:
            print(f"No se encontró un cliente con ID: {id_numero}")
    
    def ver_todos_clientes(self):
        print("\n----- Lista de Clientes -----")
        if not self.sistema.clientes:
            print("No hay clientes registrados en el sistema")
            return
        
        for id_numero, cliente in self.sistema.clientes.items():
            print(f"{cliente.id_numero} - {cliente.nombres} {cliente.apellidos}")
    
    def menu_gestion_envios(self):
        while True:
            print("\n===== GESTIÓN DE ENVÍOS =====")
            print("1. Registrar nuevo envío")
            print("2. Actualizar estado de envío")
            print("3. Buscar envío por número de guía")
            print("4. Ver envíos por remitente")
            print("5. Volver al menú principal")
            opcion = input("Seleccione una opción: ")
            
            if opcion == "1":
                self.registrar_envio()
            elif opcion == "2":
                self.actualizar_estado_envio()
            elif opcion == "3":
                self.buscar_envio()
            elif opcion == "4":
                self.ver_envios_por_remitente()
            elif opcion == "5":
                break
            else:
                print("Opción inválida. Inténtelo de nuevo.")
    
    def registrar_envio(self):
        print("\n----- Registrar Nuevo Envío -----")
        try:
            # Datos del remitente
            id_remitente = input("Número de identificación del remitente: ")
            remitente = self.sistema.buscar_cliente(id_remitente)
            if not remitente:
                print(f"No se encontró un cliente con ID: {id_remitente}")
                print("El remitente debe estar registrado en el sistema")
                return
            
            print(f"Remitente: {remitente.nombres} {remitente.apellidos}")
            
            # Fecha y hora del envío (por defecto la actual)
            fecha_actual = datetime.datetime.now()
            fecha_str = input(f"Fecha del envío (YYYY-MM-DD) [{fecha_actual.strftime('%Y-%m-%d')}]: ")
            hora_str = input(f"Hora del envío (HH:MM) [{fecha_actual.strftime('%H:%M')}]: ")
            
            if not fecha_str:
                fecha_str = fecha_actual.strftime('%Y-%m-%d')
            if not hora_str:
                hora_str = fecha_actual.strftime('%H:%M')
            
            fecha_envio = datetime.datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
            
            # Datos del destinatario
            print("\nInformación del destinatario:")
            destinatario_nombre = input("Nombre completo: ")
            destinatario_direccion = input("Dirección: ")
            destinatario_telefono = input("Teléfono de contacto: ")
            destinatario_ciudad = input("Ciudad: ")
            destinatario_barrio = input("Barrio: ")
            
            # Registrar el envío
            envio = self.sistema.registrar_envio(
                fecha_envio=fecha_envio,
                destinatario_nombre=destinatario_nombre,
                destinatario_direccion=destinatario_direccion,
                destinatario_telefono=destinatario_telefono,
                destinatario_ciudad=destinatario_ciudad,
                destinatario_barrio=destinatario_barrio,
                id_remitente=id_remitente
            )
            
            print(f"\n¡Envío registrado exitosamente!")
            print(f"Número de guía: {envio.numero_guia}")
            print(f"Estado inicial: {envio.estado}")
        except Exception as e:
            print(f"Error al registrar envío: {e}")
    
    def actualizar_estado_envio(self):
        print("\n----- Actualizar Estado de Envío -----")
        numero_guia = input("Ingrese el número de guía del envío: ")
        
        envio = self.sistema.buscar_envio(numero_guia)
        if not envio:
            print(f"No se encontró un envío con el número de guía: {numero_guia}")
            return
        
        print(f"Estado actual: {envio.estado}")
        print(f"Estados disponibles: {', '.join(ESTADOS_ENVIO)}")
        
        nuevo_estado = input("Nuevo estado: ")
        descripcion = input("Descripción o comentario (opcional): ")
        
        try:
            self.sistema.actualizar_estado_envio(numero_guia, nuevo_estado, descripcion)
            print("Estado del envío actualizado exitosamente")
        except Exception as e:
            print(f"Error al actualizar estado: {e}")
    
    def buscar_envio(self):
        print("\n----- Buscar Envío -----")
        numero_guia = input("Ingrese el número de guía: ")
        
        envio = self.sistema.buscar_envio(numero_guia)
        if envio:
            self.mostrar_informacion_envio(envio)
        else:
            print(f"No se encontró un envío con el número de guía: {numero_guia}")
    
    def mostrar_informacion_envio(self, envio):
        print("\n----- Información del Envío -----")
        print(f"Número de guía: {envio.numero_guia}")
        print(f"Fecha de envío: {envio.fecha_envio.strftime('%Y-%m-%d')}")
        print(f"Hora de envío: {envio.hora_envio.strftime('%H:%M:%S')}")
        print(f"Estado actual: {envio.estado}")
        
        # Información del remitente
        remitente = self.sistema.buscar_cliente(envio.id_remitente)
        if remitente:
            print(f"\nRemitente: {remitente.nombres} {remitente.apellidos}")
            print(f"ID: {remitente.id_numero}")
            print(f"Teléfono: {remitente.celular}")
        else:
            print(f"\nRemitente ID: {envio.id_remitente} (No encontrado)")
        
        # Información del destinatario
        print(f"\nDestinatario: {envio.destinatario.nombre}")
        print(f"Dirección: {envio.destinatario.direccion}")
        print(f"Ciudad: {envio.destinatario.ciudad}, Barrio: {envio.destinatario.barrio}")
        print(f"Teléfono: {envio.destinatario.telefono}")
        
        # Historial de estados
        print("\nHistorial de estados:")
        for i, estado in enumerate(envio.historial_estados, 1):
            print(f"{i}. {estado['estado']} - {estado['fecha']}")
            if estado['descripcion']:
                print(f"   Descripción: {estado['descripcion']}")
    
    def ver_envios_por_remitente(self):
        print("\n----- Ver Envíos por Remitente -----")
        id_remitente = input("Ingrese el número de identificación del remitente: ")
        
        remitente = self.sistema.buscar_cliente(id_remitente)
        if not remitente:
            print(f"No se encontró un cliente con ID: {id_remitente}")
            return
        
        envios = self.sistema.buscar_envios_por_remitente(id_remitente)
        if not envios:
            print(f"No hay envíos registrados para el cliente {remitente.nombres} {remitente.apellidos}")
            return
        
        print(f"\nEnvíos de {remitente.nombres} {remitente.apellidos}:")
        for i, envio in enumerate(envios, 1):
            print(f"{i}. Guía: {envio.numero_guia} - Fecha: {envio.fecha_envio.strftime('%Y-%m-%d')} - Estado: {envio.estado}")
        
        ver_detalle = input("\n¿Desea ver el detalle de algún envío? (S/N): ").upper()
        if ver_detalle == 'S':
            indice = int(input("Ingrese el número del envío: ")) - 1
            if 0 <= indice < len(envios):
                self.mostrar_informacion_envio(envios[indice])
            else:
                print("Índice inválido")
    
    def menu_seguimiento_paquetes(self):
        while True:
            print("\n===== SEGUIMIENTO DE PAQUETES =====")
            print("1. Seguimiento por número de guía")
            print("2. Seguimiento múltiple")
            print("3. Volver al menú principal")
            opcion = input("Seleccione una opción: ")
            
            if opcion == "1":
                self.seguimiento_por_guia()
            elif opcion == "2":
                self.seguimiento_multiple()
            elif opcion == "3":
                break
            else:
                print("Opción inválida. Inténtelo de nuevo.")
    
    def seguimiento_por_guia(self):
        print("\n----- Seguimiento de Paquete -----")
        numero_guia = input("Ingrese el número de guía: ")
        
        envio = self.sistema.buscar_envio(numero_guia)
        if envio:
            print("\n----- ESTADO DEL ENVÍO -----")
            print(f"Número de guía: {envio.numero_guia}")
            print(f"Estado actual: {envio.estado}")
            print(f"Destinatario: {envio.destinatario.nombre}")
            print(f"Ciudad destino: {envio.destinatario.ciudad}")
            
            print("\nHistorial de estados:")
            for i, estado in enumerate(envio.historial_estados, 1):
                print(f"{i}. {estado['estado']} - {estado['fecha']}")
                if estado['descripcion']:
                    print(f"   Descripción: {estado['descripcion']}")
        else:
            print(f"No se encontró un envío con el número de guía: {numero_guia}")
    
    def seguimiento_multiple(self):
        print("\n----- Seguimiento Múltiple de Paquetes -----")
        numeros_guia_str = input("Ingrese los números de guía separados por coma: ")
        numeros_guia = [num.strip() for num in numeros_guia_str.split(",")]
        
        resultados = self.sistema.buscar_multiple_envios(numeros_guia)
        
        print("\n----- RESULTADOS DE SEGUIMIENTO -----")
        encontrados = 0
        for numero_guia, envio in resultados.items():
            if envio:
                encontrados += 1
                print(f"\nGuía: {numero_guia}")
                print(f"Estado: {envio.estado}")
                print(f"Destinatario: {envio.destinatario.nombre}")
                print(f"Ciudad: {envio.destinatario.ciudad}")
            else:
                print(f"\nGuía: {numero_guia} - No encontrado")
        
        print(f"\nTotal: {encontrados} de {len(numeros_guia)} envíos encontrados")
    
    def menu_informes(self):
        while True:
            print("\n===== INFORMES =====")
            print("1. Informe de envíos por período")
            print("2. Volver al menú principal")
            opcion = input("Seleccione una opción: ")
            
            if opcion == "1":
                self.generar_informe_envios()
            elif opcion == "2":
                break
            else:
                print("Opción inválida. Inténtelo de nuevo.")
    
    def generar_informe_envios(self):
        print("\n----- Informe de Envíos por Período -----")
        fecha_inicio_str = input("Fecha de inicio (YYYY-MM-DD): ")
        fecha_fin_str = input("Fecha de fin (YYYY-MM-DD): ")
        
        try:
            fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
            
            informe = self.sistema.generar_informe_envios(fecha_inicio, fecha_fin)
            
            print("\n===== INFORME DE ENVÍOS =====")
            print(f"Período: {fecha_inicio_str} a {fecha_fin_str}")
            print(f"Total de envíos: {informe['total_envios']}")
            
            print("\nDistribución por estados:")
            for estado, cantidad in informe['conteo_estados'].items():
                print(f"- {estado}: {cantidad}")
            
            print("\nDistribución por ciudades:")
            for ciudad, cantidad in informe['conteo_ciudades'].items():
                print(f"- {ciudad}: {cantidad}")
            
            print(f"\nEnvíos entregados: {informe['envios_entregados']}")
            if informe['envios_entregados'] > 0:
                print(f"Tiempo promedio de entrega: {informe['tiempo_promedio_entrega_horas']:.2f} horas")
            
            guardar_archivo = input("\n¿Desea guardar este informe en un archivo? (S/N): ").upper()
            if guardar_archivo == 'S':
                nombre_archivo = f"informe_{fecha_inicio_str}_{fecha_fin_str}.txt"
                with open(nombre_archivo, "w", encoding="utf-8") as f:
                    f.write(f"===== INFORME DE ENVÍOS =====\n")
                    f.write(f"Período: {fecha_inicio_str} a {fecha_fin_str}\n")
                    f.write(f"Total de envíos: {informe['total_envios']}\n\n")
                    
                    f.write("Distribución por estados:\n")
                    for estado, cantidad in informe['conteo_estados'].items():
                        f.write(f"- {estado}: {cantidad}\n")
                    
                    f.write("\nDistribución por ciudades:\n")
                    for ciudad, cantidad in informe['conteo_ciudades'].items():
                        f.write(f"- {ciudad}: {cantidad}\n")
                    
                    f.write(f"\nEnvíos entregados: {informe['envios_entregados']}\n")
                    if informe['envios_entregados'] > 0:
                        f.write(f"Tiempo promedio de entrega: {informe['tiempo_promedio_entrega_horas']:.2f} horas\n")
                
                print(f"Informe guardado en el archivo: {nombre_archivo}")
                
        except ValueError as e:
            print(f"Error en el formato de fecha: {e}")
        except Exception as e:
            print(f"Error al generar informe: {e}")
    
    def iniciar(self):
        print("¡Bienvenido al Sistema de Gestión de Envíos!")
        
        while True:
            opcion = self.mostrar_menu_principal()
            
            if opcion == "1":
                self.menu_gestion_clientes()
            elif opcion == "2":
                self.menu_gestion_envios()
            elif opcion == "3":
                self.menu_seguimiento_paquetes()
            elif opcion == "4":
                self.menu_informes()
            elif opcion == "5":
                print("¡Gracias por usar el Sistema de Gestión de Envíos!")
                break
            else:
                print("Opción inválida. Inténtelo de nuevo.")


# Punto de entrada principal
if __name__ == "__main__":
    try:
        interfaz = InterfazConsola()
        interfaz.iniciar()
    except KeyboardInterrupt:
        print("\n\nPrograma terminado por el usuario.")
    except Exception as e:
        print(f"\nError inesperado: {e}")
        import traceback
        traceback.print_exc()