package com.example.alagamentos

import com.google.gson.annotations.SerializedName
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.util.concurrent.TimeUnit

// Endpoints de backend/api/ocorrencias.py
interface AlagamentosApi {

    // Filtro de região (bbox): o backend exige os 4 limites juntos ou nenhum
    @GET("ocorrencias")
    suspend fun listarOcorrencias(
        @Query("nivel_risco") nivelRisco: String? = null,
        @Query("fonte") fonte: String? = null,
        @Query("data_inicio") dataInicio: String? = null,
        @Query("data_fim") dataFim: String? = null,
        @Query("lat_min") latMin: Double? = null,
        @Query("lon_min") lonMin: Double? = null,
        @Query("lat_max") latMax: Double? = null,
        @Query("lon_max") lonMax: Double? = null,
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = LIMITE_MAXIMO
    ): List<OcorrenciaDto>

    @GET("ocorrencias/{id}")
    suspend fun obterOcorrencia(@Path("id") id: Long): OcorrenciaDto

    @POST("ocorrencias")
    suspend fun criarOcorrencia(@Body dados: OcorrenciaCreateDto): OcorrenciaDto

    companion object {
        // Teto de `limit` aceito pelo backend (Query(le=500))
        const val LIMITE_MAXIMO = 500
    }
}

// Formato JSON de OcorrenciaCreate (backend/api/schemas.py). Campos null não são
// enviados (padrão do Gson): sem `nivel_risco`, o backend calcula o risco (AHP).
data class OcorrenciaCreateDto(
    @SerializedName("latitude") val latitude: Double,
    @SerializedName("longitude") val longitude: Double,
    @SerializedName("descricao") val descricao: String?,
    @SerializedName("nivel_risco") val nivelRisco: String?,
    @SerializedName("fonte") val fonte: String,
    @SerializedName("id_usuario") val idUsuario: String?
)

// Formato JSON de OcorrenciaOut (backend/api/schemas.py)
data class OcorrenciaDto(
    @SerializedName("id") val id: Long,
    @SerializedName("latitude") val latitude: Double,
    @SerializedName("longitude") val longitude: Double,
    @SerializedName("data_hora") val dataHora: String,
    @SerializedName("descricao") val descricao: String?,
    @SerializedName("nivel_risco") val nivelRisco: String,
    @SerializedName("fonte") val fonte: String,
    @SerializedName("chuva_mm") val chuvaMm: Double?,
    @SerializedName("descricao_clima") val descricaoClima: String?,
    @SerializedName("temperatura") val temperatura: Double?,
    @SerializedName("umidade") val umidade: Int?,
    @SerializedName("id_usuario") val idUsuario: String?,
    @SerializedName("id_estacao_ref") val idEstacaoRef: Long?
) {
    // null se o backend devolver algo fora do vocabulário conhecido pelo app
    fun paraModelo(): Ocorrencia? {
        val severidade = Severidade.daApi(nivelRisco) ?: return null
        val fonte = FonteDado.daApi(fonte) ?: return null
        return Ocorrencia(
            id = id,
            latitude = latitude,
            longitude = longitude,
            dataHora = lerDataHora(dataHora),
            descricao = descricao?.takeIf { it.isNotBlank() },
            severidade = severidade,
            fonte = fonte,
            chuvaMm = chuvaMm,
            descricaoClima = descricaoClima?.takeIf { it.isNotBlank() },
            temperatura = temperatura,
            umidade = umidade,
            idUsuario = idUsuario,
            idEstacaoRef = idEstacaoRef
        )
    }
}

// `data_hora` é TIMESTAMPTZ (vem com fuso); sem fuso, trata como UTC
private fun lerDataHora(texto: String): ZonedDateTime {
    val instante = try {
        OffsetDateTime.parse(texto).toInstant()
    } catch (e: Exception) {
        LocalDateTime.parse(texto).toInstant(ZoneOffset.UTC)
    }
    return instante.atZone(ZoneId.systemDefault())
}

object ApiCliente {
    val api: AlagamentosApi by lazy {
        // O POST sem nivel_risco consulta as fontes climáticas externas antes de
        // responder (até ~10-20 s no pior caso); o padrão de 10 s do OkHttp cortaria
        val http = OkHttpClient.Builder()
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(http)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AlagamentosApi::class.java)
    }
}

// Tag do logcat para falhas de comunicação com a API
const val TAG_LOG = "Alagamentos"
