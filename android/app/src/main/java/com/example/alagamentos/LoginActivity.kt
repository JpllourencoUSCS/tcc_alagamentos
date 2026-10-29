package com.example.alagamentos

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.view.inputmethod.EditorInfo
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

// Tela de entrada do protótipo. Desde 29/10/2026 não pede senha: o app nunca teve
// autenticação (fora do escopo) e, na avaliação de usabilidade, o campo de senha sem
// função confundia os participantes. Relatar não depende de cadastro: o único
// identificador enviado ao servidor é o código gerado no aparelho (Perfil.idUsuario).
// O nome é opcional e só adianta o perfil, que fica no aparelho.
class LoginActivity : AppCompatActivity() {

    private lateinit var perfil: Perfil

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        perfil = Perfil(this)

        if (perfil.sessaoAtiva) {
            abrirPrincipal()
            return
        }
        setContentView(R.layout.activity_login)

        val edtUsuario = findViewById<TextInputEditText>(R.id.edt_login_usuario)
        if (savedInstanceState == null) edtUsuario.setText(perfil.nome)
        edtUsuario.setOnEditorActionListener { _, acao, _ ->
            if (acao == EditorInfo.IME_ACTION_DONE) entrar() else false
        }
        findViewById<MaterialButton>(R.id.btn_entrar).setOnClickListener { entrar() }
    }

    private fun entrar(): Boolean {
        val nome = findViewById<TextInputEditText>(R.id.edt_login_usuario).text?.toString()
            ?.trim()?.replace(Regex("\\s+"), " ")

        // Adianta o nome do perfil, sem sobrescrever um perfil já preenchido
        if (!nome.isNullOrEmpty() && !perfil.preenchido) perfil.nome = nome
        perfil.sessaoAtiva = true
        abrirPrincipal()
        return true
    }

    private fun abrirPrincipal() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }

    companion object {
        // Volta para a tela de entrada, limpando a pilha de telas
        fun sair(context: Context) {
            Perfil(context).sessaoAtiva = false
            context.startActivity(
                Intent(context, LoginActivity::class.java)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK)
            )
        }
    }
}
