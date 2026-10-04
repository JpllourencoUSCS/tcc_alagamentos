package com.example.alagamentos

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
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
}
