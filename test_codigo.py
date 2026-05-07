import pytest
from datetime import datetime
from codigo import (
    ErrorSistemaMusical, ErrorValidacion, ErrorCatalogoVacio,
    ErrorSesionVacia, ErrorEstrategiaNula, ErrorCaracteristicaInvalida,
    Cancion, Artista, Playlist, SesionEscucha,
    SonorosHandler, SentimentalesHandler,
    BusquedaAlfabetica, BusquedaTemporal, BusquedaAleatoria,
    Recomendador, RecCanciones, RecArtistas, RecPlaylists,
)

HOY = datetime(2024, 6, 15, 12, 0, 0)


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reinicia el Singleton Recomendador entre pruebas para aislar el estado."""
    Recomendador._instancia = None
    yield
    Recomendador._instancia = None


@pytest.fixture
def cancion_valida():
    return Cancion(1, "Cancion Test", HOY,
                   ritmo=0.5, tono=0.5, escala=0.5,
                   felicidad=0.5, bailabilidad=0.5, energia=0.5)


@pytest.fixture
def sesion_con_cancion(cancion_valida):
    sesion = SesionEscucha()
    sesion.historial_canciones.append(cancion_valida)
    return sesion


# -------------------------------------------------------
# Jerarquía de excepciones
# -------------------------------------------------------

class TestJerarquiaExcepciones:
    def test_error_validacion_hereda_de_sistema_musical(self):
        assert issubclass(ErrorValidacion, ErrorSistemaMusical)

    def test_error_catalogo_vacio_hereda_de_sistema_musical(self):
        assert issubclass(ErrorCatalogoVacio, ErrorSistemaMusical)

    def test_error_sesion_vacia_hereda_de_sistema_musical(self):
        assert issubclass(ErrorSesionVacia, ErrorSistemaMusical)

    def test_error_estrategia_nula_hereda_de_sistema_musical(self):
        assert issubclass(ErrorEstrategiaNula, ErrorSistemaMusical)

    def test_error_caracteristica_invalida_hereda_de_sistema_musical(self):
        assert issubclass(ErrorCaracteristicaInvalida, ErrorSistemaMusical)

    def test_todas_son_exception(self):
        for cls in (ErrorSistemaMusical, ErrorValidacion, ErrorCatalogoVacio,
                    ErrorSesionVacia, ErrorEstrategiaNula, ErrorCaracteristicaInvalida):
            assert issubclass(cls, Exception)


# -------------------------------------------------------
# ErrorValidacion — ItemMusical (id y nombre)
# -------------------------------------------------------

class TestItemMusicalValidacion:
    def test_id_negativo_lanza_error(self):
        with pytest.raises(ErrorValidacion, match="id_item"):
            Cancion(-1, "Nombre", HOY, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)

    def test_id_cero_lanza_error(self):
        with pytest.raises(ErrorValidacion, match="id_item"):
            Cancion(0, "Nombre", HOY, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)

    def test_id_float_lanza_error(self):
        with pytest.raises(ErrorValidacion, match="id_item"):
            Cancion(1.5, "Nombre", HOY, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)

    def test_nombre_vacio_lanza_error(self):
        with pytest.raises(ErrorValidacion, match="nombre"):
            Cancion(1, "", HOY, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)

    def test_nombre_solo_espacios_lanza_error(self):
        with pytest.raises(ErrorValidacion, match="nombre"):
            Cancion(1, "   ", HOY, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)

    def test_nombre_none_lanza_error(self):
        with pytest.raises(ErrorValidacion, match="nombre"):
            Cancion(1, None, HOY, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)


# -------------------------------------------------------
# ErrorValidacion — Cancion (características y fecha)
# -------------------------------------------------------

class TestCancionValidacion:
    BASE = dict(ritmo=0.5, tono=0.5, escala=0.5,
                felicidad=0.5, bailabilidad=0.5, energia=0.5)

    @pytest.mark.parametrize("campo,valor_malo", [
        ("ritmo",        1.5),
        ("tono",        -0.1),
        ("escala",       2.0),
        ("felicidad",   -1.0),
        ("bailabilidad", 1.1),
        ("energia",     99.0),
    ])
    def test_caracteristica_fuera_de_rango(self, campo, valor_malo):
        kwargs = {**self.BASE, campo: valor_malo}
        with pytest.raises(ErrorValidacion, match=campo):
            Cancion(1, "X", HOY, **kwargs)

    @pytest.mark.parametrize("campo,valor_malo", [
        ("ritmo",     "alto"),
        ("energia",   [0.5]),
        ("felicidad", None),
    ])
    def test_caracteristica_tipo_incorrecto(self, campo, valor_malo):
        kwargs = {**self.BASE, campo: valor_malo}
        with pytest.raises(ErrorValidacion, match=campo):
            Cancion(1, "X", HOY, **kwargs)

    def test_fecha_string_lanza_error(self):
        with pytest.raises(ErrorValidacion, match="fecha"):
            Cancion(1, "X", "2024-01-01", **self.BASE)

    def test_fecha_none_lanza_error(self):
        with pytest.raises(ErrorValidacion, match="fecha"):
            Cancion(1, "X", None, **self.BASE)

    def test_limites_exactos_no_lanzan_error(self):
        c = Cancion(1, "Límites", HOY, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
        assert c.ritmo == 0.0
        assert c.tono == 1.0


# -------------------------------------------------------
# ErrorValidacion — Artista y Playlist
# -------------------------------------------------------

class TestArtistaValidacion:
    def test_fecha_nacimiento_invalida(self):
        with pytest.raises(ErrorValidacion, match="fecha_nacimiento"):
            Artista(1, "DJ", "no-fecha", [])

    def test_fecha_nacimiento_none(self):
        with pytest.raises(ErrorValidacion, match="fecha_nacimiento"):
            Artista(1, "DJ", None, [])

    def test_canciones_no_lista(self):
        with pytest.raises(ErrorValidacion, match="canciones"):
            Artista(1, "DJ", HOY, "no-lista")

    def test_canciones_none(self):
        with pytest.raises(ErrorValidacion, match="canciones"):
            Artista(1, "DJ", HOY, None)

    def test_id_negativo_hereda_validacion(self):
        with pytest.raises(ErrorValidacion, match="id_item"):
            Artista(-1, "DJ", HOY, [])


class TestPlaylistValidacion:
    def test_fecha_creacion_invalida(self):
        with pytest.raises(ErrorValidacion, match="fecha_creacion"):
            Playlist(1, "Mix", "no-fecha", [])

    def test_fecha_creacion_none(self):
        with pytest.raises(ErrorValidacion, match="fecha_creacion"):
            Playlist(1, "Mix", None, [])

    def test_canciones_no_lista(self):
        with pytest.raises(ErrorValidacion, match="canciones"):
            Playlist(1, "Mix", HOY, 42)

    def test_nombre_vacio_hereda_validacion(self):
        with pytest.raises(ErrorValidacion, match="nombre"):
            Playlist(1, "", HOY, [])


# -------------------------------------------------------
# ErrorCaracteristicaInvalida
# -------------------------------------------------------

class TestCaracteristicaInvalida:
    def test_artista_caracteristica_sonora_inexistente(self, cancion_valida):
        artista = Artista(1, "DJ", HOY, [cancion_valida])
        with pytest.raises(ErrorCaracteristicaInvalida, match="inexistente"):
            artista._promediar_caracteristica("inexistente", True)

    def test_artista_caracteristica_sentimental_inexistente(self, cancion_valida):
        artista = Artista(1, "DJ", HOY, [cancion_valida])
        with pytest.raises(ErrorCaracteristicaInvalida, match="tempo"):
            artista._promediar_caracteristica("tempo", False)

    def test_playlist_caracteristica_inexistente(self, cancion_valida):
        pl = Playlist(1, "Mix", HOY, [cancion_valida])
        with pytest.raises(ErrorCaracteristicaInvalida):
            pl._promediar_caracteristica("inexistente", False)

    def test_artista_sin_canciones_devuelve_cero(self):
        artista = Artista(1, "DJ", HOY, [])
        assert artista._promediar_caracteristica("ritmo", True) == 0.0


# -------------------------------------------------------
# ErrorSesionVacia
# -------------------------------------------------------

class TestSesionVacia:
    def test_sonoros_handler_sesion_vacia(self):
        with pytest.raises(ErrorSesionVacia):
            SonorosHandler().procesar(SesionEscucha())

    def test_sentimentales_handler_sesion_vacia(self):
        with pytest.raises(ErrorSesionVacia):
            SentimentalesHandler().procesar(SesionEscucha())

    def test_sesion_vacia_es_sistema_musical(self):
        with pytest.raises(ErrorSistemaMusical):
            SonorosHandler().procesar(SesionEscucha())


# -------------------------------------------------------
# ErrorCatalogoVacio
# -------------------------------------------------------

class TestCatalogoVacio:
    def test_busqueda_alfabetica_catalogo_vacio(self):
        with pytest.raises(ErrorCatalogoVacio):
            BusquedaAlfabetica().buscar([])

    def test_busqueda_temporal_catalogo_vacio(self):
        with pytest.raises(ErrorCatalogoVacio):
            BusquedaTemporal().buscar([])

    def test_busqueda_aleatoria_catalogo_vacio(self):
        with pytest.raises(ErrorCatalogoVacio):
            BusquedaAleatoria().buscar([])

    def test_recomendador_ejecutar_busqueda_catalogo_vacio(self):
        rec = Recomendador.obtener_instancia()
        rec.catalogo = []
        with pytest.raises(ErrorCatalogoVacio):
            rec.ejecutar_busqueda()


# -------------------------------------------------------
# ErrorEstrategiaNula
# -------------------------------------------------------

class TestEstrategiaNula:
    def test_set_estrategia_none_lanza_error(self):
        rec = Recomendador.obtener_instancia()
        with pytest.raises(ErrorEstrategiaNula):
            rec.set_estrategia(None)

    def test_set_estrategia_tipo_incorrecto_lanza_error(self):
        rec = Recomendador.obtener_instancia()
        with pytest.raises(ErrorValidacion):
            rec.set_estrategia("alfabetica")

    def test_estrategia_nula_es_sistema_musical(self):
        rec = Recomendador.obtener_instancia()
        with pytest.raises(ErrorSistemaMusical):
            rec.set_estrategia(None)


# -------------------------------------------------------
# ErrorValidacion — Recomendador y SesionEscucha
# -------------------------------------------------------

class TestRecomendadorValidacion:
    def test_nueva_cancion_tipo_incorrecto(self):
        rec = Recomendador.obtener_instancia()
        with pytest.raises(ErrorValidacion, match="Cancion"):
            rec.nueva_cancion_escuchada("texto", SesionEscucha())

    def test_nueva_cancion_none(self):
        rec = Recomendador.obtener_instancia()
        with pytest.raises(ErrorValidacion):
            rec.nueva_cancion_escuchada(None, SesionEscucha())

    def test_nueva_sesion_tipo_incorrecto(self, cancion_valida):
        rec = Recomendador.obtener_instancia()
        with pytest.raises(ErrorValidacion, match="SesionEscucha"):
            rec.nueva_cancion_escuchada(cancion_valida, "texto")

    def test_anadir_cancion_tipo_incorrecto(self):
        sesion = SesionEscucha()
        with pytest.raises(ErrorValidacion):
            sesion.anadir_cancion("no_es_cancion", HOY)

    def test_anadir_cancion_none(self):
        sesion = SesionEscucha()
        with pytest.raises(ErrorValidacion):
            sesion.anadir_cancion(None, HOY)


# -------------------------------------------------------
# Happy path — flujo correcto sin excepciones
# -------------------------------------------------------

class TestFlujoNormal:
    def test_cancion_valida_se_crea_correctamente(self, cancion_valida):
        assert cancion_valida.id_item == 1
        assert cancion_valida.nombre == "Cancion Test"
        assert cancion_valida.ritmo == 0.5

    def test_cancion_get_sonoros(self, cancion_valida):
        s = cancion_valida.get_sonoros()
        assert set(s.keys()) == {"ritmo", "tono", "escala"}

    def test_cancion_get_sentimentales(self, cancion_valida):
        s = cancion_valida.get_sentimentales()
        assert set(s.keys()) == {"felicidad", "bailabilidad", "energia"}

    def test_sesion_anade_cancion(self, cancion_valida):
        sesion = SesionEscucha()
        sesion.anadir_cancion(cancion_valida, HOY)
        assert len(sesion.historial_canciones) == 1
        assert sesion.historial_canciones[0] is cancion_valida

    def test_handler_cadena_calcula_estadisticas(self, sesion_con_cancion):
        handler_s = SonorosHandler()
        handler_sent = SentimentalesHandler()
        handler_s.set_next(handler_sent)
        handler_s.procesar(sesion_con_cancion)
        assert "ritmo" in sesion_con_cancion.estadisticas_sonoras
        assert "felicidad" in sesion_con_cancion.estadisticas_sentimentales

    def test_estadisticas_media_una_cancion(self, sesion_con_cancion):
        SonorosHandler().procesar(sesion_con_cancion)
        assert sesion_con_cancion.estadisticas_sonoras["ritmo"]["med"] == pytest.approx(0.5)
        assert sesion_con_cancion.estadisticas_sonoras["ritmo"]["desv"] == pytest.approx(0.0)

    def test_busqueda_alfabetica_ordena(self, cancion_valida):
        c2 = Cancion(2, "Alfa", HOY, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
        resultado = BusquedaAlfabetica().buscar([cancion_valida, c2])
        assert resultado[0].nombre == "Alfa"

    def test_recomendador_es_singleton(self):
        r1 = Recomendador.obtener_instancia()
        r2 = Recomendador.obtener_instancia()
        assert r1 is r2

    def test_recomendador_set_estrategia_valida(self):
        rec = Recomendador.obtener_instancia()
        rec.set_estrategia(BusquedaTemporal())
        assert isinstance(rec.estrategia_busqueda, BusquedaTemporal)

    def test_artista_promedia_canciones(self, cancion_valida):
        c2 = Cancion(2, "Otro", HOY, 1.0, 0.5, 0.5, 0.5, 0.5, 0.5)
        artista = Artista(1, "DJ", HOY, [cancion_valida, c2])
        sonoros = artista.get_sonoros()
        assert sonoros["ritmo"] == pytest.approx(0.75)

    def test_flujo_completo_recomendaciones(self):
        c_hist = Cancion(1, "Fiesta", HOY, ritmo=0.8, tono=0.5, escala=0.5,
                         felicidad=0.8, bailabilidad=0.8, energia=0.9)
        c_match = Cancion(2, "Match", HOY, ritmo=0.8, tono=0.5, escala=0.5,
                          felicidad=0.5, bailabilidad=0.5, energia=0.5)
        c_no_match = Cancion(3, "Lenta", HOY, ritmo=0.1, tono=0.5, escala=0.5,
                             felicidad=0.5, bailabilidad=0.5, energia=0.5)

        rec = Recomendador.obtener_instancia()
        rec.catalogo = [c_match, c_no_match]

        handler_s = SonorosHandler()
        handler_sent = SentimentalesHandler()
        handler_s.set_next(handler_sent)
        rec.set_cadena_inicio(handler_s)

        rec_c = RecCanciones()
        rec.suscribir(rec_c)

        sesion = SesionEscucha()
        rec.nueva_cancion_escuchada(c_hist, sesion)

        assert len(sesion.historial_canciones) == 1
        assert "ritmo" in sesion.estadisticas_sonoras

        estadisticos = {
            "sonoras": sesion.estadisticas_sonoras,
            "sentimentales": sesion.estadisticas_sentimentales,
        }
        resultado = rec_c.actualizar(estadisticos, rec.catalogo)
        nombres = [r.nombre for r in resultado]
        assert "Match" in nombres
        assert "Lenta" not in nombres
