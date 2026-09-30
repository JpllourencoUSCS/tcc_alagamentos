package com.example.alagamentos

import android.content.Context
import androidx.core.content.edit
import java.util.UUID

// Bairros oficiais de São Caetano do Sul (escopo do monitoramento)
val BAIRROS_SAO_CAETANO = listOf(
    "Barcelona", "Boa Vista", "Centro", "Cerâmica", "Fundação",
    "Jardim São Caetano", "Mauá", "Nova Gerty", "Olímpico", "Oswaldo Cruz",
    "Prosperidade", "Santa Maria", "Santa Paula", "Santo Antônio", "São José"
)

// Perfil do usuário, salvo no aparelho (SharedPreferences). Fica separado das
// preferências de Ajustes para que "Restaurar padrões" não apague o perfil.
class Perfil(context: Context) {

    private val prefs = context.getSharedPreferences("perfil", Context.MODE_PRIVATE)

    var nome: String?
        get() = prefs.getString(KEY_NOME, null)
        set(valor) = prefs.edit { putString(KEY_NOME, valor) }

    var email: String?
        get() = prefs.getString(KEY_EMAIL, null)
        set(valor) = prefs.edit { putString(KEY_EMAIL, valor) }

    var bairro: String?
        get() = prefs.getString(KEY_BAIRRO, null)
        set(valor) = prefs.edit { putString(KEY_BAIRRO, valor) }

    // id_usuario "gerado pelo sistema" (docs/T13_campos_usuario.md): criado na
    // primeira leitura e mantido mesmo quando o perfil é limpo
    val idUsuario: String
        get() = prefs.getString(KEY_ID, null) ?: UUID.randomUUID().toString().also { novo ->
            prefs.edit { putString(KEY_ID, novo) }
        }

    val preenchido: Boolean
        get() = !nome.isNullOrBlank()

    fun limpar() = prefs.edit {
        remove(KEY_NOME)
        remove(KEY_EMAIL)
        remove(KEY_BAIRRO)
    }

    companion object {
        private const val KEY_NOME = "nome"
        private const val KEY_EMAIL = "email"
        private const val KEY_BAIRRO = "bairro"
        private const val KEY_ID = "id_usuario"
    }
}

// Iniciais para o avatar: "Maria da Silva" -> "MS"
fun iniciais(nome: String?): String {
    val partes = nome.orEmpty().trim().split(Regex("\\s+")).filter { it.isNotEmpty() }
    return when {
        partes.isEmpty() -> "?"
        partes.size == 1 -> partes[0].take(1).uppercase()
        else -> (partes.first().take(1) + partes.last().take(1)).uppercase()
    }
}
