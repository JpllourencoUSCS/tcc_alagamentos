package com.example.alagamentos

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.core.graphics.ColorUtils
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.OnMapReadyCallback
import com.google.android.gms.maps.SupportMapFragment
import com.google.android.gms.maps.model.BitmapDescriptorFactory
import com.google.android.gms.maps.model.CircleOptions
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.LatLngBounds
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.android.gms.maps.model.MarkerOptions
import com.google.android.material.button.MaterialButton
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch

class MapaFragment : Fragment(R.layout.fragment_mapa), OnMapReadyCallback {

    private var ocorrenciaSelecionadaId: Long? = null
    private var mapa: GoogleMap? = null
    private var ocorrencias: List<Ocorrencia>? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        view.findViewById<MaterialButton>(R.id.btn_detalhes).setOnClickListener {
            ocorrenciaSelecionadaId?.let { abrirDetalhes(it) }
        }
        // Toque no cartão de status recarrega (útil depois de um erro de conexão)
        view.findViewById<View>(R.id.card_status).setOnClickListener { carregar() }
        view.findViewById<View>(R.id.fab_registrar).setOnClickListener { abrirCadastro() }

        val mapFragment = childFragmentManager.findFragmentById(R.id.map) as SupportMapFragment
        mapFragment.getMapAsync(this)

        carregar()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        mapa = null
    }

    fun recarregar() {
        if (view != null) carregar()
    }

    private fun carregar() {
        mostrarStatus(
            getString(R.string.carregando_titulo),
            getString(R.string.carregando_descricao),
            R.color.text_secondary
        )
        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val lista = OcorrenciaRepository.listar()
                ocorrencias = lista
                preencherStatusGeral()
                desenharOcorrencias()
                NotificadorRisco.verificar(requireContext(), lista)
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Log.w(TAG_LOG, "Falha ao carregar ocorrências", e)
                mostrarStatus(
                    getString(R.string.erro_conexao_titulo),
                    getString(R.string.erro_conexao_descricao, BuildConfig.API_BASE_URL),
                    R.color.status_high
                )
            }
        }
    }

    private fun preencherStatusGeral() {
        val v = view ?: return
        val todas = ocorrencias ?: return

        val altas = todas.count { it.severidade == Severidade.ALTA }
        val medias = todas.count { it.severidade == Severidade.MODERADA }
        val baixas = todas.count { it.severidade == Severidade.BAIXA }

        when {
            todas.isEmpty() -> mostrarStatus(
                getString(R.string.status_vazio_titulo),
                getString(R.string.status_vazio_descricao),
                R.color.text_secondary
            )
            altas > 0 -> mostrarStatus(
                getString(R.string.status_alto_titulo),
                getString(R.string.status_alto_descricao, altas),
                R.color.status_high
            )
            medias > 0 -> mostrarStatus(
                getString(R.string.status_medio_titulo),
                getString(R.string.status_medio_descricao, medias),
                R.color.status_medium
            )
            else -> mostrarStatus(
                getString(R.string.status_baixo_titulo),
                getString(R.string.status_baixo_descricao, baixas),
                R.color.status_low
            )
        }

        v.findViewById<TextView>(R.id.txt_resumo_alto).text =
            getString(R.string.resumo_alto, altas)
        v.findViewById<TextView>(R.id.txt_resumo_medio).text =
            getString(R.string.resumo_medio, medias)
        v.findViewById<TextView>(R.id.txt_resumo_baixo).text =
            getString(R.string.resumo_baixo, baixas)
        v.findViewById<TextView>(R.id.txt_resumo_atualizacao).text =
            todas.maxOfOrNull { it.dataHora }
                ?.let { getString(R.string.resumo_atualizacao, it.formatado()) }
                ?: ""
    }

    private fun mostrarStatus(titulo: String, descricao: String, corRes: Int) {
        val v = view ?: return
        v.findViewById<TextView>(R.id.txt_status_titulo).text = titulo
        v.findViewById<TextView>(R.id.txt_status_descricao).text = descricao
        v.findViewById<View>(R.id.indicador_status)
            .setBackgroundColor(ContextCompat.getColor(requireContext(), corRes))
    }

    override fun onMapReady(map: GoogleMap) {
        try {
            map.setMapStyle(
                MapStyleOptions.loadRawResourceStyle(requireContext(), R.raw.map_style_dark)
            )
        } catch (e: Exception) {
            e.printStackTrace()
        }

        map.uiSettings.isZoomControlsEnabled = false
        map.uiSettings.isMapToolbarEnabled = false

        map.setOnMarkerClickListener { marcador ->
            (marcador.tag as? Long)?.let { mostrarSelecionada(it) }
            false
        }
        map.setOnMapClickListener { esconderSelecionada() }

        // Enquanto os dados não chegam, mostra a área monitorada pelo projeto
        map.moveCamera(CameraUpdateFactory.newLatLngZoom(SAO_CAETANO_DO_SUL, ZOOM_CIDADE))

        mapa = map
        desenharOcorrencias()
    }

    // Só desenha quando o mapa e os dados já estiverem prontos
    private fun desenharOcorrencias() {
        val map = mapa ?: return
        val lista = ocorrencias ?: return

        map.clear()
        esconderSelecionada()
        if (lista.isEmpty()) return

        val limites = LatLngBounds.Builder()
        lista.forEach { o ->
            val posicao = LatLng(o.latitude, o.longitude)
            val cor = ContextCompat.getColor(requireContext(), o.corRes())

            val marcador = map.addMarker(
                MarkerOptions()
                    .position(posicao)
                    .icon(BitmapDescriptorFactory.defaultMarker(o.hue()))
            )
            marcador?.tag = o.id

            // Círculo de destaque em volta do ponto, na cor do nível de risco
            map.addCircle(
                CircleOptions()
                    .center(posicao)
                    .radius(250.0)
                    .fillColor(ColorUtils.setAlphaComponent(cor, 60))
                    .strokeColor(cor)
                    .strokeWidth(2f)
            )
            limites.include(posicao)
        }

        if (lista.size == 1) {
            map.moveCamera(CameraUpdateFactory.newLatLngZoom(limites.build().center, ZOOM_PONTO))
        } else {
            val enquadrar = CameraUpdateFactory.newLatLngBounds(limites.build(), 200)
            try {
                map.moveCamera(enquadrar)
            } catch (e: IllegalStateException) {
                // Mapa ainda sem tamanho definido: enquadra quando terminar de carregar
                map.setOnMapLoadedCallback { map.moveCamera(enquadrar) }
            }
        }
    }

    private fun mostrarSelecionada(id: Long) {
        val o = ocorrencias?.find { it.id == id } ?: return
        val v = requireView()
        val ctx = requireContext()
        ocorrenciaSelecionadaId = id

        v.findViewById<TextView>(R.id.txt_sel_titulo).text = ctx.titulo(o)
        v.findViewById<TextView>(R.id.txt_sel_local).text = ctx.coordenadas(o)
        v.findViewById<TextView>(R.id.txt_sel_info).text =
            getString(R.string.sel_info, o.severidade.rotulo, o.fonte.rotulo, o.dataHora.formatado())

        v.findViewById<View>(R.id.painel_resumo).visibility = View.GONE
        v.findViewById<View>(R.id.painel_selecionada).visibility = View.VISIBLE
    }

    private fun esconderSelecionada() {
        val v = view ?: return
        ocorrenciaSelecionadaId = null
        v.findViewById<View>(R.id.painel_selecionada).visibility = View.GONE
        v.findViewById<View>(R.id.painel_resumo).visibility = View.VISIBLE
    }

    companion object {
        // Escopo do monitoramento definido pelo projeto (03/09/2026): São Caetano do Sul
        private val SAO_CAETANO_DO_SUL = LatLng(-23.6229, -46.5548)
        private const val ZOOM_CIDADE = 13f
        private const val ZOOM_PONTO = 15f
    }
}
