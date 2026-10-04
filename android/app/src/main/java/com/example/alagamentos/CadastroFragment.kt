package com.example.alagamentos

import android.os.Bundle
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.SupportMapFragment
import com.google.android.gms.maps.model.LatLng
import com.google.android.gms.maps.model.MapStyleOptions
import com.google.android.gms.maps.model.MarkerOptions
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.button.MaterialButton
import com.google.android.material.chip.ChipGroup
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

// Cadastro de ocorrência pelo usuário (fonte "usuario") via POST /ocorrencias
class CadastroFragment : Fragment(R.layout.fragment_cadastro) {

    private var mapa: GoogleMap? = null
    private var ponto: LatLng? = null
    private var enviando = false

    private val pedirLocalizacao =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { r ->
            if (r.values.any { it }) usarMinhaLocalizacao()
            else aviso(R.string.cadastro_sem_permissao_local)
        }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        savedInstanceState?.let { s ->
            if (s.containsKey(KEY_LAT)) ponto = LatLng(s.getDouble(KEY_LAT), s.getDouble(KEY_LON))
        }

        view.findViewById<MaterialToolbar>(R.id.toolbar).setNavigationOnClickListener {
            parentFragmentManager.popBackStack()
        }

        (childFragmentManager.findFragmentById(R.id.cadastro_mapa) as SupportMapFragment)
            .getMapAsync { configurarMapa(it) }

        view.findViewById<MaterialButton>(R.id.btn_minha_localizacao).setOnClickListener {
            if (Localizacao.temPermissao(requireContext())) usarMinhaLocalizacao()
            else pedirLocalizacao.launch(Localizacao.PERMISSOES)
        }

        view.findViewById<ChipGroup>(R.id.chips_cadastro_risco).setOnCheckedStateChangeListener { _, ids ->
            view.findViewById<TextView>(R.id.txt_cadastro_risco_ajuda).setText(
                if (ids.firstOrNull() == R.id.chip_risco_auto) R.string.cadastro_risco_auto_desc
                else R.string.cadastro_risco_manual_desc
            )
        }

        view.findViewById<MaterialButton>(R.id.btn_enviar).setOnClickListener { enviar(view) }

        atualizarTextoLocal(view, erro = false)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        ponto?.let {
            outState.putDouble(KEY_LAT, it.latitude)
            outState.putDouble(KEY_LON, it.longitude)
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        mapa = null
    }

    private fun configurarMapa(map: GoogleMap) {
        try {
            map.setMapStyle(MapStyleOptions.loadRawResourceStyle(requireContext(), R.raw.map_style_dark))
        } catch (e: Exception) {
            e.printStackTrace()
        }
        // Mapa dentro de uma rolagem: arrastar rola a tela; zoom pelos botões
        map.uiSettings.setAllGesturesEnabled(false)
        map.uiSettings.isZoomControlsEnabled = true
        map.uiSettings.isMapToolbarEnabled = false
        map.setOnMapClickListener { definirPonto(it) }
        map.moveCamera(CameraUpdateFactory.newLatLngZoom(ponto ?: SAO_CAETANO_DO_SUL, ZOOM))
        mapa = map
        ponto?.let { definirPonto(it, moverCamera = false) }
    }

    private fun definirPonto(novo: LatLng, moverCamera: Boolean = false) {
        ponto = novo
        mapa?.let { map ->
            map.clear()
            map.addMarker(MarkerOptions().position(novo))
            if (moverCamera) map.animateCamera(CameraUpdateFactory.newLatLngZoom(novo, ZOOM_PONTO))
        }
        view?.let { atualizarTextoLocal(it, erro = false) }
    }

    private fun atualizarTextoLocal(view: View, erro: Boolean) {
        val texto = view.findViewById<TextView>(R.id.txt_cadastro_local)
        val p = ponto
        val (msg, cor) = when {
            p == null && erro -> getString(R.string.cadastro_erro_local) to R.color.status_high
            p == null -> getString(R.string.cadastro_local_instrucao) to R.color.text_secondary
            !dentroDaCidade(p) -> getString(R.string.cadastro_local_fora, textoCoordenadas(p.latitude, p.longitude, 5)) to R.color.status_medium
            else -> getString(R.string.cadastro_local_escolhido, textoCoordenadas(p.latitude, p.longitude, 5)) to R.color.text_primary
        }
        texto.text = msg
        texto.setTextColor(ContextCompat.getColor(requireContext(), cor))
    }

    private fun dentroDaCidade(p: LatLng): Boolean = AreaBusca.SAO_CAETANO_DO_SUL.let {
        p.latitude in it.latMin..it.latMax && p.longitude in it.lonMin..it.lonMax
    }

    private fun usarMinhaLocalizacao() {
        val botao = view?.findViewById<MaterialButton>(R.id.btn_minha_localizacao) ?: return
        botao.isEnabled = false
        botao.setText(R.string.cadastro_buscando_localizacao)
        viewLifecycleOwner.lifecycleScope.launch {
            val local = Localizacao.atual(requireContext())
            botao.isEnabled = true
            botao.setText(R.string.cadastro_usar_localizacao)
            if (local == null) aviso(R.string.cadastro_sem_localizacao)
            else definirPonto(LatLng(local.latitude, local.longitude), moverCamera = true)
        }
    }

    private fun enviar(view: View) {
        if (enviando) return
        val p = ponto
        if (p == null) {
            atualizarTextoLocal(view, erro = true)
            return
        }
        val severidade = when (view.findViewById<ChipGroup>(R.id.chips_cadastro_risco).checkedChipId) {
            R.id.chip_risco_baixo -> Severidade.BAIXA
            R.id.chip_risco_medio -> Severidade.MODERADA
            R.id.chip_risco_alto -> Severidade.ALTA
            else -> null // automático: o backend calcula
        }
        val descricao = view.findViewById<TextInputEditText>(R.id.edt_descricao).text
            ?.toString()?.trim()?.takeIf { it.isNotEmpty() }

        definirEnviando(view, true)
        val fm = parentFragmentManager
        viewLifecycleOwner.lifecycleScope.launch {
            try {
                val criada = OcorrenciaRepository.criar(
                    p.latitude, p.longitude, descricao, severidade, Perfil(requireContext()).idUsuario
                )
                Toast.makeText(
                    requireContext(),
                    criada?.let { getString(R.string.cadastro_sucesso, it.severidade.rotulo) }
                        ?: getString(R.string.cadastro_sucesso_simples),
                    Toast.LENGTH_LONG
                ).show()
                // Troca o formulário pelos detalhes da ocorrência criada (com o risco calculado)
                fm.popBackStack()
                criada?.let {
                    fm.beginTransaction()
                        .replace(R.id.container, DetalhesFragment.novo(it.id))
                        .addToBackStack(null)
                        .commit()
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: HttpException) {
                definirEnviando(view, false)
                aviso(
                    when (e.code()) {
                        422 -> getString(R.string.cadastro_erro_dados)
                        // Backend sem a fonte climática para o cálculo automático (AHP):
                        // com o nível escolhido à mão, o envio funciona
                        503 -> getString(R.string.cadastro_erro_risco_auto)
                        else -> getString(R.string.cadastro_erro_servidor, e.code())
                    }
                )
            } catch (e: IOException) {
                definirEnviando(view, false)
                aviso(getString(R.string.cadastro_erro_conexao, BuildConfig.API_BASE_URL))
            }
        }
    }

    private fun definirEnviando(view: View, ativo: Boolean) {
        enviando = ativo
        view.findViewById<View>(R.id.progresso_envio).visibility = if (ativo) View.VISIBLE else View.INVISIBLE
        view.findViewById<MaterialButton>(R.id.btn_enviar).apply {
            isEnabled = !ativo
            setText(if (ativo) R.string.cadastro_enviando else R.string.cadastro_enviar)
        }
    }

    private fun aviso(resId: Int) = aviso(getString(resId))

    private fun aviso(mensagem: String) {
        Toast.makeText(requireContext(), mensagem, Toast.LENGTH_LONG).show()
    }

    companion object {
        private const val KEY_LAT = "lat"
        private const val KEY_LON = "lon"
        private val SAO_CAETANO_DO_SUL = LatLng(-23.6229, -46.5548)
        private const val ZOOM = 13f
        private const val ZOOM_PONTO = 16f
    }
}

// Abre o cadastro por cima da aba atual (volta com o botão voltar)
fun Fragment.abrirCadastro() {
    parentFragmentManager.beginTransaction()
        .replace(R.id.container, CadastroFragment())
        .addToBackStack(null)
        .commit()
}
