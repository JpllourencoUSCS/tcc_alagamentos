package com.example.alagamentos

data class CondicaoAtual(
    val temperaturaC: Int,
    val descricao: String,
    val chuvaUltimaHoraMm: Double,
    val umidade: Int,
    val ventoKmh: Int,
    val riscoAlagamento: Severidade,
    val atualizacao: String
)

data class PrevisaoHora(
    val hora: String,
    val temperaturaC: Int,
    val probabilidadeChuva: Int,
    val chuvaMm: Double
)

data class PrevisaoDia(
    val dia: String,
    val minimaC: Int,
    val maximaC: Int,
    val probabilidadeChuva: Int,
    val chuvaMm: Double,
    val riscoAlagamento: Severidade
)

object PrevisaoRepository {

    // Dados de exemplo. Depois trocamos por uma API de previsão real.
    private val agora = CondicaoAtual(
        temperaturaC = 21,
        descricao = "Chuva forte",
        chuvaUltimaHoraMm = 12.5,
        umidade = 92,
        ventoKmh = 18,
        riscoAlagamento = Severidade.ALTA,
        atualizacao = "13:45"
    )

    private val horas = listOf(
        PrevisaoHora("14:00", 21, 85, 8.0),
        PrevisaoHora("15:00", 20, 90, 10.5),
        PrevisaoHora("16:00", 20, 80, 6.0),
        PrevisaoHora("17:00", 19, 60, 3.0),
        PrevisaoHora("18:00", 19, 45, 1.5),
        PrevisaoHora("19:00", 18, 30, 0.5),
        PrevisaoHora("20:00", 18, 20, 0.0),
        PrevisaoHora("21:00", 17, 15, 0.0)
    )

    private val dias = listOf(
        PrevisaoDia("Hoje", 17, 23, 90, 45.0, Severidade.ALTA),
        PrevisaoDia("Amanhã", 18, 25, 70, 20.0, Severidade.MODERADA),
        PrevisaoDia("Quinta", 19, 27, 40, 8.0, Severidade.BAIXA),
        PrevisaoDia("Sexta", 20, 28, 20, 2.0, Severidade.BAIXA),
        PrevisaoDia("Sábado", 19, 26, 60, 15.0, Severidade.MODERADA)
    )

    fun getAgora(): CondicaoAtual = agora

    fun getProximasHoras(): List<PrevisaoHora> = horas

    fun getProximosDias(): List<PrevisaoDia> = dias
}
