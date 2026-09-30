package com.example.alagamentos

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Patterns
import android.view.inputmethod.EditorInfo
import androidx.appcompat.app.AppCompatActivity
import androidx.core.widget.doAfterTextChanged
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout

// Tela de entrada do protótipo. Não há autenticação real (fora do escopo do
// sistema, ver CT-LOG-001 e o TCLE): qualquer nome/e-mail e senha preenchidos
// levam à área principal.
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

        val tilUsuario = findViewById<TextInputLayout>(R.id.til_login_usuario)
        val tilSenha = findViewById<TextInputLayout>(R.id.til_login_senha)
        val edtUsuario = findViewById<TextInputEditText>(R.id.edt_login_usuario)
        val edtSenha = findViewById<TextInputEditText>(R.id.edt_login_senha)

        if (savedInstanceState == null) edtUsuario.setText(perfil.email ?: perfil.nome)

        edtUsuario.doAfterTextChanged { tilUsuario.error = null }
        edtSenha.doAfterTextChanged { tilSenha.error = null }
        edtSenha.setOnEditorActionListener { _, acao, _ ->
            if (acao == EditorInfo.IME_ACTION_DONE) entrar() else false
        }
        findViewById<MaterialButton>(R.id.btn_entrar).setOnClickListener { entrar() }
    }

    private fun entrar(): Boolean {
        val usuario = findViewById<TextInputEditText>(R.id.edt_login_usuario).text?.toString()?.trim()
        val senha = findViewById<TextInputEditText>(R.id.edt_login_senha).text?.toString()

        var valido = true
        if (usuario.isNullOrEmpty()) {
            findViewById<TextInputLayout>(R.id.til_login_usuario).error =
                getString(R.string.login_erro_usuario)
            valido = false
        }
        if (senha.isNullOrEmpty()) {
            findViewById<TextInputLayout>(R.id.til_login_senha).error =
                getString(R.string.login_erro_senha)
            valido = false
        }
        if (!valido || usuario == null) return true

        // Aproveita o que foi digitado para adiantar o perfil, sem sobrescrever
        if (Patterns.EMAIL_ADDRESS.matcher(usuario).matches()) {
            if (perfil.email == null) perfil.email = usuario
        } else if (!perfil.preenchido) {
            perfil.nome = usuario.replace(Regex("\\s+"), " ")
        }
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
