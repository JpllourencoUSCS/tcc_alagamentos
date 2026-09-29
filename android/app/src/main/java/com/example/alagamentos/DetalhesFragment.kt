package com.example.alagamentos

import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.core.os.bundleOf
import androidx.fragment.app.Fragment
import com.google.android.material.appbar.MaterialToolbar

class DetalhesFragment : Fragment(R.layout.fragment_detalhes) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        view.findViewById<MaterialToolbar>(R.id.toolbar).setNavigationOnClickListener {
            parentFragmentManager.popBackStack()
        }

        val id = requireArguments().getInt(ARG_ID)
        val o = OcorrenciaRepository.getById(id)
        if (o == null) {
            parentFragmentManager.popBackStack()
            return
        }
        preencher(view, o)
    }

    private fun preencher(view: View, o: Ocorrencia) {
        val corTipo = ContextCompat.getColor(requireContext(), o.corRes())
        val corSeveridade = ContextCompat.getColor(requireContext(), o.severidade.corRes())

        view.findViewById<View>(R.id.det_indicador).setBackgroundColor(corTipo)
        view.findViewById<TextView>(R.id.det_tipo).apply {
            text = o.tipo.rotulo
            setTextColor(corTipo)
        }
        view.findViewById<TextView>(R.id.det_titulo).text = o.titulo
        view.findViewById<TextView>(R.id.det_local).text = o.local

        view.findViewById<TextView>(R.id.det_severidade).apply {
            text = o.severidade.rotulo
            setTextColor(corSeveridade)
        }
        view.findViewById<TextView>(R.id.det_situacao).text = o.situacao.rotulo

        preencherInfo(view, R.id.info_deteccao, R.string.rotulo_deteccao, o.horarioDeteccao)
        preencherInfo(
            view, R.id.info_atualizacao, R.string.rotulo_atualizacao,
            getString(R.string.valor_atualizacao, o.ultimaAtualizacao, o.minutosAtras)
        )
        preencherInfo(
            view, R.id.info_chuva, R.string.rotulo_chuva,
            getString(R.string.valor_chuva, o.chuvaMm)
        )
        preencherInfo(
            view, R.id.info_temperatura, R.string.rotulo_temperatura,
            getString(R.string.valor_temperatura, o.temperaturaC)
        )
        preencherInfo(view, R.id.info_fonte, R.string.rotulo_fonte, o.fonte)
        preencherInfo(
            view, R.id.info_coordenadas, R.string.rotulo_coordenadas,
            getString(R.string.valor_coordenadas, o.latitude, o.longitude)
        )

        view.findViewById<TextView>(R.id.det_recomendacao).text = o.recomendacao
    }

    private fun preencherInfo(view: View, linhaId: Int, rotuloRes: Int, valor: String) {
        val linha = view.findViewById<View>(linhaId)
        linha.findViewById<TextView>(R.id.txt_rotulo).setText(rotuloRes)
        linha.findViewById<TextView>(R.id.txt_valor).text = valor
    }

    companion object {
        private const val ARG_ID = "ocorrencia_id"

        fun novo(ocorrenciaId: Int) = DetalhesFragment().apply {
            arguments = bundleOf(ARG_ID to ocorrenciaId)
        }
    }
}

// Abre a tela de detalhes por cima da aba atual (volta com o botão voltar)
fun Fragment.abrirDetalhes(ocorrenciaId: Int) {
    parentFragmentManager.beginTransaction()
        .replace(R.id.container, DetalhesFragment.novo(ocorrenciaId))
        .addToBackStack(null)
        .commit()
}
