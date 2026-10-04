package com.example.alagamentos

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.util.Locale

// Risco de alagamento calculado agora pelo backend (GET /risco) para a posição do
// usuário — ou para o centro de São Caetano do Sul, sem permissão de localização —
// com cada fonte que entrou no cálculo do AHP
class PrevisaoFragment : Fragment(R.layout.fragment_previsao) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        view.findViewById<View>(R.id.btn_previsao_atualizar).setOnClickListener { carregar(view) }
        carregar(view)
    }

    private fun carregar(view: View) {
        val progresso = view.findViewById<View>(R.id.progresso_previsao)
        val botao = view.findViewById<View>(R.id.btn_previsao_atualizar)
        progresso.visibility = View.VISIBLE
        botao.isEnabled = false

        viewLifecycleOwner.lifecycleScope.launch {
            // Só usa o GPS se a permissão já foi dada (pedida no cadastro e no filtro "Perto de mim")
            val local = if (Localizacao.temPermissao(requireContext())) Localizacao.atual(requireContext()) else null
            val lat = local?.latitude ?: CENTRO_SCS_LAT
            val lon = local?.longitude ?: CENTRO_SCS_LON
            view.findViewById<TextView>(R.id.txt_previsao_local).setText(
                if (local != null) R.string.previsao_local_gps else R.string.previsao_local_cidade
            )
            try {
                mostrarRisco(view, ApiCliente.api.obterRisco(lat, lon))
            } catch (e: CancellationException) {
                throw e
            } catch (e: HttpException) {
                Log.w(TAG_LOG, "GET /risco falhou", e)
                mostrarErro(
                    view,
                    getString(R.string.previsao_indisponivel_titulo),
                    if (e.code() == 503) getString(R.string.previsao_indisponivel_descricao)
                    else getString(R.string.cadastro_erro_servidor, e.code())
                )
            } catch (e: Exception) {
                Log.w(TAG_LOG, "GET /risco falhou", e)
                mostrarErro(
                    view,
                    getString(R.string.erro_conexao_titulo),
                    getString(R.string.erro_conexao_descricao, BuildConfig.API_BASE_URL)
                )
            } finally {
                progresso.visibility = View.GONE
                botao.isEnabled = true
            }
        }
    }

    private fun mostrarRisco(view: View, risco: RiscoDto) {
        view.findViewById<View>(R.id.card_previsao_erro).visibility = View.GONE
        view.findViewById<View>(R.id.grupo_previsao_resultado).visibility = View.VISIBLE

        val severidade = Severidade.daApi(risco.classificacao)
        val cor = ContextCompat.getColor(requireContext(), severidade?.corRes() ?: R.color.text_primary)
        view.findViewById<View>(R.id.risco_indicador).setBackgroundColor(cor)
        view.findViewById<TextView>(R.id.txt_risco_nivel).apply {
            text = severidade?.rotulo ?: risco.classificacao
            setTextColor(cor)
        }
        view.findViewById<TextView>(R.id.txt_risco_score).text =
            getString(R.string.previsao_score, numero(risco.scoreFinal))

        linha(view, R.id.info_chuva_agora, R.string.previsao_chuva_agora,
            getString(R.string.previsao_valor_mm_h, numero(risco.precipitacaoAtualMmH)))
        linha(view, R.id.info_pico_previsto, R.string.previsao_pico,
            getString(R.string.previsao_valor_mm_3h, numero(risco.picoPrevistoMm3h)))
        linha(view, R.id.info_pluviometro, R.string.previsao_pluviometro,
            risco.pluviometroLocalMmH?.let { getString(R.string.previsao_valor_mm_h, numero(it)) }
                ?: getString(R.string.previsao_sem_dado))
        linha(view, R.id.info_relatos, R.string.previsao_relatos,
            if (risco.componentes.colaborativo != null)
                getString(R.string.previsao_relatos_valor, risco.reportesColaborativos)
            else getString(R.string.previsao_relatos_poucos))
        linha(view, R.id.info_cptec, R.string.previsao_cptec,
            risco.validacaoCptec ?: getString(R.string.previsao_sem_dado))
    }

    private fun mostrarErro(view: View, titulo: String, descricao: String) {
        view.findViewById<View>(R.id.grupo_previsao_resultado).visibility = View.GONE
        view.findViewById<View>(R.id.card_previsao_erro).visibility = View.VISIBLE
        view.findViewById<TextView>(R.id.txt_previsao_erro_titulo).text = titulo
        view.findViewById<TextView>(R.id.txt_previsao_erro_descricao).text = descricao
    }

    private fun linha(view: View, linhaId: Int, rotuloRes: Int, valor: String) {
        val linha = view.findViewById<View>(linhaId)
        linha.findViewById<TextView>(R.id.txt_rotulo).setText(rotuloRes)
        linha.findViewById<TextView>(R.id.txt_valor).text = valor
    }

    // Uma casa decimal com vírgula (pt-BR)
    private fun numero(valor: Double): String = String.format(Locale("pt", "BR"), "%.1f", valor)

    companion object {
        private const val CENTRO_SCS_LAT = -23.6229
        private const val CENTRO_SCS_LON = -46.5548
    }
}
