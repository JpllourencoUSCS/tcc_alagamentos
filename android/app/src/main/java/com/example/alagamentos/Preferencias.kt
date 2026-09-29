package com.example.alagamentos

import android.content.Context
import androidx.core.content.edit

// Preferências do usuário, salvas no aparelho (SharedPreferences)
class Preferencias(context: Context) {

    private val prefs = context.getSharedPreferences("ajustes", Context.MODE_PRIVATE)

    var notificacoesAtivas: Boolean
        get() = prefs.getBoolean(KEY_NOTIFICACOES, true)
        set(valor) = prefs.edit { putBoolean(KEY_NOTIFICACOES, valor) }

    var severidadeMinima: Severidade
        get() = prefs.getString(KEY_SEVERIDADE, null)
            ?.let { nome -> Severidade.entries.find { it.name == nome } }
            ?: Severidade.MODERADA
        set(valor) = prefs.edit { putString(KEY_SEVERIDADE, valor.name) }

    var raioKm: Int
        get() = prefs.getInt(KEY_RAIO, RAIO_PADRAO).coerceIn(RAIO_MIN, RAIO_MAX)
        set(valor) = prefs.edit { putInt(KEY_RAIO, valor) }

    fun notificarTipo(tipo: TipoOcorrencia): Boolean =
        prefs.getBoolean(chaveTipo(tipo), true)

    fun setNotificarTipo(tipo: TipoOcorrencia, valor: Boolean) =
        prefs.edit { putBoolean(chaveTipo(tipo), valor) }

    fun restaurarPadrao() = prefs.edit { clear() }

    private fun chaveTipo(tipo: TipoOcorrencia) = "notificar_${tipo.name}"

    companion object {
        private const val KEY_NOTIFICACOES = "notificacoes_ativas"
        private const val KEY_SEVERIDADE = "severidade_minima"
        private const val KEY_RAIO = "raio_km"

        const val RAIO_MIN = 1
        const val RAIO_MAX = 20
        const val RAIO_PADRAO = 5
    }
}
