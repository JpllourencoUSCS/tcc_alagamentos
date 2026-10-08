package com.example.alagamentos

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.ZonedDateTime
import java.util.Locale

// Testes de JVM (sem emulador) das funções puras do app (03/10/2026):
// ./gradlew testDebugUnitTest
class FuncoesPurasTest {

    @Test
    fun coordenadasUsamPontoDecimalMesmoEmPortugues() {
        val anterior = Locale.getDefault()
        try {
            Locale.setDefault(Locale("pt", "BR"))
            assertEquals("-23.6148, -46.5435", textoCoordenadas(-23.61481, -46.54349))
            assertEquals("-23.62290, -46.55480", textoCoordenadas(-23.6229, -46.5548, 5))
        } finally {
            Locale.setDefault(anterior)
        }
    }

    @Test
    fun distanciaHaversineEntreCentrosDeSaoCaetanoESantoAndre() {
        // Centro de São Caetano do Sul -> ponto de teste em Santo André: ~4,86 km em linha reta
        val km = distanciaKm(-23.6229, -46.5548, -23.6639, -46.5383)
        assertEquals(4.9, km, 0.3)
    }

    @Test
    fun areaPertoDeMimContemOCirculoDoRaio() {
        val area = AreaBusca.emVoltaDe(-23.6229, -46.5548, 5.0)
        // Pontos a 5 km para o norte e para o leste ficam dentro do quadrado
        assertTrue(-23.6229 + 5.0 / 111.32 <= area.latMax + 1e-9)
        val leste = -46.5548 + 5.0 / (111.32 * Math.cos(Math.toRadians(-23.6229)))
        assertTrue(leste <= area.lonMax + 1e-9)
        assertEquals(5.0, distanciaKm(-23.6229, -46.5548, -23.6229, leste), 0.01)
    }

    @Test
    fun vocabularioEspelhaOBackend() {
        assertEquals(Severidade.MODERADA, Severidade.daApi("Médio"))
        assertEquals(FonteDado.USUARIO, FonteDado.daApi("usuario"))
        assertNull(Severidade.daApi("Altíssimo"))
    }

    @Test
    fun dtoDaApiViraModeloComDataComFuso() {
        val dto = OcorrenciaDto(
            id = 7, latitude = -23.62, longitude = -46.55,
            dataHora = "2026-10-03T21:27:26.252443Z", descricao = "  ",
            nivelRisco = "Alto", fonte = "openweather", chuvaMm = 12.0,
            descricaoClima = null, temperatura = 20.5, umidade = 90,
            idUsuario = null, idEstacaoRef = null
        )
        val modelo = dto.paraModelo()
        assertNotNull(modelo)
        assertEquals(Severidade.ALTA, modelo!!.severidade)
        assertNull(modelo.descricao) // descrição em branco vira ausente
        assertEquals(1_791_062_846L, modelo.dataHora.toEpochSecond())
    }

    @Test
    fun dtoComValorForaDoVocabularioEDescartado() {
        val dto = OcorrenciaDto(
            id = 8, latitude = 0.0, longitude = 0.0, dataHora = "2026-10-03T21:27:26Z",
            descricao = null, nivelRisco = "Crítico", fonte = "usuario", chuvaMm = null,
            descricaoClima = null, temperatura = null, umidade = null, idUsuario = null, idEstacaoRef = null
        )
        assertNull(dto.paraModelo())
    }

    // Municipio (cadastro, 07/10/2026): só aceita locais em São Caetano do Sul
    @Test
    fun municipioComparaSemAcentoNemMaiuscula() {
        assertTrue(Municipio.ehSaoCaetano("São Caetano do Sul"))
        assertTrue(Municipio.ehSaoCaetano("Sao Caetano do Sul"))
        assertTrue(Municipio.ehSaoCaetano(" SÃO CAETANO DO SUL "))
        assertFalse(Municipio.ehSaoCaetano("São Paulo"))
        assertFalse(Municipio.ehSaoCaetano("Santo André"))
        assertFalse(Municipio.ehSaoCaetano(null))
    }

    @Test
    fun municipioDecidePelaCidadeInformadaQuandoHa() {
        // Ponto dentro do retângulo aproximado, mas o geocodificador diz São Paulo: recusa
        assertFalse(Municipio.pertence(listOf("São Paulo", null), -23.6000, -46.5900))
        // Cidade informada só em locality (subAdminArea ausente): aceita
        assertTrue(Municipio.pertence(listOf(null, "São Caetano do Sul"), -23.6229, -46.5548))
        // Avenida Paulista, informada como São Paulo: recusa
        assertFalse(Municipio.pertence(listOf("São Paulo", "São Paulo"), -23.5614, -46.6559))
    }

    @Test
    fun municipioSemCidadeInformadaUsaORetangulo() {
        assertTrue(Municipio.pertence(emptyList(), -23.6229, -46.5548))  // centro de São Caetano
        assertTrue(Municipio.pertence(listOf(null, " "), -23.6229, -46.5548))
        assertFalse(Municipio.pertence(emptyList(), -23.5614, -46.6559)) // Av. Paulista
    }

    // JanelaOcorrencia (07/10/2026): ativa por 24 h; esmaecida depois de 3 h
    @Test
    fun janelaDeOcorrenciasAtivasERecentes() {
        val agora = ZonedDateTime.parse("2026-10-07T20:00:00-03:00")
        assertEquals(ZonedDateTime.parse("2026-10-06T20:00:00-03:00"), JanelaOcorrencia.inicioAtivas(agora))
        assertTrue(JanelaOcorrencia.recente(agora.minusMinutes(170), agora))   // 2 h 50 min
        assertFalse(JanelaOcorrencia.recente(agora.minusMinutes(190), agora))  // 3 h 10 min
    }
}
