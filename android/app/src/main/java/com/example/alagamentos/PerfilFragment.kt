package com.example.alagamentos

import android.os.Bundle
import android.util.Patterns
import android.view.View
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.TextView
import android.widget.Toast
import androidx.core.widget.doAfterTextChanged
import androidx.fragment.app.Fragment
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.button.MaterialButton
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout

class PerfilFragment : Fragment(R.layout.fragment_perfil) {

    private lateinit var perfil: Perfil

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        perfil = Perfil(requireContext())

        view.findViewById<MaterialToolbar>(R.id.toolbar).setNavigationOnClickListener {
            parentFragmentManager.popBackStack()
        }

        view.findViewById<AutoCompleteTextView>(R.id.edt_bairro).setAdapter(
            ArrayAdapter(requireContext(), android.R.layout.simple_list_item_1, BAIRROS_SAO_CAETANO)
        )

        // Na recriação (ex.: rotação) o próprio Android restaura o que foi digitado
        if (savedInstanceState == null) preencher(view)
        atualizarCabecalho(view)
        configurarListeners(view)
    }

    // Coloca na tela os valores salvos
    private fun preencher(view: View) {
        view.findViewById<TextInputEditText>(R.id.edt_nome).setText(perfil.nome)
        view.findViewById<TextInputEditText>(R.id.edt_email).setText(perfil.email)
        // filter = false: senão o dropdown passa a mostrar só o bairro já escolhido
        view.findViewById<AutoCompleteTextView>(R.id.edt_bairro).setText(perfil.bairro, false)
        view.findViewById<TextView>(R.id.perfil_id).text = perfil.idUsuario
    }

    // Avatar, nome e bairro do topo acompanham o que está sendo digitado
    private fun atualizarCabecalho(view: View) {
        val nome = texto(view, R.id.edt_nome)
        val bairro = texto(view, R.id.edt_bairro)
        view.findViewById<TextView>(R.id.perfil_avatar).text = iniciais(nome)
        view.findViewById<TextView>(R.id.perfil_nome_exibido).text =
            nome ?: getString(R.string.perfil_sem_nome)
        view.findViewById<TextView>(R.id.perfil_bairro_exibido).text =
            bairro?.let { getString(R.string.perfil_bairro_cidade, it) }
                ?: getString(R.string.perfil_sem_bairro)
    }

    private fun configurarListeners(view: View) {
        val tilNome = view.findViewById<TextInputLayout>(R.id.til_nome)
        val tilEmail = view.findViewById<TextInputLayout>(R.id.til_email)

        view.findViewById<TextInputEditText>(R.id.edt_nome).doAfterTextChanged {
            tilNome.error = null
            atualizarCabecalho(view)
        }
        view.findViewById<TextInputEditText>(R.id.edt_email).doAfterTextChanged {
            tilEmail.error = null
        }
        view.findViewById<AutoCompleteTextView>(R.id.edt_bairro).doAfterTextChanged {
            atualizarCabecalho(view)
        }

        view.findViewById<MaterialButton>(R.id.btn_salvar_perfil).setOnClickListener {
            salvar(view)
        }

        view.findViewById<MaterialButton>(R.id.btn_limpar_perfil).setOnClickListener {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle(R.string.perfil_limpar_titulo)
                .setMessage(R.string.perfil_limpar_mensagem)
                .setNegativeButton(R.string.cancelar, null)
                .setPositiveButton(R.string.perfil_limpar) { _, _ ->
                    perfil.limpar()
                    preencher(view)
                    atualizarCabecalho(view)
                    Toast.makeText(requireContext(), R.string.perfil_limpo, Toast.LENGTH_SHORT).show()
                }
                .show()
        }
    }

    private fun salvar(view: View) {
        val nome = texto(view, R.id.edt_nome)
        val email = texto(view, R.id.edt_email)
        val bairro = texto(view, R.id.edt_bairro)

        var valido = true
        if (nome == null || nome.length < 2) {
            view.findViewById<TextInputLayout>(R.id.til_nome).error = getString(R.string.perfil_erro_nome)
            valido = false
        }
        // E-mail é opcional; só valida o formato quando preenchido
        if (email != null && !Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            view.findViewById<TextInputLayout>(R.id.til_email).error = getString(R.string.perfil_erro_email)
            valido = false
        }
        if (!valido) return

        perfil.nome = nome
        perfil.email = email
        perfil.bairro = bairro
        Toast.makeText(requireContext(), R.string.perfil_salvo, Toast.LENGTH_SHORT).show()
        parentFragmentManager.popBackStack()
    }

    // Texto do campo sem espaços extras; vazio vira null
    private fun texto(view: View, id: Int): String? =
        view.findViewById<TextView>(id).text?.toString()?.trim()?.replace(Regex("\\s+"), " ")
            ?.takeIf { it.isNotEmpty() }
}

// Abre o perfil por cima da aba Ajustes (volta com o botão voltar)
fun Fragment.abrirPerfil() {
    parentFragmentManager.beginTransaction()
        .replace(R.id.container, PerfilFragment())
        .addToBackStack(null)
        .commit()
}
