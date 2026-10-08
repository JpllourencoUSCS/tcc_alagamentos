package com.example.alagamentos

import android.content.Context
import android.util.AttributeSet
import android.view.MotionEvent
import android.widget.FrameLayout

// Moldura para um mapa dentro de uma tela que rola (cadastro, 07/10/2026): enquanto o dedo
// está no mapa, a rolagem da tela não "rouba" o gesto, então arrastar move o mapa, e não
// a tela. Fora do mapa, a tela rola normalmente.
class MapaArrastavel @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
) : FrameLayout(context, attrs) {

    override fun dispatchTouchEvent(ev: MotionEvent): Boolean {
        when (ev.actionMasked) {
            MotionEvent.ACTION_DOWN -> parent?.requestDisallowInterceptTouchEvent(true)
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL ->
                parent?.requestDisallowInterceptTouchEvent(false)
        }
        return super.dispatchTouchEvent(ev)
    }
}
