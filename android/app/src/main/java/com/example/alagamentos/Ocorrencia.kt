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
    CPTEC("cptec", "CPTEC/INPE");

    companion object {
        fun daApi(valor: String?): FonteDado? = entries.find { it.api == valor }
    }
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
