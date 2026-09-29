package com.example.alagamentos

enum class TipoOcorrencia(val rotulo: String) {
    ALAGAMENTO("Alagamento"),
    RISCO_ALAGAMENTO("Risco de alagamento"),
    CHUVA_FORTE("Chuva forte"),
    AREA_ALERTA("Área com alerta"),
    OUTROS("Outros")
}

enum class Severidade(val rotulo: String) {
    ALTA("ALTO"),
    MODERADA("MODERADO"),
    BAIXA("BAIXO")
}

enum class Situacao(val rotulo: String) {
    ATIVA("Ativa"),
    EM_OBSERVACAO("Em observação"),
    ENCERRADA("Encerrada")
}

data class Ocorrencia(
    val id: Int,
    val tipo: TipoOcorrencia,
    val titulo: String,
    val local: String,
    val situacao: Situacao,
    val severidade: Severidade,
    val latitude: Double,
    val longitude: Double,
    val horarioDeteccao: String,
    val ultimaAtualizacao: String,
    val minutosAtras: Int,
    val chuvaMm: Double,
    val temperaturaC: Int,
    val fonte: String,
    val recomendacao: String
)