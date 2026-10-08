package com.example.alagamentos

import android.graphics.Typeface
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.util.Locale

// Risco de alagamento calculado agora pelo backend (GET /risco) para a posição do
// usuário — ou para o centro de São Caetano do Sul, sem permissão de localização —
// com cada fonte que entrou no cálculo do AHP. A origem de cada dado e a explicação do
// cálculo ficam em cartões abertos pelos ícones ⓘ (07/10/2026), não mais no texto da tela.
class PrevisaoFragment : Fragment(R.layout.fragment_previsao) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        view.findViewById<View>(R.id.btn_previsao_atualizar).setOnClickListener { carregar(view) }
        view.findViewById<View>(R.id.btn_info_risco).setOnClickListener {
            mostrarInfo(getString(R.string.previsao_info_risco_titulo), getString(R.string.previsao_explicacao))
        }
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

        // Aviso do INMET elevou a classe: explica a diferença entre a pontuação do índice
        // e a classe exibida (ex.: pontuação baixa com classe MÉDIO)
        val piso = risco.pisoAvisoInmet
        view.findViewById<TextView>(R.id.txt_risco_piso).apply {
            visibility = if (piso == null) View.GONE else View.VISIBLE
            if (piso != null) {
                text = getString(
                    R.string.previsao_piso,
                    Severidade.daApi(risco.classificacaoIndice)?.rotulo ?: risco.classificacaoIndice ?: "-",
                    severidade?.rotulo ?: risco.classificacao,
                    piso.evento ?: "-", piso.severidade ?: "-"
                )
            }
        }

        linha(view, R.id.info_chuva_agora, R.string.previsao_chuva_agora, R.string.previsao_info_chuva_agora,
            getString(R.string.previsao_valor_mm_h, numero(risco.precipitacaoAtualMmH)))
        linha(view, R.id.info_pico_previsto, R.string.previsao_pico, R.string.previsao_info_pico,
            getString(R.string.previsao_valor_mm_3h, numero(risco.picoPrevistoMm3h)))
        linha(view, R.id.info_pluviometro, R.string.previsao_pluviometro, R.string.previsao_info_pluviometro,
            risco.pluviometroLocalMmH?.let { getString(R.string.previsao_valor_mm_h, numero(it)) }
                ?: getString(R.string.previsao_sem_dado))
        linha(view, R.id.info_relatos, R.string.previsao_relatos, R.string.previsao_info_relatos,
            if (risco.componentes.colaborativo != null)
                getString(R.string.previsao_relatos_valor, risco.reportesColaborativos)
            else getString(R.string.previsao_relatos_poucos))
        linha(view, R.id.info_inmet, R.string.previsao_inmet, R.string.previsao_info_inmet,
            risco.previsaoInmet ?: getString(R.string.previsao_sem_dado))
        mostrarAvisos(view, risco.avisosInmet.orEmpty())
    }

    // Avisos oficiais do INMET para o município: um bloco por aviso, na cor do nível
    // de perigo (amarelo/laranja/vermelho nos tons do app). Sem aviso, o cartão some.
    private fun mostrarAvisos(view: View, avisos: List<AvisoInmetDto>) {
        val cartao = view.findViewById<View>(R.id.card_avisos_inmet)
        val lista = view.findViewById<LinearLayout>(R.id.lista_avisos_inmet)
        while (lista.childCount > 1) lista.removeViewAt(1) // mantém só o título
        cartao.visibility = if (avisos.isEmpty()) View.GONE else View.VISIBLE
        val ctx = requireContext()
        avisos.forEach { aviso ->
            val cor = ContextCompat.getColor(ctx, when (aviso.severidade) {
                "Grande Perigo" -> R.color.status_high
                "Perigo" -> R.color.status_medium
                else -> R.color.status_yellow
            })
            lista.addView(TextView(ctx).apply {
                text = getString(R.string.previsao_aviso, aviso.evento ?: "-", aviso.severidade ?: "-")
                setTextColor(cor)
                textSize = 16f
                setTypeface(typeface, Typeface.BOLD)
                setPadding(0, (10 * resources.displayMetrics.density).toInt(), 0, 0)
            })
            lista.addView(TextView(ctx).apply {
                text = getString(R.string.previsao_aviso_validade, dataHoraAviso(aviso.inicio), dataHoraAviso(aviso.fim))
                setTextColor(ContextCompat.getColor(ctx, R.color.text_secondary))
                textSize = 13f
            })
            aviso.riscos?.takeIf { it.isNotBlank() }?.let { riscos ->
                lista.addView(TextView(ctx).apply {
                    text = riscos
                    setTextColor(ContextCompat.getColor(ctx, R.color.text_primary))
                    textSize = 13f
                })
            }
        }
    }

    // "2026-10-06 08:52" (horário de Brasília, como o INMET envia) -> "06/10 08:52"
    private fun dataHoraAviso(texto: String?): String {
        val partes = texto?.split(" ", "-", ":") ?: return "-"
        return if (partes.size >= 5) "${partes[2]}/${partes[1]} ${partes[3]}:${partes[4]}" else texto
    }

    private fun mostrarErro(view: View, titulo: String, descricao: String) {
        view.findViewById<View>(R.id.grupo_previsao_resultado).visibility = View.GONE
        view.findViewById<View>(R.id.card_previsao_erro).visibility = View.VISIBLE
        view.findViewById<TextView>(R.id.txt_previsao_erro_titulo).text = titulo
        view.findViewById<TextView>(R.id.txt_previsao_erro_descricao).text = descricao
    }

    private fun linha(view: View, linhaId: Int, rotuloRes: Int, infoRes: Int, valor: String) {
        val linha = view.findViewById<View>(linhaId)
        val rotulo = getString(rotuloRes)
        linha.findViewById<TextView>(R.id.txt_rotulo).text = rotulo
        linha.findViewById<TextView>(R.id.txt_valor).text = valor
        linha.findViewById<View>(R.id.btn_info).apply {
            contentDescription = getString(R.string.previsao_info_descricao, rotulo)
            setOnClickListener { mostrarInfo(rotulo, getString(infoRes)) }
        }
    }

    // Cartão com a origem do dado (ou a explicação do cálculo), aberto pelo ícone ⓘ
    private fun mostrarInfo(titulo: String, texto: String) {
        MaterialAlertDialogBuilder(requireContext())
            .setTitle(titulo)
            .setMessage(texto)
            .setPositiveButton(R.string.entendi, null)
            .show()
    }

    // Uma casa decimal com vírgula (pt-BR)
    private fun numero(valor: Double): String = String.format(Locale("pt", "BR"), "%.1f", valor)

    companion object {
        private const val CENTRO_SCS_LAT = -23.6229
        private const val CENTRO_SCS_LON = -46.5548
    }
}
