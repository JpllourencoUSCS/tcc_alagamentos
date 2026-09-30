package com.example.alagamentos

import android.os.Bundle
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.core.os.bundleOf
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.google.android.material.appbar.MaterialToolbar
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch

class DetalhesFragment : Fragment(R.layout.fragment_detalhes) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        view.findViewById<MaterialToolbar>(R.id.toolbar).setNavigationOnClickListener {
            parentFragmentManager.popBackStack()
        }

        val id = requireArguments().getLong(ARG_ID)
        viewLifecycleOwner.lifecycleScope.launch {
            val o = try {
                OcorrenciaRepository.obter(id)
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                voltarComAviso(getString(R.string.erro_conexao_titulo))
                return@launch
            }
            if (o == null) {
                voltarComAviso(getString(R.string.ocorrencia_nao_encontrada))
                return@launch
            }
            preencher(view, o)
            view.findViewById<View>(R.id.det_conteudo).visibility = View.VISIBLE
        }
    }

    private fun voltarComAviso(mensagem: String) {
        Toast.makeText(requireContext(), mensagem, Toast.LENGTH_SHORT).show()
        parentFragmentManager.popBackStack()
    }

    private fun preencher(view: View, o: Ocorrencia) {
        val ctx = requireContext()
        val cor = ContextCompat.getColor(ctx, o.corRes())

        view.findViewById<View>(R.id.det_indicador).setBackgroundColor(cor)
        view.findViewById<TextView>(R.id.det_tipo).apply {
            text = getString(R.string.ocorrencia_sem_descricao, o.id)
            setTextColor(cor)
        }
        view.findViewById<TextView>(R.id.det_titulo).text =
            o.descricao ?: getString(R.string.descricao_nao_informada)
        view.findViewById<TextView>(R.id.det_local).text = ctx.tempoRelativo(o.dataHora)

        view.findViewById<TextView>(R.id.det_severidade).apply {
            text = o.severidade.rotulo
            setTextColor(cor)
        }
        view.findViewById<TextView>(R.id.det_fonte).text = o.fonte.rotulo

        preencherInfo(view, R.id.info_deteccao, R.string.rotulo_deteccao, o.dataHora.formatado())
        preencherInfo(view, R.id.info_clima, R.string.rotulo_clima, o.descricaoClima)
        preencherInfo(
            view, R.id.info_chuva, R.string.rotulo_chuva,
            o.chuvaMm?.let { getString(R.string.valor_chuva, it) }
        )
        preencherInfo(
            view, R.id.info_temperatura, R.string.rotulo_temperatura,
            o.temperatura?.let { getString(R.string.valor_temperatura, it) }
        )
        preencherInfo(
            view, R.id.info_umidade, R.string.rotulo_umidade,
            o.umidade?.let { getString(R.string.valor_percentual, it) }
        )
        preencherInfo(
            view, R.id.info_estacao, R.string.rotulo_estacao,
            o.idEstacaoRef?.let { getString(R.string.valor_estacao, it) }
        )
        preencherInfo(view, R.id.info_coordenadas, R.string.rotulo_coordenadas, ctx.coordenadas(o))
    }

    // Campos opcionais que o backend não preencheu ficam ocultos
    private fun preencherInfo(view: View, linhaId: Int, rotuloRes: Int, valor: String?) {
        val linha = view.findViewById<View>(linhaId)
        if (valor == null) {
            linha.visibility = View.GONE
            return
        }
        linha.visibility = View.VISIBLE
        linha.findViewById<TextView>(R.id.txt_rotulo).setText(rotuloRes)
        linha.findViewById<TextView>(R.id.txt_valor).text = valor
    }

    companion object {
        private const val ARG_ID = "ocorrencia_id"

        fun novo(ocorrenciaId: Long) = DetalhesFragment().apply {
            arguments = bundleOf(ARG_ID to ocorrenciaId)
        }
    }
}

// Abre a tela de detalhes por cima da aba atual (volta com o botão voltar)
fun Fragment.abrirDetalhes(ocorrenciaId: Long) {
    parentFragmentManager.beginTransaction()
        .replace(R.id.container, DetalhesFragment.novo(ocorrenciaId))
        .addToBackStack(null)
        .commit()
}
