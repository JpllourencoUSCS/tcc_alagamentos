package com.example.alagamentos

import android.content.Context
import android.location.Address
import android.location.Geocoder
import android.os.Build
import android.util.Log
import androidx.annotation.RequiresApi
import kotlinx.coroutines.CancellableContinuation
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import java.io.IOException
import java.util.Locale
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

// Endereço <-> coordenadas pelo geocodificador do próprio Android (07/10/2026): não exige
// chave nem outra API no Google Cloud (ao contrário do Places Autocomplete), mas também não
// sugere endereços enquanto se digita. Precisa de internet; sem o serviço, lança IOException.
// O retângulo de busca do Geocoder não foi usado: no teste, ele restringia demais (endereços
// de fora sumiam, e "Rua Alegre, 100" não era achado sem o nome da cidade no texto).
object Geocodificacao {
    private const val MAX_RESULTADOS = 5

    suspend fun buscar(ctx: Context, texto: String): List<Address> {
        val geocoder = geocoder(ctx)
        val resultados = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            suspendCancellableCoroutine { cont ->
                geocoder.getFromLocationName(texto, MAX_RESULTADOS, ouvinte(cont))
            }
        } else withContext(Dispatchers.IO) {
            @Suppress("DEPRECATION")
            geocoder.getFromLocationName(texto, MAX_RESULTADOS).orEmpty()
        }.filter { it.hasLatitude() && it.hasLongitude() }
        registrar("busca '$texto'", resultados)
        return resultados
    }

    // Endereço (e cidade) de um ponto tocado no mapa ou vindo do GPS
    suspend fun reverso(ctx: Context, latitude: Double, longitude: Double): List<Address> {
        val geocoder = geocoder(ctx)
        val resultados = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            suspendCancellableCoroutine { cont ->
                geocoder.getFromLocation(latitude, longitude, 1, ouvinte(cont))
            }
        } else withContext(Dispatchers.IO) {
            @Suppress("DEPRECATION")
            geocoder.getFromLocation(latitude, longitude, 1).orEmpty()
        }
        registrar("reverso $latitude,$longitude", resultados)
        return resultados
    }

    // Diagnóstico no logcat: cidade e endereço de cada resultado
    private fun registrar(consulta: String, resultados: List<Address>) {
        Log.d(TAG_LOG, "Geocodificação $consulta -> " +
            resultados.joinToString { "${it.cidades()} ${it.getAddressLine(0)}" }.ifEmpty { "nenhum resultado" })
    }

    private fun geocoder(ctx: Context): Geocoder {
        if (!Geocoder.isPresent()) throw IOException("Geocodificador indisponível neste aparelho")
        return Geocoder(ctx, Locale("pt", "BR"))
    }

    @RequiresApi(Build.VERSION_CODES.TIRAMISU)
    private fun ouvinte(cont: CancellableContinuation<List<Address>>) = object : Geocoder.GeocodeListener {
        override fun onGeocode(enderecos: MutableList<Address>) {
            if (cont.isActive) cont.resume(enderecos)
        }

        override fun onError(mensagem: String?) {
            if (cont.isActive) cont.resumeWithException(IOException(mensagem ?: "Falha no geocodificador"))
        }
    }
}

// Cidades que o geocodificador informou para o endereço (entrada de Municipio.pertence)
fun Address.cidades(): List<String?> = listOf(subAdminArea, locality)

// Resultado mais preciso que "o município inteiro" (rua, bairro ou ponto conhecido)?
fun Address.especifico(): Boolean =
    !Municipio.ehSoOMunicipio(thoroughfare, subLocality, featureName)

// "Rua Alegre, 100 - Santa Paula" (ou a primeira linha completa do endereço)
fun Address.resumo(): String? {
    val rua = thoroughfare?.let { r -> subThoroughfare?.let { "$r, $it" } ?: r }
    return listOfNotNull(rua, subLocality).joinToString(" - ").ifEmpty { getAddressLine(0) }
}
