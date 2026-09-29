package com.example.alagamentos

import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.core.graphics.ColorUtils
import androidx.fragment.app.Fragment
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

class MapaFragment : Fragment(R.layout.fragment_mapa), OnMapReadyCallback {

    private var ocorrenciaSelecionadaId: Int? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        preencherStatusGeral(view)

        view.findViewById<MaterialButton>(R.id.btn_detalhes).setOnClickListener {
            ocorrenciaSelecionadaId?.let { abrirDetalhes(it) }
        }

        val mapFragment = childFragmentManager.findFragmentById(R.id.map) as SupportMapFragment
        mapFragment.getMapAsync(this)
    }

    private fun preencherStatusGeral(view: View) {
        val todas = OcorrenciaRepository.getAll()
        val ativas = OcorrenciaRepository.getAtivas()

        val alagamentos = ativas.count { it.tipo == TipoOcorrencia.ALAGAMENTO }
        val riscoAlto = ativas.count {
            it.tipo == TipoOcorrencia.RISCO_ALAGAMENTO && it.severidade == Severidade.ALTA
        }
        val chuva = ativas.count { it.tipo == TipoOcorrencia.CHUVA_FORTE }
        val atualizacao = todas.maxOf { it.ultimaAtualizacao }

        val (titulo, descricao, corRes) = when {
            alagamentos > 0 -> Triple(
                getString(R.string.status_alagamento_titulo),
                getString(R.string.status_alagamento_descricao, alagamentos),
                R.color.status_high
            )
            riscoAlto > 0 -> Triple(
                getString(R.string.status_risco_titulo),
                getString(R.string.status_risco_descricao, riscoAlto),
                R.color.status_medium
            )
            chuva > 0 -> Triple(
                getString(R.string.status_chuva_titulo),
                getString(R.string.status_chuva_descricao, chuva),
                R.color.status_rain
            )
            else -> Triple(
                getString(R.string.status_normal_titulo),
                getString(R.string.status_normal_descricao),
                R.color.status_low
            )
        }

        view.findViewById<TextView>(R.id.txt_status_titulo).text = titulo
        view.findViewById<TextView>(R.id.txt_status_descricao).text = descricao
        view.findViewById<View>(R.id.indicador_status)
            .setBackgroundColor(ContextCompat.getColor(requireContext(), corRes))

        view.findViewById<TextView>(R.id.txt_resumo_alagamentos).text =
            getString(R.string.resumo_alagamentos, alagamentos)
        view.findViewById<TextView>(R.id.txt_resumo_risco).text =
            getString(R.string.resumo_risco, riscoAlto)
        view.findViewById<TextView>(R.id.txt_resumo_chuva).text =
            getString(R.string.resumo_chuva, chuva)
        view.findViewById<TextView>(R.id.txt_resumo_atualizacao).text =
            getString(R.string.resumo_atualizacao, atualizacao)
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

        val limites = LatLngBounds.Builder()

        OcorrenciaRepository.getAll().forEach { o ->
            val posicao = LatLng(o.latitude, o.longitude)
            val cor = ContextCompat.getColor(requireContext(), o.corRes())

            val marcador = map.addMarker(
                MarkerOptions()
                    .position(posicao)
                    .icon(BitmapDescriptorFactory.defaultMarker(o.hue()))
            )
            marcador?.tag = o.id

            // Círculo de área de risco para ocorrências não encerradas
            if (o.situacao != Situacao.ENCERRADA) {
                map.addCircle(
                    CircleOptions()
                        .center(posicao)
                        .radius(250.0)
                        .fillColor(ColorUtils.setAlphaComponent(cor, 60))
                        .strokeColor(cor)
                        .strokeWidth(2f)
                )
            }
            limites.include(posicao)
        }

        map.setOnMarkerClickListener { marcador ->
            (marcador.tag as? Int)?.let { mostrarSelecionada(it) }
            false
        }
        map.setOnMapClickListener { esconderSelecionada() }

        val bounds = limites.build()
        map.setOnMapLoadedCallback {
            map.moveCamera(CameraUpdateFactory.newLatLngBounds(bounds, 200))
        }
    }

    private fun mostrarSelecionada(id: Int) {
        val o = OcorrenciaRepository.getById(id) ?: return
        val v = requireView()
        ocorrenciaSelecionadaId = id

        v.findViewById<TextView>(R.id.txt_sel_titulo).text = o.titulo
        v.findViewById<TextView>(R.id.txt_sel_local).text = o.local
        v.findViewById<TextView>(R.id.txt_sel_info).text =
            getString(R.string.sel_info, o.severidade.rotulo, o.tipo.rotulo, o.ultimaAtualizacao)

        v.findViewById<View>(R.id.painel_resumo).visibility = View.GONE
        v.findViewById<View>(R.id.painel_selecionada).visibility = View.VISIBLE
    }

    private fun esconderSelecionada() {
        val v = view ?: return
        ocorrenciaSelecionadaId = null
        v.findViewById<View>(R.id.painel_selecionada).visibility = View.GONE
        v.findViewById<View>(R.id.painel_resumo).visibility = View.VISIBLE
    }
}