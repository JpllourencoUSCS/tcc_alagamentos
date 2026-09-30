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

    fun notificarFonte(fonte: FonteDado): Boolean =
        prefs.getBoolean(chaveFonte(fonte), true)

    fun setNotificarFonte(fonte: FonteDado, valor: Boolean) =
        prefs.edit { putBoolean(chaveFonte(fonte), valor) }

    fun restaurarPadrao() = prefs.edit { clear() }

    private fun chaveFonte(fonte: FonteDado) = "notificar_fonte_${fonte.name}"

    companion object {
        private const val KEY_NOTIFICACOES = "notificacoes_ativas"
        private const val KEY_SEVERIDADE = "severidade_minima"
        private const val KEY_RAIO = "raio_km"

        const val RAIO_MIN = 1
        const val RAIO_MAX = 20
        const val RAIO_PADRAO = 5
    }
}
