package com.example.alagamentos

import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment

class PrevisaoFragment : Fragment(R.layout.fragment_previsao) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        preencherAgora(view)
        preencherAviso(view)
        preencherHoras(view)
        preencherDias(view)
    }

    private fun preencherAgora(view: View) {
        val agora = PrevisaoRepository.getAgora()

        view.findViewById<TextView>(R.id.txt_prev_atualizacao).text =
            getString(R.string.previsao_atualizacao, agora.atualizacao)
        view.findViewById<TextView>(R.id.txt_prev_temp).text =
            getString(R.string.valor_temperatura, agora.temperaturaC)
        view.findViewById<TextView>(R.id.txt_prev_descricao).text = agora.descricao
        view.findViewById<TextView>(R.id.txt_prev_detalhes).text =
            getString(R.string.previsao_umidade_vento, agora.umidade, agora.ventoKmh)

        val chuva = view.findViewById<View>(R.id.info_prev_chuva)
        chuva.findViewById<TextView>(R.id.txt_rotulo).setText(R.string.rotulo_chuva_ultima_hora)
        chuva.findViewById<TextView>(R.id.txt_valor).text =
            getString(R.string.valor_chuva, agora.chuvaUltimaHoraMm)

        val risco = view.findViewById<View>(R.id.info_prev_risco)
        risco.findViewById<TextView>(R.id.txt_rotulo).setText(R.string.rotulo_risco_alagamento)
        risco.findViewById<TextView>(R.id.txt_valor).apply {
            text = agora.riscoAlagamento.rotulo
            setTextColor(ContextCompat.getColor(requireContext(), agora.riscoAlagamento.corRes()))
        }
    }

    // Destaca o primeiro dia com risco alto de alagamento previsto
    private fun preencherAviso(view: View) {
        val dia = PrevisaoRepository.getProximosDias()
            .firstOrNull { it.riscoAlagamento == Severidade.ALTA } ?: return

        view.findViewById<TextView>(R.id.txt_prev_aviso).text =
            getString(R.string.previsao_aviso, dia.dia.lowercase(), dia.chuvaMm)
        view.findViewById<View>(R.id.card_prev_aviso).visibility = View.VISIBLE
    }

    private fun preencherHoras(view: View) {
        val container = view.findViewById<LinearLayout>(R.id.lista_horas)
        val alturaBarra = resources.displayMetrics.density * 48

        PrevisaoRepository.getProximasHoras().forEach { h ->
            val item = layoutInflater.inflate(R.layout.item_previsao_hora, container, false)
            item.findViewById<TextView>(R.id.hora_hora).text = h.hora
            item.findViewById<TextView>(R.id.hora_temp).text =
                getString(R.string.valor_temperatura, h.temperaturaC)
            item.findViewById<TextView>(R.id.hora_prob).text =
                getString(R.string.valor_percentual, h.probabilidadeChuva)
            item.findViewById<TextView>(R.id.hora_mm).text =
                getString(R.string.valor_chuva, h.chuvaMm)

            val barra = item.findViewById<View>(R.id.hora_barra)
            barra.layoutParams = barra.layoutParams.apply {
                height = (alturaBarra * h.probabilidadeChuva / 100).toInt()
            }
            container.addView(item)
        }
    }

    private fun preencherDias(view: View) {
        val container = view.findViewById<LinearLayout>(R.id.lista_dias)
        val dias = PrevisaoRepository.getProximosDias()

        dias.forEachIndexed { i, d ->
            val item = layoutInflater.inflate(R.layout.item_previsao_dia, container, false)
            item.findViewById<TextView>(R.id.dia_nome).text = d.dia
            item.findViewById<TextView>(R.id.dia_chuva).text =
                getString(R.string.previsao_dia_chuva, d.probabilidadeChuva, d.chuvaMm)
            item.findViewById<TextView>(R.id.dia_temp).text =
                getString(R.string.previsao_min_max, d.minimaC, d.maximaC)
            item.findViewById<TextView>(R.id.dia_risco).apply {
                text = d.riscoAlagamento.rotulo
                setTextColor(ContextCompat.getColor(requireContext(), d.riscoAlagamento.corRes()))
            }
            container.addView(item)

            if (i < dias.lastIndex) container.addView(criarDivisor(container))
        }
    }

    private fun criarDivisor(parent: LinearLayout) = View(requireContext()).apply {
        layoutParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            resources.displayMetrics.density.toInt().coerceAtLeast(1)
        )
        setBackgroundColor(ContextCompat.getColor(parent.context, R.color.divider))
    }
}
