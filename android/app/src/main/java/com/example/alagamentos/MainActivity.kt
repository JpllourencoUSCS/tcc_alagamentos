package com.example.alagamentos

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentManager
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
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
        }
    }

    private fun mostrar(fragment: Fragment) {
        // Ao trocar de aba, descarta telas empilhadas (ex.: detalhes)
        supportFragmentManager.popBackStack(null, FragmentManager.POP_BACK_STACK_INCLUSIVE)
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, fragment)
            .commit()
    }
}