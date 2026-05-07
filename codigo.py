from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime
from functools import reduce
import math
import random

# ==========================================
# 1. MODELO DE DATOS (Jerarquía ItemMusical)
# ==========================================

class ItemMusical(ABC):
    """Clase abstracta base para los elementos musicales."""
    def __init__(self, id_item: int, nombre: str):
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
        self.fecha = fecha
        self.ritmo = ritmo
        self.tono = tono
        self.escala = escala
        self.felicidad = felicidad
        self.bailabilidad = bailabilidad
        self.energia = energia

    def get_sonoros(self) -> Dict[str, float]:
        return {"ritmo": self.ritmo, "tono": self.tono, "escala": self.escala}

    def get_sentimentales(self) -> Dict[str, float]:
        return {"felicidad": self.felicidad, "bailabilidad": self.bailabilidad, "energia": self.energia}

class Artista(ItemMusical):
    def __init__(self, id_item: int, nombre: str, fecha_nacimiento: datetime, canciones: List[Cancion]):
        super().__init__(id_item, nombre)
        self.fecha_nacimiento = fecha_nacimiento
        self.canciones = canciones

    def _promediar_caracteristica(self, caracteristica: str, is_sonoro: bool) -> float:
        # Programación Funcional: Uso de map y reduce para calcular promedios
        if not self.canciones:
            return 0.0
        
        extractor = lambda c: c.get_sonoros()[caracteristica] if is_sonoro else c.get_sentimentales()[caracteristica]
        valores = list(map(extractor, self.canciones))
        return reduce(lambda x, y: x + y, valores) / len(valores)

    def get_sonoros(self) -> Dict[str, float]:
        return {k: self._promediar_caracteristica(k, True) for k in ["ritmo", "tono", "escala"]}

    def get_sentimentales(self) -> Dict[str, float]:
        return {k: self._promediar_caracteristica(k, False) for k in ["felicidad", "bailabilidad", "energia"]}

class Playlist(ItemMusical):
    def __init__(self, id_item: int, nombre: str, fecha_creacion: datetime, canciones: List[Cancion]):
        super().__init__(id_item, nombre)
        self.fecha_creacion = fecha_creacion
        self.canciones = canciones

    def _promediar_caracteristica(self, caracteristica: str, is_sonoro: bool) -> float:
        if not self.canciones: return 0.0
        extractor = lambda c: c.get_sonoros()[caracteristica] if is_sonoro else c.get_sentimentales()[caracteristica]
        valores = list(map(extractor, self.canciones))
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
        caracteristicas = ["ritmo", "tono", "escala"]
        for feat in caracteristicas:
            valores = list(map(lambda c: c.get_sonoros()[feat], sesion.historial_canciones))
            sesion.estadisticas_sonoras[feat] = _calcular_med_desv(valores)
        super().procesar(sesion)

class SentimentalesHandler(HandlerEstadisticos):
    def procesar(self, sesion: SesionEscucha) -> None:
        caracteristicas = ["felicidad", "bailabilidad", "energia"]
        for feat in caracteristicas:
            # Programación Funcional: map para extraer características
            valores = list(map(lambda c: c.get_sentimentales()[feat], sesion.historial_canciones))
            sesion.estadisticas_sentimentales[feat] = _calcular_med_desv(valores)
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
        return sorted(catalogo, key=lambda x: x.nombre.lower())

class BusquedaTemporal(EstrategiaBusqueda):
    def buscar(self, catalogo: List[ItemMusical]) -> List[ItemMusical]:
        def obtener_fecha(item: ItemMusical) -> datetime:
            if isinstance(item, Cancion): return item.fecha
            if isinstance(item, Artista): return item.fecha_nacimiento
            if isinstance(item, Playlist): return item.fecha_creacion
            return datetime.min
        
        return sorted(catalogo, key=obtener_fecha, reverse=True)

class BusquedaAleatoria(EstrategiaBusqueda):
    def buscar(self, catalogo: List[ItemMusical]) -> List[ItemMusical]:
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
        canciones = filter(lambda x: isinstance(x, Cancion), catalogo)

        def encaja_perfil(item: ItemMusical) -> bool:
            est_ritmo = estadisticos["sonoras"].get("ritmo")
            if not est_ritmo or est_ritmo["med"] == 0: 
                return True 
                
            ritmo_item = item.get_sonoros()["ritmo"]
            margen_tolerancia = 0.2
            
            return abs(ritmo_item - est_ritmo["med"]) <= (est_ritmo["desv"] + margen_tolerancia)

        recomendadas = list(filter(encaja_perfil, canciones))
        print(f"RecCanciones generó {len(recomendadas)} recomendaciones basadas en el ritmo.")
        return recomendadas

class RecArtistas(IRecomendador):
    def actualizar(self, estadisticos: Dict[str, Any], catalogo: List[ItemMusical]) -> List[ItemMusical]:
        artistas = filter(lambda x: isinstance(x, Artista), catalogo)
        
        def encaja_perfil(item: ItemMusical) -> bool:
            est_energia = estadisticos["sentimentales"].get("energia")
            if not est_energia or est_energia["med"] == 0:
                return True
                
            energia_item = item.get_sentimentales()["energia"]
            margen = 0.25
            
            return abs(energia_item - est_energia["med"]) <= (est_energia["desv"] + margen)

        recomendadas = list(filter(encaja_perfil, artistas))
        print(f"RecArtistas generó {len(recomendadas)} recomendaciones basadas en la energía.")
        return recomendadas

class RecPlaylists(IRecomendador):
    def actualizar(self, estadisticos: Dict[str, Any], catalogo: List[ItemMusical]) -> List[ItemMusical]:
        playlists = filter(lambda x: isinstance(x, Playlist), catalogo)
        
        def encaja_perfil(item: ItemMusical) -> bool:
            est_felicidad = estadisticos["sentimentales"].get("felicidad")
            if not est_felicidad or est_felicidad["med"] == 0:
                return True
                
            felicidad_item = item.get_sentimentales()["felicidad"]
            margen = 0.2
            
            return abs(felicidad_item - est_felicidad["med"]) <= (est_felicidad["desv"] + margen)

        recomendadas = list(filter(encaja_perfil, playlists))
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
        self.estrategia_busqueda = estrategia

    def set_cadena_inicio(self, handler: HandlerEstadisticos):
        self.cadena_inicio = handler

    def ejecutar_busqueda(self) -> List[ItemMusical]:
        return self.estrategia_busqueda.buscar(self.catalogo)

    def nueva_cancion_escuchada(self, cancion: Cancion, sesion: SesionEscucha):
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