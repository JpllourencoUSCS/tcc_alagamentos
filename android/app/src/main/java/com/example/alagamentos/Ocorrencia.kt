package com.example.alagamentos

import java.time.ZonedDateTime

// Espelha backend/constants.py (NivelRisco). `api` é o valor exato trafegado no JSON.
enum class Severidade(val api: String, val rotulo: String) {
    ALTA("Alto", "ALTO"),
    MODERADA("Médio", "MÉDIO"),
    BAIXA("Baixo", "BAIXO");

    companion object {
        fun daApi(valor: String?): Severidade? = entries.find { it.api == valor }
    }
}

// Espelha backend/constants.py (FonteDado)
enum class FonteDado(val api: String, val rotulo: String) {
    USUARIO("usuario", "Relato de usuário"),
    OPENWEATHER("openweather", "OpenWeather"),
    ANA("ana", "ANA"),
    INMET("inmet", "INMET"); // até 07/10/2026: CPTEC("cptec", "CPTEC/INPE")

    companion object {
        fun daApi(valor: String?): FonteDado? = entries.find { it.api == valor }
    }
}

// Por quanto tempo uma ocorrência aparece como atual (07/10/2026). Nada é apagado do
// banco: depois da janela ela sai do mapa e da "Situação atual", mas continua no
// histórico da aba Alertas.
object JanelaOcorrencia {
    const val ATIVA_HORAS = 24L   // mapa, "Situação atual" e notificações
    const val RECENTE_HORAS = 3L  // mesma janela do componente colaborativo do AHP (T15 §6.4)

    fun inicioAtivas(agora: ZonedDateTime = ZonedDateTime.now()): ZonedDateTime =
        agora.minusHours(ATIVA_HORAS)

    fun recente(dataHora: ZonedDateTime, agora: ZonedDateTime = ZonedDateTime.now()): Boolean =
        dataHora.isAfter(agora.minusHours(RECENTE_HORAS))
}

// Espelha OcorrenciaOut (backend/api/schemas.py)
data class Ocorrencia(
    val id: Long,
    val latitude: Double,
    val longitude: Double,
    val dataHora: ZonedDateTime,
    val descricao: String?,
    val severidade: Severidade,
    val fonte: FonteDado,
    val chuvaMm: Double?,
    val descricaoClima: String?,
    val temperatura: Double?,
    val umidade: Int?,
    val idUsuario: String?,
    val idEstacaoRef: Long?
)
