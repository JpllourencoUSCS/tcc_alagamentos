package com.example.alagamentos

import android.location.Address
import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
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
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

// Cadastro de ocorrência pelo usuário (fonte "usuario") via POST /ocorrencias.
// O local vem de um endereço digitado, de um toque no mapa ou do GPS e só é aceito se
// pertencer a São Caetano do Sul (Municipio.pertence, 07/10/2026).
class CadastroFragment : Fragment(R.layout.fragment_cadastro) {

    private var mapa: GoogleMap? = null
    private var ponto: LatLng? = null          // local já conferido (dentro do município)
    private var enderecoPonto: String? = null  // endereço do local, quando o geocodificador informa
    private var conferencia: Job? = null       // busca/conferência do local em andamento
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
            enderecoPonto = s.getString(KEY_ENDERECO)
        }

        view.findViewById<MaterialToolbar>(R.id.toolbar).setNavigationOnClickListener {
            parentFragmentManager.popBackStack()
        }

        (childFragmentManager.findFragmentById(R.id.cadastro_mapa) as SupportMapFragment)
            .getMapAsync { configurarMapa(it) }

        val busca = view.findViewById<TextInputEditText>(R.id.edt_busca_endereco)
        view.findViewById<TextInputLayout>(R.id.til_busca_endereco).setEndIconOnClickListener {
            buscarEndereco(view)
        }
        // "Buscar" do teclado virtual ou Enter de um teclado físico
        busca.setOnEditorActionListener { _, acao, evento ->
            val enter = evento?.keyCode == KeyEvent.KEYCODE_ENTER && evento.action == KeyEvent.ACTION_DOWN
            if (acao == EditorInfo.IME_ACTION_SEARCH || enter) { buscarEndereco(view); true } else false
        }

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
            outState.putString(KEY_ENDERECO, enderecoPonto)
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
        // Arrastar e pinça liberados: a moldura MapaArrastavel impede a tela de rolar junto.
        // Girar e inclinar continuam desligados (só atrapalham a marcação do ponto).
        map.uiSettings.isScrollGesturesEnabled = true
        map.uiSettings.isZoomGesturesEnabled = true
        map.uiSettings.isRotateGesturesEnabled = false
        map.uiSettings.isTiltGesturesEnabled = false
        map.uiSettings.isZoomControlsEnabled = true
        map.uiSettings.isMapToolbarEnabled = false
        map.setOnMapClickListener { conferirPonto(it, moverCamera = false) }
        map.moveCamera(CameraUpdateFactory.newLatLngZoom(ponto ?: SAO_CAETANO_DO_SUL, ZOOM))
        mapa = map
        ponto?.let { mostrarMarcador(it, moverCamera = false) }
    }

    private fun mostrarMarcador(p: LatLng?, moverCamera: Boolean) {
        val map = mapa ?: return
        map.clear()
        if (p == null) return
        map.addMarker(MarkerOptions().position(p))
        if (moverCamera) map.animateCamera(CameraUpdateFactory.newLatLngZoom(p, ZOOM_PONTO))
    }

    // Ponto do toque no mapa ou do GPS: confere a cidade pelo endereço do ponto
    private fun conferirPonto(p: LatLng, moverCamera: Boolean) {
        conferencia?.cancel()
        ponto = null
        enderecoPonto = null
        mostrarMarcador(p, moverCamera)
        mostrarConferindo()
        conferencia = viewLifecycleOwner.lifecycleScope.launch {
            val endereco = try {
                Geocodificacao.reverso(requireContext(), p.latitude, p.longitude).firstOrNull()
            } catch (e: IOException) {
                null // sem o serviço: Municipio.pertence usa o retângulo do município
            }
            if (Municipio.pertence(endereco?.cidades().orEmpty(), p.latitude, p.longitude)) {
                aceitar(p, endereco?.resumo())
            } else {
                recusarForaDaCidade()
            }
        }
    }

    // Endereço digitado, em duas buscas: (1) com o município no texto, aceita o primeiro
    // resultado específico (rua, bairro, ponto) em São Caetano do Sul; (2) sem achar, busca o
    // texto como foi digitado: se existir em outra cidade, avisa que está fora da área.
    private fun buscarEndereco(view: View) {
        val campo = view.findViewById<TextInputLayout>(R.id.til_busca_endereco)
        val texto = view.findViewById<TextInputEditText>(R.id.edt_busca_endereco).text?.toString()?.trim()
        if (texto.isNullOrEmpty()) {
            campo.error = getString(R.string.cadastro_busca_vazia)
            return
        }
        esconderTeclado(view)
        campo.error = null
        campo.helperText = getString(R.string.cadastro_busca_buscando)
        interromperConferencia()
        conferencia = viewLifecycleOwner.lifecycleScope.launch {
            fun naCidade(lista: List<Address>) = lista.firstOrNull {
                it.especifico() && Municipio.pertence(it.cidades(), it.latitude, it.longitude)
            }
            var outrasCidades = false
            val achado = try {
                naCidade(Geocodificacao.buscar(requireContext(), "$texto, ${Municipio.NOME} - SP"))
                    ?: Geocodificacao.buscar(requireContext(), texto).let { comoDigitado ->
                        outrasCidades = comoDigitado.any { it.especifico() }
                        naCidade(comoDigitado)
                    }
            } catch (e: IOException) {
                campo.error = getString(R.string.cadastro_busca_erro)
                return@launch
            } finally {
                // Também quando a busca é interrompida (ex.: toque no mapa no meio dela)
                campo.helperText = null
            }
            when {
                achado != null -> {
                    val p = LatLng(achado.latitude, achado.longitude)
                    mostrarMarcador(p, moverCamera = true)
                    aceitar(p, achado.resumo())
                }
                outrasCidades -> mostrarForaDaCidade()
                else -> campo.error = getString(R.string.cadastro_busca_nao_encontrado)
            }
        }
    }

    // Cancela a busca/conferência em andamento. Se era a conferência de um toque, o pino
    // provisório e o "Conferindo o local…" saem da tela (volta o último local aceito, se houver).
    private fun interromperConferencia() {
        if (conferencia?.isActive == true) {
            conferencia?.cancel()
            mostrarMarcador(ponto, moverCamera = false)
            view?.let { atualizarTextoLocal(it, erro = false) }
        }
    }

    private fun aceitar(p: LatLng, endereco: String?) {
        ponto = p
        enderecoPonto = endereco
        view?.let { atualizarTextoLocal(it, erro = false) }
    }

    // Toque/GPS fora do município: tira o pino e avisa
    private fun recusarForaDaCidade() {
        ponto = null
        enderecoPonto = null
        mostrarMarcador(null, moverCamera = false)
        view?.let { atualizarTextoLocal(it, erro = false) }
        mostrarForaDaCidade()
    }

    private fun mostrarForaDaCidade() {
        MaterialAlertDialogBuilder(requireContext())
            .setTitle(R.string.cadastro_fora_titulo)
            .setMessage(R.string.cadastro_fora_mensagem)
            .setPositiveButton(R.string.entendi, null)
            .show()
    }

    private fun mostrarConferindo() {
        val texto = view?.findViewById<TextView>(R.id.txt_cadastro_local) ?: return
        texto.setText(R.string.cadastro_local_conferindo)
        texto.setTextColor(ContextCompat.getColor(requireContext(), R.color.text_secondary))
    }

    private fun atualizarTextoLocal(view: View, erro: Boolean) {
        val texto = view.findViewById<TextView>(R.id.txt_cadastro_local)
        val p = ponto
        val (msg, cor) = when {
            p == null && erro -> getString(R.string.cadastro_erro_local) to R.color.status_high
            p == null -> getString(R.string.cadastro_local_instrucao) to R.color.text_secondary
            else -> {
                val coordenadas = textoCoordenadas(p.latitude, p.longitude, 5)
                val msgLocal = enderecoPonto?.let { getString(R.string.cadastro_local_endereco, it, coordenadas) }
                    ?: getString(R.string.cadastro_local_escolhido, coordenadas)
                msgLocal to R.color.text_primary
            }
        }
        texto.text = msg
        texto.setTextColor(ContextCompat.getColor(requireContext(), cor))
    }

    private fun esconderTeclado(view: View) {
        view.findViewById<View>(R.id.edt_busca_endereco).clearFocus()
        ContextCompat.getSystemService(requireContext(), InputMethodManager::class.java)
            ?.hideSoftInputFromWindow(view.windowToken, 0)
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
            else conferirPonto(LatLng(local.latitude, local.longitude), moverCamera = true)
        }
    }

    private fun enviar(view: View) {
        if (enviando) return
        if (conferencia?.isActive == true) {
            aviso(R.string.cadastro_local_aguarde)
            return
        }
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
        private const val KEY_ENDERECO = "endereco"
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
