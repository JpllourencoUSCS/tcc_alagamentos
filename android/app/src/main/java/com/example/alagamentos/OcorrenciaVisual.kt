package com.example.alagamentos

import android.content.Context
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import java.time.Duration
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter

// Cor da ocorrência: segue o nível de risco calculado pelo backend
fun Ocorrencia.corRes(): Int = severidade.corRes()

// Cor do nível de severidade
fun Severidade.corRes(): Int = when (this) {
    Severidade.ALTA -> R.color.status_high
    Severidade.MODERADA -> R.color.status_medium
    Severidade.BAIXA -> R.color.status_low
}

// Cor do marcador no mapa
fun Ocorrencia.hue(): Float = when (severidade) {
    Severidade.ALTA -> BitmapDescriptorFactory.HUE_RED
    Severidade.MODERADA -> BitmapDescriptorFactory.HUE_ORANGE
    Severidade.BAIXA -> BitmapDescriptorFactory.HUE_GREEN
}

// Descrição enviada ao backend ou, sem ela, o número da ocorrência
fun Context.titulo(o: Ocorrencia): String =
    o.descricao ?: getString(R.string.ocorrencia_sem_descricao, o.id)

fun Context.coordenadas(o: Ocorrencia): String =
    getString(R.string.valor_coordenadas, o.latitude, o.longitude)

private val formatoDataHora = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm")

fun ZonedDateTime.formatado(): String = format(formatoDataHora)

// "há 12 min" / "há 1 h 5 min" / "há 3 d"
fun Context.tempoRelativo(dataHora: ZonedDateTime): String {
    val minutos = Duration.between(dataHora, ZonedDateTime.now()).toMinutes().coerceAtLeast(0)
    return when {
        minutos < 60 -> getString(R.string.tempo_minutos, minutos)
        minutos < 60 * 24 -> getString(R.string.tempo_horas, minutos / 60, minutos % 60)
        else -> getString(R.string.tempo_dias, minutos / (60 * 24))
    }
}
