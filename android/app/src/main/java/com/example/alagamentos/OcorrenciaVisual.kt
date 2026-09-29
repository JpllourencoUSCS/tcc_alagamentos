package com.example.alagamentos

import android.content.Context
import com.google.android.gms.maps.model.BitmapDescriptorFactory

// Cor de cada ocorrência (seguindo a classificação visual do PDF)
fun Ocorrencia.corRes(): Int = when (tipo) {
    TipoOcorrencia.ALAGAMENTO -> R.color.status_high
    TipoOcorrencia.RISCO_ALAGAMENTO ->
        if (severidade == Severidade.ALTA) R.color.status_medium else R.color.status_yellow
    TipoOcorrencia.CHUVA_FORTE -> R.color.status_rain
    TipoOcorrencia.AREA_ALERTA -> R.color.status_alert
    TipoOcorrencia.OUTROS -> R.color.status_low
}

// Cor do nível de severidade
fun Severidade.corRes(): Int = when (this) {
    Severidade.ALTA -> R.color.status_high
    Severidade.MODERADA -> R.color.status_medium
    Severidade.BAIXA -> R.color.status_low
}

// "há 12 min" / "há 1 h 5 min"
fun Context.tempoRelativo(minutos: Int): String =
    if (minutos < 60) getString(R.string.tempo_minutos, minutos)
    else getString(R.string.tempo_horas, minutos / 60, minutos % 60)

// Cor do marcador no mapa
fun Ocorrencia.hue(): Float = when (tipo) {
    TipoOcorrencia.ALAGAMENTO -> BitmapDescriptorFactory.HUE_RED
    TipoOcorrencia.RISCO_ALAGAMENTO ->
        if (severidade == Severidade.ALTA) BitmapDescriptorFactory.HUE_ORANGE
        else BitmapDescriptorFactory.HUE_YELLOW
    TipoOcorrencia.CHUVA_FORTE -> BitmapDescriptorFactory.HUE_AZURE
    TipoOcorrencia.AREA_ALERTA -> BitmapDescriptorFactory.HUE_VIOLET
    TipoOcorrencia.OUTROS -> BitmapDescriptorFactory.HUE_GREEN
}