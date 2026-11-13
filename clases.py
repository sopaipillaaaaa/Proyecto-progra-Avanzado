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
        self.__barras = {}
        self.__indice_elementos = {}


    def agregar_elemento(self, elemento):
        """Agrega un elemento al sistema eléctrico."""
        if not isinstance(elemento, ElementoRed):
            raise ValueError("El elemento debe pertenecer a ElementoRed.")
        id_elemento = elemento.id_elemento

        # Verifica duplicados mediante Hash
        if id_elemento in self.__indice_elementos:
            raise ValueError(f"Ya existe un elemento con ID: {id_elemento}")

        # Almacena en la lista general
        self.__elementos.append(elemento)

        # Registra en el diccionario general
        self.__indice_elementos[id_elemento] = elemento

        # Registra en el diccionario de barras
        if isinstance(elemento, Barra):
            self.__barras[id_elemento] = elemento


    def buscar_elemento(self, id_elemento):
        """Busca cualquier elemento utilizando una Tabla Hash.
        Complejidad promedio: O(1).
        """
        return self.__indice_elementos.get(id_elemento)

    def buscar_barra(self, id_barra):
        """Busca una barra mediante su identificador.
        Complejidad promedio: O(1).
        """
        return self.__barras.get(id_barra)




    def eliminar_elemento(self, id_elemento):
        """Elimina un elemento de las estructuras del sistema."""
        elemento = self.buscar_elemento(id_elemento)
        if elemento is None:
            print("No se encontró el elemento.")
            return

        # Elimina de la lista general
        self.__elementos.remove(elemento)

        # Elimina del diccionario general
        del self.__indice_elementos[id_elemento]

        # Si es una barra elimina del diccionario de barras
        if isinstance(elemento, Barra):
            del self.__barras[id_elemento]


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
        """Calcula el balance actual de las potencias de los generadores
        a partir de la generación y demanda total."""
        return self.capacidad_actual_despachada() - self.capacidad_demanda_total()

    def ordenar_generadores_por_costo(self):
        """Obtiene los generadores ordenados por costo creciente."""
        generadores = [elemento for elemento in self.__elementos
            if isinstance(elemento, Generador)]
        return self._mergesort(generadores)

    def _mergesort(self, generadores):
        """Ordena recursivamente una lista de generadores."""
        if len(generadores) <= 1:
            return generadores

        medio = len(generadores) // 2
        izquierda = self._mergesort(generadores[:medio])
        derecha = self._mergesort(generadores[medio:])

        return self._mezclar(izquierda, derecha)

    def _mezclar(self, izquierda, derecha):
        """Combina dos listas previamente ordenadas."""
        resultado = []
        i = 0
        j = 0

        while i < len(izquierda) and j < len(derecha):
            if izquierda[i].get_costo() <= derecha[j].get_costo():
                resultado.append(izquierda[i])
                i += 1
            else:
                resultado.append(derecha[j])
                j += 1

        resultado.extend(izquierda[i:])
        resultado.extend(derecha[j:])
        return resultado

    def despachar_economicamente(self):
        """Realiza el despacho económico por orden de mérito.
        Modelo inicial: costos marginales constantes,
        potencias mínimas cero y sin restricciones de red.
        Returns:
            float: Costo total de generación por hora.
        """
        #Ordena generadores por costo
        generadores = self.ordenar_generadores_por_costo()

        # Verifica las hipótesis del modelo
        for generador in generadores:
            if generador.get_potencia_minima() > 0:
                raise NotImplementedError(
                    "El despacho con mínimos técnicos positivos "
                    "se implementará en una etapa posterior.")

        # Obtiene demanda y capacidad máxima
        demanda = self.capacidad_demanda_total()

        capacidad = sum(g.get_potencia_maxima() for g in generadores)

        # Verifica factibilidad
        if demanda > capacidad:
            raise ValueError(
                "La capacidad máxima no permite "
                "satisfacer la demanda.")

        # Reinicia el despacho anterior
        for generador in generadores:
            generador.set_potencia_despachada(0)

        # Asigna generación por orden de mérito
        demanda_restante = demanda
        for generador in generadores:
            if demanda_restante <= 0:
                break
            potencia = min(generador.get_potencia_maxima(),demanda_restante)
            generador.set_potencia_despachada(potencia)
            demanda_restante -= potencia

        # Calcula el costo operativo total
        costo_total = sum(
            g.get_potencia_despachada() * g.get_costo()
            for g in generadores)

        return costo_total



    def despachar_con_minimos(self, ids_activos):
        """Despacha las unidades seleccionadas respetando
        sus potencias mínimas y máximas.
        """
        generadores = self.ordenar_generadores_por_costo()
        # Valida los identificadores
        ids_activos = list(ids_activos)

        if len(ids_activos) != len(set(ids_activos)):
            raise ValueError("Hay identificadores repetidos.")

        for id_generador in ids_activos:
            elemento = self.buscar_elemento(id_generador)
            if not isinstance(elemento, Generador):
                raise ValueError(f"{id_generador} no es un generador válido.")

        # Obtiene demanda
        demanda = self.capacidad_demanda_total()

        # Calcula despacho sin modificar el sistema
        resultado = self._evaluar_seleccion(generadores, set(ids_activos), demanda)

        if resultado is None:
            raise ValueError(
                "No existe un despacho factible "
                "con los generadores seleccionados.")
        potencias, costo_total = resultado

        # Aplica las potencias calculadas
        for g in generadores:
            g.set_potencia_despachada(
                potencias[g.id_elemento])
        return costo_total


    def seleccionar_generadores_automaticamente(self):
        """Selecciona generadores usando una heurística Greedy.
        Prioriza costos bajos y respeta los mínimos técnicos.
        No garantiza encontrar el óptimo global.
        """
        demanda = self.capacidad_demanda_total()
        if demanda == 0:
            return []
        # Generadores ordenados mediante Mergesort
        generadores = self.ordenar_generadores_por_costo()

        seleccionados = []

        minimo_acumulado = 0.0
        maximo_acumulado = 0.0
        tolerancia = 1e-9

        for generador in generadores:
            p_min = generador.get_potencia_minima()
            p_max = generador.get_potencia_maxima()

            # Ignora generadores sin capacidad
            if p_max == 0:
                continue

            # No incorpora mínimos incompatibles
            if minimo_acumulado + p_min > demanda + tolerancia:
                continue

            # Selecciona generador
            seleccionados.append(generador.id_elemento)

            minimo_acumulado += p_min
            maximo_acumulado += p_max

            # Capacidad suficiente para cubrir demanda
            if maximo_acumulado >= demanda - tolerancia:
                return seleccionados

        raise ValueError(
            "La heurística no encontró un conjunto factible "
            "Podría existir otra combinación de generadores.")


    def _calcular_costo_seleccion(self, generadores, ids_activos, demanda):
        """Calcula el costo de una selección factible."""

        resultado = self._evaluar_seleccion(generadores, ids_activos, demanda)

        if resultado is None:
            return None
        potencias, costo_total = resultado
        return costo_total


    def seleccionar_generadores_mejorado(self):
        """Mejora la selección Greedy mediante intercambios
        Evalúa reemplazos de un generador activo por uno inactivo
        No garantiza el óptimo global.
        """
        demanda = self.capacidad_demanda_total()
        generadores = self.ordenar_generadores_por_costo()

        # Obtiene solución inicial Greedy
        seleccion_inicial = (self.seleccionar_generadores_automaticamente())

        # Si todos los mínimos técnicos son cero,
        # Greedy ya encuentra el óptimo global del modelo básico.
        if all(
            g.get_potencia_minima() == 0
            for g in generadores):
            return seleccion_inicial

        activos = set(seleccion_inicial)

        # Calcula costo inicial
        mejor_costo = self._calcular_costo_seleccion(
            generadores, activos, demanda)

        mejor_seleccion = activos.copy()

        # Prueba intercambios 1 a 1
        for id_saliente in seleccion_inicial:
            for candidato in generadores:
                id_entrante = candidato.id_elemento

                # No intercambia por otro que ya esta activo
                if id_entrante in activos:
                    continue

                # Construye selección alternativa
                nueva_seleccion = activos.copy()
                nueva_seleccion.remove(id_saliente)
                nueva_seleccion.add(id_entrante)

                # Evalua alternativa
                nuevo_costo = self._calcular_costo_seleccion(
                    generadores, nueva_seleccion, demanda)

                # Conserva si mejora el costo
                if nuevo_costo is not None:
                    if nuevo_costo < mejor_costo - 1e-9:
                        mejor_costo = nuevo_costo
                        mejor_seleccion = nueva_seleccion

        # Retorna identificadores ordenados por costo
        return [
            g.id_elemento
            for g in generadores
            if g.id_elemento in mejor_seleccion]


    def _evaluar_seleccion(self, generadores, ids_activos, demanda):
        """Evalúa una selección de generadores.
        Los generadores deben estar ordenados por costo.
        No modifica las potencias del sistema.
        Returns:
            tupla: (diccionario de potencias, costo total).
            None: Si la selección no es factible.
        """
        activos = set(ids_activos)

        # Obtiene los generadores seleccionados
        seleccionados = [
            g for g in generadores
            if g.id_elemento in activos]

        # Calcula restricciones de generación
        minimo_total = sum(
            g.get_potencia_minima()
            for g in seleccionados)

        maximo_total = sum(
            g.get_potencia_maxima()
            for g in seleccionados)

        tolerancia = 1e-9

        # Comprueba factibilidad
        if minimo_total > demanda + tolerancia:
            return None

        if maximo_total < demanda - tolerancia:
            return None

        # Inicializa las potencias propuestas
        potencias = {
            g.id_elemento: 0.0
            for g in generadores}

        restante = max(0.0, demanda - minimo_total)
        costo_total = 0.0

        # Distribuye generación adicional por costo
        for g in seleccionados:
            disponible = (g.get_potencia_maxima() - g.get_potencia_minima())

            adicional = min(disponible, restante)
            potencia = (g.get_potencia_minima() + adicional)
            potencias[g.id_elemento] = potencia
            restante = max(0.0, restante - adicional)
            costo_total += potencia * g.get_costo()

        return potencias, costo_total


 # 2. Clase Hija
class  Generador ( ElementoRed ) :
    """ Representa un generador eléctrico perteneciente al sistema.
    Atributos:
      id (str): Código único del generador.
      potencia_max (float): Potencia máxima que puede entregar el generador.
      costo_operativo (float): Costo asociado a la operación del generador. """

    def __init__ ( self , id_elemento : str , potencia_min : float,
                  potencia_max: float, costo_operativo:float) :
        super() . __init__ ( id_elemento) # Llamada al padre
        if potencia_min < 0 or potencia_max < 0:
            raise ValueError("Las potencias no pueden ser negativas.")
        if potencia_min > potencia_max:
            raise ValueError("La potencia mínima no puede ser mayor a la potencia máxima.")
        if costo_operativo < 0:
            raise ValueError("El costo operativo no puede ser negativo.")

        self.__potencia_min = potencia_min
        self.__potencia_max = potencia_max
        self.__potencia_despachada = 0.0
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
        """Actualiza la potencia despachada del generador."""
        # Permite apagar el generador
        if new == 0:
            self.__potencia_despachada = 0.0
            return

        # Comprueba el límite inferior
        if new < self.__potencia_min:
            raise ValueError("La potencia es menor al mínimo permitido.")

        # Comprobar el límite superior
        if new > self.__potencia_max:
            raise ValueError("La potencia supera el máximo permitido.")
        self.__potencia_despachada = new


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
    """
    Representa una barra eléctrica perteneciente al sistema.
    Atributos: id (str): Código único de la barra.
    """
    def __init__(self, id_elemento: str):
        super().__init__(id_elemento)
        self.__generadores = []
        self.__cargas = []

    def agregar_generador(self, generador):
        """
        Agrega un generador a la barra.
        """
        if not isinstance(generador, Generador):
            raise ValueError("El elemento debe ser un objeto de la clase Generador.")
        self.__generadores.append(generador)

    def agregar_carga(self, carga):
        """
        Agrega una carga a la barra.
        """
        if not isinstance(carga, Carga):
            raise ValueError("El elemento debe ser un objeto de la clase Carga")
        self.__cargas.append(carga)

    def calcular_generacion_total(self):
        """
        Calcula la potencia generada por la barra.
        """
        generacion_total = 0.0
        for generador in self.__generadores:
            generacion_total = generacion_total + generador.get_potencia_despachada()
        return generacion_total

    def calcular_demanda_total(self):
        """
        Calcula la potencia demandada por la barra.
        """
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

# Esta clase probablemente se implemente más adelante en siguientes hitos.
class  Transformador ( ElementoRed ) :
    """ Representa un transformador perteneciente al sistema.
    Atributos: id (str): Código único del transformador. """
    def __init__ ( self , id_elemento : str ) :
        super() . __init__ ( id_elemento ) # Llamada al padre



# PRUEBAS DE FUNCIONAMIENTO
if __name__ == "__main__":
    print("PRUEBAS\n")

    # Se crea sistema eléctrico
    sistema = SistemaPotencia("Sistema_Prueba")
    barra = Barra("B1")

    # Generadores con mínimos técnicos
    g1 = Generador("G1", 45, 45, 10)
    g2 = Generador("G2", 50, 50, 11)
    g3 = Generador("G3", 0, 35, 40)

    # Demanda total: 80 MW
    carga = Carga("C1", 80)

    # Se registran elementos
    for elemento in [barra, g1, g2, g3, carga]:
        sistema.agregar_elemento(elemento)


    # PRUEBA 1: MERGESORT
    ordenados = sistema.ordenar_generadores_por_costo()
    ids = [g.id_elemento for g in ordenados]
    assert ids == ["G1", "G2", "G3"]

    print("1. Mergesort: CORRECTO")
    print("   Orden:", ids)


    # PRUEBA 2: TABLAS HASH
    assert sistema.buscar_barra("B1") is barra
    assert sistema.buscar_elemento("G2") is g2
    assert sistema.buscar_elemento("G99") is None

    # Verifica identificadores duplicados
    try:
        sistema.agregar_elemento(Barra("B1"))
    except ValueError:
        pass
    else:
        raise AssertionError("Se permitió un ID duplicado.")

    print("\n2. Tablas Hash: CORRECTO")
    print("   Búsqueda y validación de IDs exitosas")


    # PRUEBA 3: SELECCIÓN GREEDY
    seleccion_greedy = (sistema.seleccionar_generadores_automaticamente())
    assert seleccion_greedy == ["G1", "G3"]
    costo_greedy = sistema._calcular_costo_seleccion(
        ordenados, set(seleccion_greedy), 80)

    assert abs(costo_greedy - 1850) < 1e-9

    print("\n3. Greedy: CORRECTO")
    print("   Selección:", seleccion_greedy)
    print("   Costo:", costo_greedy, "$/h")


    # PRUEBA 4: BÚSQUEDA LOCAL 1 A 1
    seleccion_mejorada = (sistema.seleccionar_generadores_mejorado())
    assert seleccion_mejorada == ["G2", "G3"]

    # La selección no modifica aún las potencias
    assert sistema.capacidad_actual_despachada() == 0
    costo = sistema.despachar_con_minimos(
        seleccion_mejorada)
    assert abs(costo - 1750) < 1e-9

    print("\n4. Búsqueda local: CORRECTO")
    print("   Selección mejorada:", seleccion_mejorada)
    print("   Nuevo costo:", costo, "$/h")
    print("   Ahorro:", costo_greedy - costo, "$/h")


    # PRUEBA 5: DESPACHO Y FACTIBILIDAD
    assert g1.get_potencia_despachada() == 0
    assert g2.get_potencia_despachada() == 50
    assert g3.get_potencia_despachada() == 30
    assert abs(sistema.balance_actual_potencias()) < 1e-9

    # Guarda despacho antes del escenario inviable
    potencias_antes = [
        g.get_potencia_despachada()
        for g in [g1, g2, g3]]

    # Aumenta demanda a 100 MW
    carga.set_potencia_demandada(100)
    try:
        sistema.despachar_con_minimos(["G2", "G3"])
    except ValueError:
        pass
    else:
        raise AssertionError("No se detectó el despacho inviable.")

    # Comprueba que no se alteró el despacho anterior
    potencias_despues = [
        g.get_potencia_despachada()
        for g in [g1, g2, g3]]
    assert potencias_antes == potencias_despues

    # Restaura demanda original
    carga.set_potencia_demandada(80)
    print("\n5. Despacho y factibilidad: CORRECTO")
    print("   Generación total: 80 MW")
    print("   Demanda total: 80 MW")
    print("   Balance: 0 MW")
    print("   Escenario inviable detectado")
    print("\nTODAS LAS PRUEBAS FUERON EXITOSAS.")
