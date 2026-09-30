package com.example.alagamentos

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import androidx.core.content.ContextCompat
import androidx.core.location.LocationManagerCompat
import androidx.core.os.CancellationSignal
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.coroutines.resume
import kotlin.math.asin
import kotlin.math.cos
import kotlin.math.pow
import kotlin.math.sin
import kotlin.math.sqrt

// Retângulo de busca no formato do filtro de região do backend (bbox)
data class AreaBusca(val latMin: Double, val lonMin: Double, val latMax: Double, val lonMax: Double) {
    companion object {
        // Limites aproximados do município, com uma pequena folga nas bordas
        val SAO_CAETANO_DO_SUL = AreaBusca(-23.650, -46.600, -23.595, -46.535)

        // Quadrado que contém o círculo de `raioKm` em volta do ponto
        fun emVoltaDe(lat: Double, lon: Double, raioKm: Double): AreaBusca {
            val dLat = raioKm / KM_POR_GRAU
            val dLon = raioKm / (KM_POR_GRAU * cos(Math.toRadians(lat)))
            return AreaBusca(lat - dLat, lon - dLon, lat + dLat, lon + dLon)
        }
    }
}

private const val KM_POR_GRAU = 111.32
private const val RAIO_TERRA_KM = 6371.0

// Distância em linha reta (fórmula de haversine)
fun distanciaKm(lat1: Double, lon1: Double, lat2: Double, lon2: Double): Double {
    val dLat = Math.toRadians(lat2 - lat1)
    val dLon = Math.toRadians(lon2 - lon1)
    val a = sin(dLat / 2).pow(2) +
        cos(Math.toRadians(lat1)) * cos(Math.toRadians(lat2)) * sin(dLon / 2).pow(2)
    return 2 * RAIO_TERRA_KM * asin(sqrt(a))
}

object Localizacao {

    val PERMISSOES = arrayOf(
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION
    )

    fun temPermissao(context: Context): Boolean = PERMISSOES.any {
        ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
    }

    // Última posição conhecida, sem ligar o GPS (null sem permissão ou sem histórico)
    fun ultimaConhecida(context: Context): Location? {
        if (!temPermissao(context)) return null
        val lm = context.getSystemService(LocationManager::class.java) ?: return null
        return try {
            lm.getProviders(true)
                .mapNotNull { lm.getLastKnownLocation(it) }
                .maxByOrNull { it.time }
        } catch (e: SecurityException) {
            null
        }
    }

    // Posição atual; se não vier em `timeoutMs`, cai para a última conhecida
    suspend fun atual(context: Context, timeoutMs: Long = 10_000): Location? {
        if (!temPermissao(context)) return null
        val lm = context.getSystemService(LocationManager::class.java) ?: return null
        val provedor = listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)
            .firstOrNull { lm.isProviderEnabled(it) }
            ?: return ultimaConhecida(context)

        val atual = withTimeoutOrNull(timeoutMs) {
            suspendCancellableCoroutine<Location?> { cont ->
                val cancelar = CancellationSignal()
                cont.invokeOnCancellation { cancelar.cancel() }
                try {
                    LocationManagerCompat.getCurrentLocation(
                        lm, provedor, cancelar, ContextCompat.getMainExecutor(context)
                    ) { local -> if (cont.isActive) cont.resume(local) }
                } catch (e: SecurityException) {
                    cont.resume(null)
                }
            }
        }
        return atual ?: ultimaConhecida(context)
    }
}
