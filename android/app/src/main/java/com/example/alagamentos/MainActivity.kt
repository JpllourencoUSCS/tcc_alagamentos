package com.example.alagamentos

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentManager
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {

    // Sem permissão, o NotificadorRisco simplesmente não mostra nada. Com ela, o mapa
    // recarrega para avisar do que chegou enquanto o pedido estava na tela.
    private val pedirNotificacoes =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { concedida ->
            if (concedida) {
                (supportFragmentManager.findFragmentById(R.id.container) as? MapaFragment)?.recarregar()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Sem passar pela tela de entrada (ex.: toque numa notificação após "Sair")
        if (!Perfil(this).sessaoAtiva) {
            startActivity(Intent(this, LoginActivity::class.java))
            finish()
            return
        }
        setContentView(R.layout.activity_main)

        val nav = findViewById<BottomNavigationView>(R.id.bottom_nav)

        nav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_mapa -> mostrar(MapaFragment())
                R.id.nav_alertas -> mostrar(AlertasFragment())
                R.id.nav_previsao -> mostrar(PrevisaoFragment())
                R.id.nav_ajustes -> mostrar(AjustesFragment())
            }
            true
        }

        if (savedInstanceState == null) {
            nav.selectedItemId = R.id.nav_mapa
            pedirPermissaoNotificacoes()
            abrirOcorrenciaDaNotificacao(intent)
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        abrirOcorrenciaDaNotificacao(intent)
    }

    private fun mostrar(fragment: Fragment) {
        // Ao trocar de aba, descarta telas empilhadas (ex.: detalhes)
        supportFragmentManager.popBackStack(null, FragmentManager.POP_BACK_STACK_INCLUSIVE)
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, fragment)
            .commit()
    }

    // Android 13+ exige pedir a permissão de notificações em tempo de execução
    private fun pedirPermissaoNotificacoes() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return
        if (!Preferencias(this).notificacoesAtivas) return
        val permissao = Manifest.permission.POST_NOTIFICATIONS
        if (ContextCompat.checkSelfPermission(this, permissao) != PackageManager.PERMISSION_GRANTED) {
            pedirNotificacoes.launch(permissao)
        }
    }

    // Toque numa notificação de uma única ocorrência abre os detalhes dela
    private fun abrirOcorrenciaDaNotificacao(intent: Intent?) {
        val id = intent?.getLongExtra(NotificadorRisco.EXTRA_OCORRENCIA_ID, -1L) ?: -1L
        if (id < 0) return
        intent?.removeExtra(NotificadorRisco.EXTRA_OCORRENCIA_ID)
        supportFragmentManager.executePendingTransactions()
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, DetalhesFragment.novo(id))
            .addToBackStack(null)
            .commit()
    }
}
