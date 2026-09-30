package com.example.alagamentos

import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.RadioGroup
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.core.view.children
import androidx.fragment.app.Fragment
import com.google.android.material.button.MaterialButton
import com.google.android.material.materialswitch.MaterialSwitch
import com.google.android.material.slider.Slider

class AjustesFragment : Fragment(R.layout.fragment_ajustes) {

    private lateinit var prefs: Preferencias
    private val switchesFonte = mutableMapOf<FonteDado, MaterialSwitch>()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        prefs = Preferencias(requireContext())

        preencherPerfil(view)
        criarSwitchesFonte(view)
        preencher(view)
        configurarListeners(view)
    }

    // Cartão do perfil no topo; a view é recriada ao voltar da tela de perfil
    private fun preencherPerfil(view: View) {
        val perfil = Perfil(requireContext())
        view.findViewById<TextView>(R.id.ajustes_avatar).text = iniciais(perfil.nome)
        view.findViewById<TextView>(R.id.ajustes_perfil_nome).text =
            if (perfil.preenchido) perfil.nome else getString(R.string.ajustes_perfil_vazio_titulo)
        view.findViewById<TextView>(R.id.ajustes_perfil_desc).text = when {
            !perfil.preenchido -> getString(R.string.ajustes_perfil_vazio_desc)
            perfil.bairro != null -> getString(R.string.perfil_bairro_cidade, perfil.bairro)
            else -> getString(R.string.ajustes_perfil_desc)
        }
        view.findViewById<View>(R.id.card_perfil).setOnClickListener { abrirPerfil() }
    }

    private fun criarSwitchesFonte(view: View) {
        val container = view.findViewById<LinearLayout>(R.id.lista_fontes)
        switchesFonte.clear()
        FonteDado.entries.forEach { fonte ->
            val switch = MaterialSwitch(requireContext()).apply {
                text = fonte.rotulo
                setTextColor(ContextCompat.getColor(requireContext(), R.color.text_primary))
            }
            container.addView(
                switch,
                LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
                )
            )
            switchesFonte[fonte] = switch
        }
    }

    // Coloca na tela os valores salvos
    private fun preencher(view: View) {
        val ativas = prefs.notificacoesAtivas
        view.findViewById<MaterialSwitch>(R.id.switch_notificacoes).isChecked = ativas

        switchesFonte.forEach { (fonte, switch) -> switch.isChecked = prefs.notificarFonte(fonte) }

        view.findViewById<RadioGroup>(R.id.grupo_severidade).check(
            when (prefs.severidadeMinima) {
                Severidade.BAIXA -> R.id.rb_sev_baixa
                Severidade.MODERADA -> R.id.rb_sev_moderada
                Severidade.ALTA -> R.id.rb_sev_alta
            }
        )

        val raio = prefs.raioKm
        view.findViewById<Slider>(R.id.slider_raio).value = raio.toFloat()
        view.findViewById<TextView>(R.id.txt_raio).text = getString(R.string.valor_raio, raio)

        atualizarHabilitados(view, ativas)
    }

    private fun configurarListeners(view: View) {
        view.findViewById<MaterialSwitch>(R.id.switch_notificacoes)
            .setOnCheckedChangeListener { _, marcado ->
                prefs.notificacoesAtivas = marcado
                atualizarHabilitados(view, marcado)
            }

        switchesFonte.forEach { (fonte, switch) ->
            switch.setOnCheckedChangeListener { _, marcado -> prefs.setNotificarFonte(fonte, marcado) }
        }

        view.findViewById<RadioGroup>(R.id.grupo_severidade)
            .setOnCheckedChangeListener { _, id ->
                prefs.severidadeMinima = when (id) {
                    R.id.rb_sev_baixa -> Severidade.BAIXA
                    R.id.rb_sev_alta -> Severidade.ALTA
                    else -> Severidade.MODERADA
                }
            }

        view.findViewById<Slider>(R.id.slider_raio).apply {
            setLabelFormatter { getString(R.string.valor_raio, it.toInt()) }
            addOnChangeListener { _, valor, _ ->
                prefs.raioKm = valor.toInt()
                view.findViewById<TextView>(R.id.txt_raio).text =
                    getString(R.string.valor_raio, valor.toInt())
            }
        }

        view.findViewById<MaterialButton>(R.id.btn_restaurar).setOnClickListener {
            prefs.restaurarPadrao()
            preencher(view)
            Toast.makeText(requireContext(), R.string.ajustes_restaurados, Toast.LENGTH_SHORT).show()
        }
    }

    // Sem notificações, as opções dependentes ficam desabilitadas
    private fun atualizarHabilitados(view: View, habilitado: Boolean) {
        switchesFonte.values.forEach { it.isEnabled = habilitado }
        view.findViewById<RadioGroup>(R.id.grupo_severidade).children
            .forEach { it.isEnabled = habilitado }
    }
}
