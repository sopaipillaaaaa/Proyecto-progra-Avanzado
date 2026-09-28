# 1. Clase Padre
class ElementoRed :

    """ Representa un elemento general de la red eléctrica.
    Atributos: id (str): Código único que identifica al elemento. """

    def __init__ ( self, id_elemento) :
        self.id_elemento = id_elemento

class SistemaPotencia:
    """ Representa y administra un sistema eléctrico de potencia.
      Atributos: id (str): Código único que identifica al sistema. """
    def __init__ (self, id_sistema) :
        self.id_sistema = id_sistema
        self.__elementos = []


    def agregar_elemento(self, elemento):
        """Agrega elemento al sistema"""
        # Cualquier objeto agregado debe pertenecer a la familia de clases definidas
        # como lo son (Generador, Carga, LineaDeTransmision, Barra)
        if not isinstance(elemento, ElementoRed):
            raise ValueError("El elemento debe ser un objeto de la clase ElementoRed.")
        for objeto in self.__elementos:
            if objeto == elemento:
                raise ValueError(f'Ya existe un elemento con ID: {elemento.id_elemento}')
        self.__elementos.append(elemento)

    def buscar_elemento(self, elemento):
        """Busca un elemento en el sistema"""
        for elemento in self.__elementos:
            if elemento.id_elemento == elemento:
                return elemento
        return None

    def eliminar_elemento(self, id_elemento: str):
        """Elimina un elemento del sistema"""
        for elemento in self.__elementos:
            if elemento.id_elemento == id_elemento:
                self.__elementos.remove(elemento)
                return
        print("No se encontro elemento")

    def get_elemento(self):
        return self.__elementos.copy()

    def capacidad_demanda_total(self):
        """Calcula la demanda total, o potencia total que consumen las cargas."""
        demanda_total = 0.0
        for elemento in self.__elementos:
            if isinstance(elemento, Carga):
                demanda_total = demanda_total + elemento.get_potencia_demandada()
        return demanda_total

    def capacidad_maxima_total_generadores(self):
        """Calcula la potencia máxima que pueden suministrar entre todos los generadores"""
        capacidad_maxima_total = 0.0
        for generadores in self.__elementos:
            if isinstance(generadores, Generador):
                capacidad_maxima_total += generadores.get_potencia_maxima()
        return capacidad_maxima_total

    def capacidad_actual_despachada(self):
        """Capacidad actual de despacho considerando todos los generadores."""
        capacidad_actual_despachada = 0.0
        for actual in self.__elementos:
            if isinstance(actual, Generador):
                capacidad_actual_despachada += actual.get_potencia_despachada()
        return capacidad_actual_despachada

    def satisfacer_demanda(self):
        """
        Se verifica que la potencia máxima sea mayor o igual a la demanda para
        poder satisfacerla.
        """
        if self.capacidad_maxima_total_generadores() >= self.capacidad_demanda_total():
            print("Si se puede satisfacer la demanda con los generadores existentes")
            return True
        else:
            print("No se puede satisfacer la demanda de las cargas.")
            return False

    def balance_actual_potencias(self):
        return self.capacidad_actual_despachada() - self.capacidad_demanda_total()

 # 2. Clase Hija
class  Generador ( ElementoRed ) :
    """ Representa un generador eléctrico perteneciente al sistema.
    Atributos:
      id (str): Código único del generador.
      potencia_max (float): Potencia máxima que puede entregar el generador.
      costo_operativo (float): Costo asociado a la operación del generador. """

    def __init__ ( self , id_elemento : str , potencia_min : float,
                  potencia_max: float, costo_operativo:float) :   #Acá realicé cambios.
        super() . __init__ ( id_elemento) # Llamada al padre
        if potencia_min < 0 or potencia_max < 0:
            raise ValueError("Las potencias no pueden ser negativas.")
        if potencia_min > potencia_max:
            raise ValueError("La potencia mínima no puede ser mayor a la potencia máxima.")
        if costo_operativo < 0:
            raise ValueError("El costo operativo no puede ser negativo.")

        self.__potencia_min = potencia_min  # Se añadió potencia mínima.
        self.__potencia_max = potencia_max
        self.__potencia_despachada = 0.0   # Se añadió potencia generada o despachada.
        self.__costo_operativo = costo_operativo

    def get_potencia_maxima(self) -> float:
        """ Entrega la potencia máxima del generador.
            Returns: float: Potencia máxima del generador. """
        return self.__potencia_max

    def get_potencia_minima(self) -> float:
        """ Entrega la potencia mínima del generador.
            Returns: Potencia mínima del generador. """
        return self.__potencia_min


    def get_potencia_despachada(self) -> float:
        """ Entrega la potencia actual del generador.
            Returns: Potencia actual del generador. """
        return self.__potencia_despachada


    def set_potencia_despachada(self, new):
        """ Modifica la potencia despachada del generador."""
        if new == 0:
            self.potencia_despachada = 0.0   # El generador está apagado.

        if self.__potencia_min <= new <= self.__potencia_max:
            self.__potencia_despachada = new

        elif new < self.__potencia_min:
            raise ValueError("La potencia despachada es menor al límite inferior del generador.")

        else:
            raise ValueError("La potencia despachada es mayor al límite superior del generador")


    def get_costo(self):
            """ Entrega el costo operativo.
                Returns: float: costo operativo del generador. """
            return self.__costo_operativo


    def set_costo(self,new):
            """ Modifica el costo operativo del generador."""
            if new >= 0:
                self.__costo_operativo = new
            else:
                raise ValueError("El costo debe ser positivo")


class  Carga ( ElementoRed ) :
    """ Representa una carga eléctrica perteneciente al sistema.
    Atributos: id (str): Código único de la carga. """
    def __init__ ( self , id_elemento : str, potencia_demandada: float) :
        super().__init__( id_elemento ) # Llamada al padre
        if potencia_demandada < 0:
            raise ValueError("La potencia demandada no puede ser negativa.")
        self.__potencia_demandada = potencia_demandada

    def get_potencia_demandada(self):
        """
        Entrega potencia demandada.
        Returns: float: Potencia demandada.
        """
        return self.__potencia_demandada

    def set_potencia_demandada(self, potencia):
        """
        Modifica la potencia demandada.
        Args: potencia (float): potencia demandada
        """
        if potencia >= 0:
            self.__potencia_demandada = potencia
        else:
            raise ValueError("La potencia demandada no puede ser negativa.")

class Barra(ElementoRed):
    def __init__(self, id_elemento: str):
        super().__init__(id_elemento)
        self.__generadores = []
        self.__cargas = []

    def agregar_generador(self, generador):
        if not isinstance(generador, Generador):
            raise ValueError("El elemento debe ser un objeto de la clase Generador.")
        self.__generadores.append(generador)

    def agregar_carga(self, carga):
        if not isinstance(carga, Carga):
            raise ValueError("El elemento debe ser un objeto de la clase Carga")
        self.__cargas.append(carga)

    def calcular_generacion_total(self):
        generacion_total = 0.0
        for generador in self.__generadores:
            generacion_total = generacion_total + generador.get_potencia_despachada()
        return generacion_total

    def calcular_demanda_total(self):
        demanda_total = 0.0
        for carga in self.__cargas:
            demanda_total = demanda_total + carga.get_potencia_demandada()
        return demanda_total

    def calcular_potencia_neta(self):
        """
        Calcula la potencia neta inyectada a la barra (potencia generada - potencia demandada)
        """
        return self.calcular_generacion_total() - self.calcular_demanda_total()




class  LineaDeTransmision ( ElementoRed ) :
    """ Representa una línea de transmisión perteneciente al sistema.
    Atributos:
    id (str): Código único de la línea de transmisión.
    barra_origen (Barra): Barra de origen de la línea de transmisión.
    barra_destino (Barra): Barra de destino de la línea de transmisión.
    reactancia (float): Reactancia de la línea de transmisión.
    """
    def __init__ ( self , id_elemento : str, barra_origen: str, barra_destino: str, reactancia: float) :
        super().__init__( id_elemento ) # Llamada al padre
        if not isinstance(barra_origen, Barra):
            raise ValueError("La barra de origen debe ser un objeto de tipo Barra.")
        if not isinstance(barra_destino, Barra):
            raise ValueError("La barra de destino debe ser un objeto de tipo Barra.")
        if barra_origen is barra_destino:
            raise ValueError("Las barras deben estar separadas por una línea de transmisión.")
        if reactancia < 0:
            raise ValueError("La reactancia debe ser positiva.")
        if reactancia == 0:
            raise ValueError("La reactancia no puede ser cero dado que las barras serían iguales.")

        self.__barra_origen = barra_origen
        self.__barra_destino = barra_destino
        self.__reactancia = reactancia

    def get_barra_origen(self):
        return self.__barra_origen

    def get_barra_destino(self):
        return self.__barra_destino

    def get_reactancia(self):
        return self.__reactancia

    def calcular_susceptancia(self):
        """
        Calcula la susceptancia de la línea de transmisión.
        """
        return 1 / self.__reactancia

class  Transformador ( ElementoRed ) :
    """ Representa un transformador perteneciente al sistema.
    Atributos: id (str): Código único del transformador. """
    def __init__ ( self , id_elemento : str ) :
        super() . __init__ ( id_elemento ) # Llamada al padre
