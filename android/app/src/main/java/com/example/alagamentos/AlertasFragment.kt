package com.example.alagamentos

import android.location.Location
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.google.android.material.chip.Chip
import com.google.android.material.chip.ChipGroup
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.time.ZonedDateTime

// Região e período vão para o backend (bbox e data_inicio); nível de risco é filtrado aqui
enum class FiltroRegiao { TODAS, CIDADE, PERTO }

enum class FiltroPeriodo(val horas: Long?) {
    TODO(null), DIA(24), SEMANA(24 * 7), MES(24 * 30);

    fun inicio(): ZonedDateTime? = horas?.let { ZonedDateTime.now().minusHours(it) }
}

class AlertasFragment : Fragment(R.layout.fragment_alertas) {

    // Mantidos no fragment para sobreviver à ida e volta da tela de detalhes
    // (filtro null = todos os níveis de risco)
    private var filtro: Severidade? = null
    private var regiao = FiltroRegiao.TODAS
    private var periodo = FiltroPeriodo.TODO
    private var ocorrencias: List<Ocorrencia>? = null
    private var localAtual: Location? = null
    private var carregamento: Job? = null

    private val pedirLocalizacao =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { r ->
            if (r.values.any { it }) view?.let { carregar(it) }
            else voltarParaTodasAsRegioes(R.string.filtro_perto_sem_permissao)
        }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        view.findViewById<Chip>(R.id.chip_regiao_perto).text =
            getString(R.string.filtro_regiao_perto, Preferencias(requireContext()).raioKm)

        configurarFiltroRisco(view)
        configurarFiltroRegiao(view)
        configurarFiltroPeriodo(view)

        view.findViewById<TextView>(R.id.txt_alertas_vazio).setOnClickListener {
            if (ocorrencias == null) carregar(view)
        }
        view.findViewById<View>(R.id.fab_registrar).setOnClickListener { abrirCadastro() }

        carregar(view)
    }

    private fun configurarFiltroRisco(view: View) {
        val chips = view.findViewById<ChipGroup>(R.id.chips_filtro)
        chips.check(
            when (filtro) {
                null -> R.id.chip_todos
                Severidade.ALTA -> R.id.chip_alto
                Severidade.MODERADA -> R.id.chip_medio
                Severidade.BAIXA -> R.id.chip_baixo
            }
        )
        chips.setOnCheckedStateChangeListener { _, ids ->
            filtro = when (ids.firstOrNull()) {
                R.id.chip_alto -> Severidade.ALTA
                R.id.chip_medio -> Severidade.MODERADA
                R.id.chip_baixo -> Severidade.BAIXA
                else -> null
            }
            preencherLista(view)
        }
    }

    private fun configurarFiltroRegiao(view: View) {
        val chips = view.findViewById<ChipGroup>(R.id.chips_regiao)
        chips.check(
            when (regiao) {
                FiltroRegiao.TODAS -> R.id.chip_regiao_todas
                FiltroRegiao.CIDADE -> R.id.chip_regiao_cidade
                FiltroRegiao.PERTO -> R.id.chip_regiao_perto
            }
        )
        chips.setOnCheckedStateChangeListener { _, ids ->
            val nova = when (ids.firstOrNull()) {
                R.id.chip_regiao_cidade -> FiltroRegiao.CIDADE
                R.id.chip_regiao_perto -> FiltroRegiao.PERTO
                else -> FiltroRegiao.TODAS
            }
            if (nova == regiao) return@setOnCheckedStateChangeListener
            regiao = nova
            if (nova == FiltroRegiao.PERTO && !Localizacao.temPermissao(requireContext())) {
                pedirLocalizacao.launch(Localizacao.PERMISSOES)
            } else {
                carregar(view)
            }
        }
    }

    private fun configurarFiltroPeriodo(view: View) {
        val chips = view.findViewById<ChipGroup>(R.id.chips_periodo)
        chips.check(
            when (periodo) {
                FiltroPeriodo.TODO -> R.id.chip_periodo_todo
                FiltroPeriodo.DIA -> R.id.chip_periodo_24h
                FiltroPeriodo.SEMANA -> R.id.chip_periodo_7d
                FiltroPeriodo.MES -> R.id.chip_periodo_30d
            }
        )
        chips.setOnCheckedStateChangeListener { _, ids ->
            val novo = when (ids.firstOrNull()) {
                R.id.chip_periodo_24h -> FiltroPeriodo.DIA
                R.id.chip_periodo_7d -> FiltroPeriodo.SEMANA
                R.id.chip_periodo_30d -> FiltroPeriodo.MES
                else -> FiltroPeriodo.TODO
            }
            if (novo == periodo) return@setOnCheckedStateChangeListener
            periodo = novo
            carregar(view)
        }
    }

    // "Perto de mim" sem localização disponível: volta para todas as regiões
    private fun voltarParaTodasAsRegioes(mensagem: Int) {
        Toast.makeText(requireContext(), mensagem, Toast.LENGTH_LONG).show()
        regiao = FiltroRegiao.TODAS
        view?.findViewById<ChipGroup>(R.id.chips_regiao)?.check(R.id.chip_regiao_todas)
        view?.let { carregar(it) }
    }

    private fun carregar(view: View) {
        val contagem = view.findViewById<TextView>(R.id.txt_alertas_contagem)
        contagem.setText(R.string.carregando_titulo)
        mostrarMensagem(view, null)

        // Troca rápida de filtro: só vale a resposta da última consulta
        carregamento?.cancel()
        carregamento = viewLifecycleOwner.lifecycleScope.launch {
            val raioKm = Preferencias(requireContext()).raioKm.toDouble()
            val area = when (regiao) {
                FiltroRegiao.TODAS -> null
                FiltroRegiao.CIDADE -> AreaBusca.SAO_CAETANO_DO_SUL
                FiltroRegiao.PERTO -> {
                    val local = Localizacao.atual(requireContext())
                    if (local == null) {
                        voltarParaTodasAsRegioes(R.string.filtro_perto_sem_localizacao)
                        return@launch
                    }
                    localAtual = local
                    AreaBusca.emVoltaDe(local.latitude, local.longitude, raioKm)
                }
            }
            try {
                var lista = OcorrenciaRepository.listar(area, periodo.inicio())
                // O bbox do backend é um quadrado; aqui corta para o círculo do raio
                if (regiao == FiltroRegiao.PERTO) {
                    localAtual?.let { l ->
                        lista = lista.filter {
                            distanciaKm(l.latitude, l.longitude, it.latitude, it.longitude) <= raioKm
                        }
                    }
                }
                ocorrencias = lista
                preencherLista(view)
                NotificadorRisco.verificar(requireContext(), lista)
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Log.w(TAG_LOG, "Falha ao carregar ocorrências", e)
                ocorrencias = null
                contagem.setText(R.string.erro_conexao_titulo)
                view.findViewById<LinearLayout>(R.id.lista_alertas).removeAllViews()
                mostrarMensagem(
                    view,
                    getString(R.string.erro_conexao_descricao, BuildConfig.API_BASE_URL)
                )
            }
        }
    }

    private fun preencherLista(view: View) {
        val todas = ocorrencias ?: return
        val lista = filtro?.let { f -> todas.filter { it.severidade == f } } ?: todas
        // Contagem do que está na tela (região + período + nível), não só do que
        // veio da API — antes ignorava o filtro de nível (achado no teste contra a
        // API real, 03/10/2026)
        view.findViewById<TextView>(R.id.txt_alertas_contagem).text =
            getString(R.string.alertas_contagem, lista.size)

        val container = view.findViewById<LinearLayout>(R.id.lista_alertas)
        container.removeAllViews()
        lista.forEach { container.addView(criarItem(container, it)) }

        mostrarMensagem(view, if (lista.isEmpty()) getString(R.string.alertas_vazio) else null)
    }

    private fun mostrarMensagem(view: View, mensagem: String?) {
        view.findViewById<TextView>(R.id.txt_alertas_vazio).apply {
            text = mensagem
            visibility = if (mensagem == null) View.GONE else View.VISIBLE
        }
    }

    private fun criarItem(parent: LinearLayout, o: Ocorrencia): View {
        val ctx = requireContext()
        val item = layoutInflater.inflate(R.layout.item_alerta, parent, false)
        val cor = ContextCompat.getColor(ctx, o.corRes())

        item.findViewById<View>(R.id.alerta_indicador).setBackgroundColor(cor)
        item.findViewById<TextView>(R.id.alerta_tipo).apply {
            text = o.fonte.rotulo
            setTextColor(cor)
        }
        item.findViewById<TextView>(R.id.alerta_titulo).text = ctx.titulo(o)
        item.findViewById<TextView>(R.id.alerta_local).text = ctx.coordenadas(o)
        item.findViewById<TextView>(R.id.alerta_severidade).apply {
            text = o.severidade.rotulo
            setTextColor(cor)
        }

        val info = listOfNotNull(
            o.descricaoClima,
            o.chuvaMm?.let { getString(R.string.valor_chuva, it) },
            ctx.tempoRelativo(o.dataHora)
        )
        item.findViewById<TextView>(R.id.alerta_info).text = info.joinToString(" • ")

        item.setOnClickListener { abrirDetalhes(o.id) }
        return item
    }
}
