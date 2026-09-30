package com.example.alagamentos

import retrofit2.HttpException
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

// Dados reais vindos da API do backend (GET/POST /ocorrencias e GET /ocorrencias/{id})
object OcorrenciaRepository {

    // Mais recentes primeiro (o backend ordena por data_hora desc).
    // `regiao` e `desde` viram filtros do próprio backend (bbox e data_inicio).
    suspend fun listar(regiao: AreaBusca? = null, desde: ZonedDateTime? = null): List<Ocorrencia> =
        ApiCliente.api.listarOcorrencias(
            dataInicio = desde?.let(::paraUtcIso),
            latMin = regiao?.latMin,
            lonMin = regiao?.lonMin,
            latMax = regiao?.latMax,
            lonMax = regiao?.lonMax
        ).mapNotNull { it.paraModelo() }

    suspend fun obter(id: Long): Ocorrencia? =
        try {
            ApiCliente.api.obterOcorrencia(id).paraModelo()
        } catch (e: HttpException) {
            if (e.code() == 404) null else throw e
        }

    // Reporte do usuário (fonte "usuario"). `severidade` null = o backend calcula
    // o risco pela fusão climática + AHP.
    suspend fun criar(
        latitude: Double,
        longitude: Double,
        descricao: String?,
        severidade: Severidade?,
        idUsuario: String
    ): Ocorrencia? =
        ApiCliente.api.criarOcorrencia(
            OcorrenciaCreateDto(
                latitude = latitude,
                longitude = longitude,
                descricao = descricao,
                nivelRisco = severidade?.api,
                fonte = FonteDado.USUARIO.api,
                idUsuario = idUsuario
            )
        ).paraModelo()

    // Sempre em UTC ("...Z"): um "+hh:mm" na query string chegaria ao backend como espaço
    private fun paraUtcIso(dataHora: ZonedDateTime): String =
        dataHora.withZoneSameInstant(ZoneOffset.UTC)
            .truncatedTo(ChronoUnit.SECONDS)
            .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
}
