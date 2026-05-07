from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
from functools import reduce
import math
import random

# ===========================
# 0. JERARQUÍA DE EXCEPCIONES
# ===========================

class ErrorSistemaMusical(Exception):
    """Excepción base del sistema musical."""
    pass

class ErrorValidacion(ErrorSistemaMusical):
    """Datos de entrada inválidos o tipos incorrectos."""
    pass

class ErrorCatalogoVacio(ErrorSistemaMusical):
    """Operación sobre catálogo sin elementos."""
    pass

class ErrorSesionVacia(ErrorSistemaMusical):
    """Operación estadística sobre sesión sin historial."""
    pass

class ErrorEstrategiaNula(ErrorSistemaMusical):
    """Estrategia de búsqueda nula o no configurada."""
    pass

class ErrorCaracteristicaInvalida(ErrorSistemaMusical):
    """Característica musical desconocida o no encontrada."""
    pass


# ==========================================
# 1. MODELO DE DATOS (Jerarquía ItemMusical)
# ==========================================

def _validar_caracteristica_musical(valor: Any, nombre_param: str) -> float:
    """Valida que un valor sea numérico y esté en el rango [0.0, 1.0]."""
    if not isinstance(valor, (int, float)):
        raise ErrorValidacion(
            f"'{nombre_param}' debe ser numérico, recibido: {valor!r} ({type(valor).__name__})"
        )
    valor = float(valor)
    if not (0.0 <= valor <= 1.0):
        raise ErrorValidacion(
            f"'{nombre_param}' debe estar en [0.0, 1.0], recibido: {valor}"
        )
    return valor

class ItemMusical(ABC):
    """Clase abstracta base para los elementos musicales."""
    def __init__(self, id_item: int, nombre: str):
        if not isinstance(id_item, int) or id_item <= 0:
            raise ErrorValidacion(
                f"id_item debe ser un entero positivo, recibido: {id_item!r}"
            )
        if not isinstance(nombre, str) or not nombre.strip():
            raise ErrorValidacion(
                f"nombre debe ser una cadena no vacía, recibido: {nombre!r}"
            )
        self.id_item = id_item
        self.nombre = nombre

    @abstractmethod
    def get_sonoros(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def get_sentimentales(self) -> Dict[str, float]:
        pass

class Cancion(ItemMusical):
    def __init__(self, id_item: int, nombre: str, fecha: datetime,
                 ritmo: float, tono: float, escala: float,
                 felicidad: float, bailabilidad: float, energia: float):
        super().__init__(id_item, nombre)
        if not isinstance(fecha, datetime):
            raise ErrorValidacion(
                f"fecha debe ser datetime, recibido: {type(fecha).__name__}"
            )
        self.fecha = fecha
        self.ritmo = _validar_caracteristica_musical(ritmo, "ritmo")
        self.tono = _validar_caracteristica_musical(tono, "tono")
        self.escala = _validar_caracteristica_musical(escala, "escala")
        self.felicidad = _validar_caracteristica_musical(felicidad, "felicidad")
        self.bailabilidad = _validar_caracteristica_musical(bailabilidad, "bailabilidad")
        self.energia = _validar_caracteristica_musical(energia, "energia")

    def get_sonoros(self) -> Dict[str, float]:
        return {"ritmo": self.ritmo, "tono": self.tono, "escala": self.escala}

    def get_sentimentales(self) -> Dict[str, float]:
        return {"felicidad": self.felicidad, "bailabilidad": self.bailabilidad, "energia": self.energia}

class Artista(ItemMusical):
    def __init__(self, id_item: int, nombre: str, fecha_nacimiento: datetime, canciones: List[Cancion]):
        super().__init__(id_item, nombre)
        if not isinstance(fecha_nacimiento, datetime):
            raise ErrorValidacion(
                f"fecha_nacimiento debe ser datetime, recibido: {type(fecha_nacimiento).__name__}"
            )
        if not isinstance(canciones, list):
            raise ErrorValidacion(
                f"canciones debe ser una lista, recibido: {type(canciones).__name__}"
            )
        self.fecha_nacimiento = fecha_nacimiento
        self.canciones = canciones

    def _promediar_caracteristica(self, caracteristica: str, is_sonoro: bool) -> float:
        # Programación Funcional: Uso de map y reduce para calcular promedios
        if not self.canciones:
            return 0.0
        try:
            extractor = lambda c: c.get_sonoros()[caracteristica] if is_sonoro else c.get_sentimentales()[caracteristica]
            valores = list(map(extractor, self.canciones))
        except KeyError:
            raise ErrorCaracteristicaInvalida(
                f"Característica '{caracteristica}' no existe en las canciones del artista '{self.nombre}'"
            )
        return reduce(lambda x, y: x + y, valores) / len(valores)

    def get_sonoros(self) -> Dict[str, float]:
        return {k: self._promediar_caracteristica(k, True) for k in ["ritmo", "tono", "escala"]}

    def get_sentimentales(self) -> Dict[str, float]:
        return {k: self._promediar_caracteristica(k, False) for k in ["felicidad", "bailabilidad", "energia"]}

class Playlist(ItemMusical):
    def __init__(self, id_item: int, nombre: str, fecha_creacion: datetime, canciones: List[Cancion]):
        super().__init__(id_item, nombre)
        if not isinstance(fecha_creacion, datetime):
            raise ErrorValidacion(
                f"fecha_creacion debe ser datetime, recibido: {type(fecha_creacion).__name__}"
            )
        if not isinstance(canciones, list):
            raise ErrorValidacion(
                f"canciones debe ser una lista, recibido: {type(canciones).__name__}"
            )
        self.fecha_creacion = fecha_creacion
        self.canciones = canciones

    def _promediar_caracteristica(self, caracteristica: str, is_sonoro: bool) -> float:
        if not self.canciones:
            return 0.0
        try:
            extractor = lambda c: c.get_sonoros()[caracteristica] if is_sonoro else c.get_sentimentales()[caracteristica]
            valores = list(map(extractor, self.canciones))
        except KeyError:
            raise ErrorCaracteristicaInvalida(
                f"Característica '{caracteristica}' no existe en las canciones de la playlist '{self.nombre}'"
            )
        return reduce(lambda x, y: x + y, valores) / len(valores)

    def get_sonoros(self) -> Dict[str, float]:
        return {k: self._promediar_caracteristica(k, True) for k in ["ritmo", "tono", "escala"]}

    def get_sentimentales(self) -> Dict[str, float]:
        return {k: self._promediar_caracteristica(k, False) for k in ["felicidad", "bailabilidad", "energia"]}

class SesionEscucha:
    def __init__(self):
        self.historial_canciones: List[Cancion] = []
        self.estadisticas_sonoras: Dict[str, Dict[str, float]] = {}
        self.estadisticas_sentimentales: Dict[str, Dict[str, float]] = {}

    def anadir_cancion(self, cancion: Cancion, fecha_hora: datetime):
        if not isinstance(cancion, Cancion):
            raise ErrorValidacion(
                f"anadir_cancion espera Cancion, recibido: {type(cancion).__name__}"
            )
        self.historial_canciones.append(cancion)


# =======================================================
# 2. PATRÓN CHAIN OF RESPONSIBILITY (Cálculo Estadístico)
# =======================================================

class HandlerEstadisticos(ABC):
    def __init__(self):
        self._siguiente_handler: Optional['HandlerEstadisticos'] = None

    def set_next(self, handler: 'HandlerEstadisticos') -> 'HandlerEstadisticos':
        self._siguiente_handler = handler
        return handler

    @abstractmethod
    def procesar(self, sesion: SesionEscucha) -> None:
        if self._siguiente_handler:
            self._siguiente_handler.procesar(sesion)

def _calcular_med_desv(valores: List[float]) -> Dict[str, float]:
    """Función para calcular media y desviación estándar."""
    if not valores: return {"med": 0.0, "desv": 0.0}
    n = len(valores)
    media = reduce(lambda a, b: a + b, valores) / n
    if n < 2: return {"med": media, "desv": 0.0}

    varianza = reduce(lambda a, b: a + b, map(lambda x: (x - media)**2, valores)) / (n - 1) # Cuasivarianza
    return {"med": media, "desv": math.sqrt(varianza)}

class SonorosHandler(HandlerEstadisticos):
    def procesar(self, sesion: SesionEscucha) -> None:
        if not sesion.historial_canciones:
            raise ErrorSesionVacia(
                "No hay canciones en el historial para calcular estadísticas sonoras."
            )
        caracteristicas = ["ritmo", "tono", "escala"]
        try:
            for feat in caracteristicas:
                valores = list(map(lambda c: c.get_sonoros()[feat], sesion.historial_canciones))
                sesion.estadisticas_sonoras[feat] = _calcular_med_desv(valores)
        except KeyError as e:
            raise ErrorCaracteristicaInvalida(f"Característica sonora no encontrada: {e}")
        super().procesar(sesion)

class SentimentalesHandler(HandlerEstadisticos):
    def procesar(self, sesion: SesionEscucha) -> None:
        if not sesion.historial_canciones:
            raise ErrorSesionVacia(
                "No hay canciones en el historial para calcular estadísticas sentimentales."
            )
        caracteristicas = ["felicidad", "bailabilidad", "energia"]
        try:
            for feat in caracteristicas:
                # Programación Funcional: map para extraer características
                valores = list(map(lambda c: c.get_sentimentales()[feat], sesion.historial_canciones))
                sesion.estadisticas_sentimentales[feat] = _calcular_med_desv(valores)
        except KeyError as e:
            raise ErrorCaracteristicaInvalida(f"Característica sentimental no encontrada: {e}")
        super().procesar(sesion)


# =================================================
# 3. PATRÓN STRATEGY (Algoritmos de Búsqueda)
# =================================================

class EstrategiaBusqueda(ABC):
    @abstractmethod
    def buscar(self, catalogo: List[ItemMusical]) -> List[ItemMusical]:
        pass

class BusquedaAlfabetica(EstrategiaBusqueda):
    def buscar(self, catalogo: List[ItemMusical]) -> List[ItemMusical]:
        if not catalogo:
            raise ErrorCatalogoVacio("No hay elementos en el catálogo para ordenar alfabéticamente.")
        return sorted(catalogo, key=lambda x: x.nombre.lower())

class BusquedaTemporal(EstrategiaBusqueda):
    def buscar(self, catalogo: List[ItemMusical]) -> List[ItemMusical]:
        if not catalogo:
            raise ErrorCatalogoVacio("No hay elementos en el catálogo para ordenar temporalmente.")
        def obtener_fecha(item: ItemMusical) -> datetime:
            if isinstance(item, Cancion): return item.fecha
            if isinstance(item, Artista): return item.fecha_nacimiento
            if isinstance(item, Playlist): return item.fecha_creacion
            return datetime.min

        return sorted(catalogo, key=obtener_fecha, reverse=True)

class BusquedaAleatoria(EstrategiaBusqueda):
    def buscar(self, catalogo: List[ItemMusical]) -> List[ItemMusical]:
        if not catalogo:
            raise ErrorCatalogoVacio("No hay elementos en el catálogo para ordenar aleatoriamente.")
        copia = catalogo.copy()
        random.shuffle(copia)
        return copia


# ==================================================
# 4. PATRÓN OBSERVER (Generación de Recomendaciones)
# ==================================================

class IRecomendador(ABC):
    """Observador abstracto."""
    @abstractmethod
    def actualizar(self, estadisticos: Dict[str, Any], catalogo: List[ItemMusical]) -> List[ItemMusical]:
        pass

class Sujeto(ABC):
    """Sujeto observable abstracto."""
    def __init__(self):
        self._observadores: List[IRecomendador] = []

    def suscribir(self, obs: IRecomendador):
        if obs not in self._observadores:
            self._observadores.append(obs)

    def desuscribir(self, obs: IRecomendador):
        if obs in self._observadores:
            self._observadores.remove(obs)

    def notificar(self, estadisticos: Dict[str, Any], catalogo: List[ItemMusical]):
        for obs in self._observadores:
            obs.actualizar(estadisticos, catalogo)

class RecCanciones(IRecomendador):
    def actualizar(self, estadisticos: Dict[str, Any], catalogo: List[ItemMusical]) -> List[ItemMusical]:
        try:
            canciones = filter(lambda x: isinstance(x, Cancion), catalogo)

            def encaja_perfil(item: ItemMusical) -> bool:
                est_ritmo = estadisticos["sonoras"].get("ritmo")
                if not est_ritmo or est_ritmo["med"] == 0:
                    return True

                ritmo_item = item.get_sonoros()["ritmo"]
                margen_tolerancia = 0.2

                return abs(ritmo_item - est_ritmo["med"]) <= (est_ritmo["desv"] + margen_tolerancia)

            recomendadas = list(filter(encaja_perfil, canciones))
        except KeyError as e:
            raise ErrorCaracteristicaInvalida(
                f"Clave de estadísticos no encontrada en RecCanciones: {e}"
            )
        print(f"RecCanciones generó {len(recomendadas)} recomendaciones basadas en el ritmo.")
        return recomendadas

class RecArtistas(IRecomendador):
    def actualizar(self, estadisticos: Dict[str, Any], catalogo: List[ItemMusical]) -> List[ItemMusical]:
        try:
            artistas = filter(lambda x: isinstance(x, Artista), catalogo)

            def encaja_perfil(item: ItemMusical) -> bool:
                est_energia = estadisticos["sentimentales"].get("energia")
                if not est_energia or est_energia["med"] == 0:
                    return True

                energia_item = item.get_sentimentales()["energia"]
                margen = 0.25

                return abs(energia_item - est_energia["med"]) <= (est_energia["desv"] + margen)

            recomendadas = list(filter(encaja_perfil, artistas))
        except KeyError as e:
            raise ErrorCaracteristicaInvalida(
                f"Clave de estadísticos no encontrada en RecArtistas: {e}"
            )
        print(f"RecArtistas generó {len(recomendadas)} recomendaciones basadas en la energía.")
        return recomendadas

class RecPlaylists(IRecomendador):
    def actualizar(self, estadisticos: Dict[str, Any], catalogo: List[ItemMusical]) -> List[ItemMusical]:
        try:
            playlists = filter(lambda x: isinstance(x, Playlist), catalogo)

            def encaja_perfil(item: ItemMusical) -> bool:
                est_felicidad = estadisticos["sentimentales"].get("felicidad")
                if not est_felicidad or est_felicidad["med"] == 0:
                    return True

                felicidad_item = item.get_sentimentales()["felicidad"]
                margen = 0.2

                return abs(felicidad_item - est_felicidad["med"]) <= (est_felicidad["desv"] + margen)

            recomendadas = list(filter(encaja_perfil, playlists))
        except KeyError as e:
            raise ErrorCaracteristicaInvalida(
                f"Clave de estadísticos no encontrada en RecPlaylists: {e}"
            )
        print(f"RecPlaylists generó {len(recomendadas)} recomendaciones basadas en la felicidad.")
        return recomendadas


# ====================================================
# 5. PATRÓN SINGLETON + CONTEXTO CENTRAL (Recomendador)
# ====================================================

class Recomendador(Sujeto):
    """Punto de entrada del sistema (Singleton) y Sujeto (Observer)."""
    _instancia = None

    def __new__(cls, *args, **kwargs):
        if not cls._instancia:
            cls._instancia = super(Recomendador, cls).__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        super().__init__()  # Inicializa la lista de observadores del Sujeto
        self.catalogo: List[ItemMusical] = []
        self.estrategia_busqueda: EstrategiaBusqueda = BusquedaAlfabetica()
        self.cadena_inicio: HandlerEstadisticos = None

    @classmethod
    def obtener_instancia(cls):
        return cls()

    def set_estrategia(self, estrategia: EstrategiaBusqueda):
        if estrategia is None:
            raise ErrorEstrategiaNula("La estrategia de búsqueda no puede ser None.")
        if not isinstance(estrategia, EstrategiaBusqueda):
            raise ErrorValidacion(
                f"estrategia debe ser EstrategiaBusqueda, recibido: {type(estrategia).__name__}"
            )
        self.estrategia_busqueda = estrategia

    def set_cadena_inicio(self, handler: HandlerEstadisticos):
        self.cadena_inicio = handler

    def ejecutar_busqueda(self) -> List[ItemMusical]:
        if not self.catalogo:
            raise ErrorCatalogoVacio("El catálogo está vacío. Añade elementos antes de buscar.")
        return self.estrategia_busqueda.buscar(self.catalogo)

    def nueva_cancion_escuchada(self, cancion: Cancion, sesion: SesionEscucha):
        if not isinstance(cancion, Cancion):
            raise ErrorValidacion(
                f"Se esperaba Cancion, recibido: {type(cancion).__name__}"
            )
        if not isinstance(sesion, SesionEscucha):
            raise ErrorValidacion(
                f"Se esperaba SesionEscucha, recibido: {type(sesion).__name__}"
            )

        # 1. Añadir la canción al historial de la sesión
        sesion.anadir_cancion(cancion, datetime.now())

        # 2. Iniciar la cadena de Chain of Responsibility para estadísticos
        if self.cadena_inicio:
            self.cadena_inicio.procesar(sesion)

        # 3. Notificar a los observadores (estrategias de recomendación)
        estadisticos_actuales = {
            "sonoras": sesion.estadisticas_sonoras,
            "sentimentales": sesion.estadisticas_sentimentales
        }
        self.notificar(estadisticos_actuales, self.catalogo)

# ==========================================
# 6. SCRIPT DE PRUEBA (Filtros Estadísticos)
# ==========================================

if __name__ == "__main__":
    from datetime import datetime, timedelta

    print("--- INICIANDO SISTEMA DE RECOMENDACIONES (TEST ESTADÍSTICO) ---\n")
    hoy = datetime.now()

    # --- BLOQUE DE PRUEBAS DE EXCEPCIONES ---
    print("=" * 55)
    print("  PRUEBAS DE GESTIÓN DE EXCEPCIONES")
    print("=" * 55 + "\n")

    print("[TEST 1] Canción con ritmo fuera de rango (1.5):")
    try:
        mala_cancion = Cancion(99, "Inválida", hoy, ritmo=1.5, tono=0.5, escala=0.5,
                               felicidad=0.5, bailabilidad=0.5, energia=0.5)
    except ErrorValidacion as e:
        print(f"  [CAPTURADO] ErrorValidacion: {e}\n")

    print("[TEST 2] ItemMusical con id negativo:")
    try:
        mala_cancion2 = Cancion(-5, "Negativa", hoy, ritmo=0.5, tono=0.5, escala=0.5,
                                felicidad=0.5, bailabilidad=0.5, energia=0.5)
    except ErrorValidacion as e:
        print(f"  [CAPTURADO] ErrorValidacion: {e}\n")

    print("[TEST 3] Estrategia nula en Recomendador:")
    try:
        r_test = Recomendador.obtener_instancia()
        r_test.set_estrategia(None)
    except ErrorEstrategiaNula as e:
        print(f"  [CAPTURADO] ErrorEstrategiaNula: {e}\n")

    print("[TEST 4] Búsqueda con catálogo vacío:")
    try:
        r_test2 = Recomendador.obtener_instancia()
        r_test2.catalogo = []
        r_test2.ejecutar_busqueda()
    except ErrorCatalogoVacio as e:
        print(f"  [CAPTURADO] ErrorCatalogoVacio: {e}\n")

    print("[TEST 5] Pasar tipo incorrecto a nueva_cancion_escuchada:")
    try:
        sesion_test = SesionEscucha()
        r_test3 = Recomendador.obtener_instancia()
        r_test3.nueva_cancion_escuchada("esto_no_es_cancion", sesion_test)
    except ErrorValidacion as e:
        print(f"  [CAPTURADO] ErrorValidacion: {e}\n")

    print("=" * 55)
    print("  FIN DE PRUEBAS — TODAS LAS EXCEPCIONES CAPTURADAS")
    print("=" * 55 + "\n")

    # --- FLUJO NORMAL ---
    try:
        print("--- FLUJO NORMAL DEL SISTEMA ---\n")

        # 1. Canciones que el usuario va a escuchar (Perfil: Upbeat, Enérgico, Feliz)
        h1 = Cancion(1, "Historial 1 (Fiesta)", hoy, ritmo=0.8, tono=0.5, escala=0.5, felicidad=0.8, bailabilidad=0.8, energia=0.9)
        h2 = Cancion(2, "Historial 2 (Subidón)", hoy, ritmo=0.7, tono=0.5, escala=0.5, felicidad=0.9, bailabilidad=0.8, energia=0.8)

        # 2. Catálogo: Canciones a evaluar (Filtro por Ritmo ~0.75)
        c_match = Cancion(3, "Canción Ideal (Ritmo 0.75)", hoy, ritmo=0.75, tono=0.5, escala=0.5, felicidad=0.5, bailabilidad=0.5, energia=0.5)
        c_fail = Cancion(4, "Canción Lenta (Ritmo 0.2)", hoy, ritmo=0.2, tono=0.5, escala=0.5, felicidad=0.5, bailabilidad=0.5, energia=0.5)

        # 3. Catálogo: Canciones base para Artistas (Filtro por Energía ~0.85)
        c_energia_alta = Cancion(5, "Track Energía Alta", hoy, ritmo=0.5, tono=0.5, escala=0.5, felicidad=0.5, bailabilidad=0.5, energia=0.85)
        c_energia_baja = Cancion(6, "Track Acústico", hoy, ritmo=0.5, tono=0.5, escala=0.5, felicidad=0.5, bailabilidad=0.5, energia=0.2)

        # 4. Catálogo: Canciones base para Playlists (Filtro por Felicidad ~0.85)
        c_feliz = Cancion(7, "Track Feliz", hoy, ritmo=0.5, tono=0.5, escala=0.5, felicidad=0.85, bailabilidad=0.5, energia=0.5)
        c_triste = Cancion(8, "Track Triste", hoy, ritmo=0.5, tono=0.5, escala=0.5, felicidad=0.1, bailabilidad=0.5, energia=0.5)

        # Creación de Artistas y Playlists en base a las canciones anteriores
        a_match = Artista(101, "DJ Enérgico", hoy, [c_energia_alta])
        a_fail = Artista(102, "Cantautor Melancólico", hoy, [c_energia_baja])

        p_match = Playlist(201, "Good Vibes Playlist", hoy, [c_feliz])
        p_fail = Playlist(202, "Lluvia y Tristeza Playlist", hoy, [c_triste])

        # 5. Configuración del Sistema
        recomendador = Recomendador.obtener_instancia()
        recomendador.catalogo = [c_match, c_fail, a_match, a_fail, p_match, p_fail]

        # Cadena de responsabilidad (Cálculo matemático)
        handler_sonoro = SonorosHandler()
        handler_sentimental = SentimentalesHandler()
        handler_sonoro.set_next(handler_sentimental)
        recomendador.set_cadena_inicio(handler_sonoro)

        # Observadores (Nuestros generadores de recomendaciones)
        rec_canciones = RecCanciones()
        rec_artistas = RecArtistas()
        rec_playlists = RecPlaylists()

        recomendador.suscribir(rec_canciones)
        recomendador.suscribir(rec_artistas)
        recomendador.suscribir(rec_playlists)

        # 6. Simulamos la sesión
        sesion_usuario = SesionEscucha()
        print("Usuario escuchando 'Historial 1 (Fiesta)'...")
        recomendador.nueva_cancion_escuchada(h1, sesion_usuario)

        print("Usuario escuchando 'Historial 2 (Subidón)'...")
        recomendador.nueva_cancion_escuchada(h2, sesion_usuario)

        # 7. Mostramos el perfil calculado en la sesión
        print("\n--- PERFIL ESTADÍSTICO DEL USUARIO ---")
        est_ritmo = sesion_usuario.estadisticas_sonoras['ritmo']
        est_energia = sesion_usuario.estadisticas_sentimentales['energia']
        est_felicidad = sesion_usuario.estadisticas_sentimentales['felicidad']

        print(f"Ritmo promedio: {est_ritmo['med']:.2f} (Desv: {est_ritmo['desv']:.2f})")
        print(f"Energía promedio: {est_energia['med']:.2f} (Desv: {est_energia['desv']:.2f})")
        print(f"Felicidad promedio: {est_felicidad['med']:.2f} (Desv: {est_felicidad['desv']:.2f})")

        # 8. Extraemos e imprimimos los resultados filtrados
        print("\n--- RESULTADOS DE LAS RECOMENDACIONES ---")
        estadisticos_actuales = {
            "sonoras": sesion_usuario.estadisticas_sonoras,
            "sentimentales": sesion_usuario.estadisticas_sentimentales
        }

        # Comprobamos las Canciones (Filtro: Ritmo)
        print("\n CANCIONES RECOMENDADAS (Basado en Ritmo):")
        resultado_canciones = rec_canciones.actualizar(estadisticos_actuales, recomendador.catalogo)
        for item in resultado_canciones:
            print(f" -> {item.nombre} (Ritmo: {item.get_sonoros()['ritmo']})")

        # Comprobamos los Artistas (Filtro: Energía)
        print("\n ARTISTAS RECOMENDADOS (Basado en Energía):")
        resultado_artistas = rec_artistas.actualizar(estadisticos_actuales, recomendador.catalogo)
        for item in resultado_artistas:
            print(f" -> {item.nombre} (Energía: {item.get_sentimentales()['energia']:.2f})")

        # Comprobamos las Playlists (Filtro: Felicidad)
        print("\n PLAYLISTS RECOMENDADAS (Basado en Felicidad):")
        resultado_playlists = rec_playlists.actualizar(estadisticos_actuales, recomendador.catalogo)
        for item in resultado_playlists:
            print(f" -> {item.nombre} (Felicidad: {item.get_sentimentales()['felicidad']:.2f})")

    except ErrorSesionVacia as e:
        print(f"[ERROR] Sesión sin historial: {e}")
    except ErrorCatalogoVacio as e:
        print(f"[ERROR] Catálogo vacío: {e}")
    except ErrorCaracteristicaInvalida as e:
        print(f"[ERROR] Característica inválida: {e}")
    except ErrorValidacion as e:
        print(f"[ERROR] Dato inválido: {e}")
    except ErrorSistemaMusical as e:
        print(f"[ERROR] Error del sistema musical: {e}")
    except Exception as e:
        print(f"[ERROR INESPERADO] {type(e).__name__}: {e}")
