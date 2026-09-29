package com.example.alagamentos

import android.os.Bundle
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import com.google.android.material.chip.ChipGroup

class AlertasFragment : Fragment(R.layout.fragment_alertas) {

    private enum class Filtro { TODOS, ATIVOS, ENCERRADOS }

    // Mantido no fragment para sobreviver à ida e volta da tela de detalhes
    private var filtro = Filtro.TODOS

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val ativas = OcorrenciaRepository.getAtivas().size
        view.findViewById<TextView>(R.id.txt_alertas_contagem).text =
            getString(R.string.alertas_contagem, ativas)

        val chips = view.findViewById<ChipGroup>(R.id.chips_filtro)
        chips.check(
            when (filtro) {
                Filtro.TODOS -> R.id.chip_todos
                Filtro.ATIVOS -> R.id.chip_ativos
                Filtro.ENCERRADOS -> R.id.chip_encerrados
            }
        )
        chips.setOnCheckedStateChangeListener { _, ids ->
            filtro = when (ids.firstOrNull()) {
                R.id.chip_ativos -> Filtro.ATIVOS
                R.id.chip_encerrados -> Filtro.ENCERRADOS
                else -> Filtro.TODOS
            }
            preencherLista(view)
        }

        preencherLista(view)
    }

    private fun preencherLista(view: View) {
        val lista = when (filtro) {
            Filtro.TODOS -> OcorrenciaRepository.getAll()
            Filtro.ATIVOS -> OcorrenciaRepository.getAtivas()
            Filtro.ENCERRADOS ->
                OcorrenciaRepository.getAll().filter { it.situacao == Situacao.ENCERRADA }
        }.sortedBy { it.minutosAtras }

        val container = view.findViewById<LinearLayout>(R.id.lista_alertas)
        container.removeAllViews()
        lista.forEach { container.addView(criarItem(container, it)) }

        view.findViewById<View>(R.id.txt_alertas_vazio).visibility =
            if (lista.isEmpty()) View.VISIBLE else View.GONE
    }

    private fun criarItem(parent: LinearLayout, o: Ocorrencia): View {
        val item = layoutInflater.inflate(R.layout.item_alerta, parent, false)
        val corTipo = ContextCompat.getColor(requireContext(), o.corRes())
        val corSeveridade = ContextCompat.getColor(requireContext(), o.severidade.corRes())

        item.findViewById<View>(R.id.alerta_indicador).setBackgroundColor(corTipo)
        item.findViewById<TextView>(R.id.alerta_tipo).apply {
            text = o.tipo.rotulo
            setTextColor(corTipo)
        }
        item.findViewById<TextView>(R.id.alerta_titulo).text = o.titulo
        item.findViewById<TextView>(R.id.alerta_local).text = o.local
        item.findViewById<TextView>(R.id.alerta_severidade).apply {
            text = o.severidade.rotulo
            setTextColor(corSeveridade)
        }
        item.findViewById<TextView>(R.id.alerta_info).text = getString(
            R.string.alerta_info,
            o.situacao.rotulo,
            requireContext().tempoRelativo(o.minutosAtras)
        )

        // Ocorrências encerradas ficam esmaecidas
        if (o.situacao == Situacao.ENCERRADA) item.alpha = 0.6f

        item.setOnClickListener { abrirDetalhes(o.id) }
        return item
    }
}
