package com.example.alagamentos

import androidx.fragment.app.Fragment

// A API do backend (backend/main.py) ainda não tem endpoint de previsão: a fusão
// climática (fusao_climatica.py) só é usada internamente no POST /ocorrencias.
// Até esse endpoint existir, a aba mostra apenas o aviso do layout.
class PrevisaoFragment : Fragment(R.layout.fragment_previsao)
