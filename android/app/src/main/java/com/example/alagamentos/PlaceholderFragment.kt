package com.example.alagamentos

import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.core.os.bundleOf
import androidx.fragment.app.Fragment

class PlaceholderFragment : Fragment(R.layout.fragment_placeholder) {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        view.findViewById<TextView>(R.id.txt_titulo).text =
            arguments?.getString("titulo") ?: ""
    }

    companion object {
        fun novo(titulo: String) = PlaceholderFragment().apply {
            arguments = bundleOf("titulo" to titulo)
        }
    }
}