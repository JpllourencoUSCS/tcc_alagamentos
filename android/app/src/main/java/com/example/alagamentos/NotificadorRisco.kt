package com.example.alagamentos

import android.annotation.SuppressLint
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import androidx.core.app.NotificationChannelCompat
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import androidx.core.content.edit
import java.time.ZonedDateTime

// Notificação local de risco (Semana 7): chamada sempre que o app recebe
// ocorrências da API. Segue as preferências da aba Ajustes (liga/desliga,
// fontes, nível mínimo e raio) e avisa cada ocorrência uma única vez.
// Só roda com o app aberto — não há verificação em segundo plano.
object NotificadorRisco {

    private const val CANAL = "alertas_risco"
    private const val ID_NOTIFICACAO = 1001
    private const val MAX_GUARDADAS = 500
    const val EXTRA_OCORRENCIA_ID = "ocorrencia_id"

    // Ocorrências mais antigas que isso não geram aviso (evita notificar o histórico)
    private const val JANELA_HORAS = 24L

    fun verificar(context: Context, ocorrencias: List<Ocorrencia>) {
        val prefs = Preferencias(context)
        if (!prefs.notificacoesAtivas) return

        val local = Localizacao.ultimaConhecida(context)
        val limite = ZonedDateTime.now().minusHours(JANELA_HORAS)
        val jaAvisadas = avisadas(context)

        val novas = ocorrencias.filter { o ->
            o.id !in jaAvisadas &&
                o.dataHora.isAfter(limite) &&
                o.severidade.ordinal <= prefs.severidadeMinima.ordinal &&
                prefs.notificarFonte(o.fonte) &&
                // Sem localização conhecida, não dá para aplicar o raio: avisa a cidade toda
                (local == null || distanciaKm(local.latitude, local.longitude, o.latitude, o.longitude) <= prefs.raioKm)
        }.sortedBy { it.severidade.ordinal }
        if (novas.isEmpty()) return

        // Só marca como avisadas se o aviso apareceu: na primeira abertura a lista
        // pode chegar antes de a pessoa responder o pedido de permissão
        if (mostrar(context, novas)) guardarAvisadas(context, jaAvisadas + novas.map { it.id })
    }

    fun criarCanal(context: Context) {
        NotificationManagerCompat.from(context).createNotificationChannel(
            NotificationChannelCompat.Builder(CANAL, NotificationManagerCompat.IMPORTANCE_HIGH)
                .setName(context.getString(R.string.notif_canal_nome))
                .setDescription(context.getString(R.string.notif_canal_desc))
                .build()
        )
    }

    @SuppressLint("MissingPermission") // conferido por areNotificationsEnabled()
    private fun mostrar(context: Context, novas: List<Ocorrencia>): Boolean {
        val gerenciador = NotificationManagerCompat.from(context)
        if (!gerenciador.areNotificationsEnabled()) return false
        criarCanal(context)

        val principal = novas.first()
        val abrir = Intent(context, MainActivity::class.java)
            .addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        if (novas.size == 1) abrir.putExtra(EXTRA_OCORRENCIA_ID, principal.id)

        val (titulo, texto) = if (novas.size == 1) {
            context.getString(R.string.notif_titulo, principal.severidade.rotulo) to
                context.titulo(principal)
        } else {
            context.getString(R.string.notif_titulo_varias, novas.size) to
                context.getString(
                    R.string.notif_texto_varias,
                    novas.count { it.severidade == Severidade.ALTA }
                )
        }

        val notificacao = NotificationCompat.Builder(context, CANAL)
            .setSmallIcon(R.drawable.ic_alertas)
            .setColor(ContextCompat.getColor(context, principal.corRes()))
            .setContentTitle(titulo)
            .setContentText(texto)
            .setStyle(NotificationCompat.BigTextStyle().bigText(texto))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setAutoCancel(true)
            .setContentIntent(
                PendingIntent.getActivity(
                    context, 0, abrir,
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
            )
            .build()
        gerenciador.notify(ID_NOTIFICACAO, notificacao)
        return true
    }

    // Guardadas fora das preferências de Ajustes: "Restaurar padrões" não repete avisos
    private fun avisadas(context: Context): Set<Long> =
        context.getSharedPreferences("notificacoes", Context.MODE_PRIVATE)
            .getStringSet("avisadas", emptySet())!!
            .mapNotNull { it.toLongOrNull() }
            .toSet()

    private fun guardarAvisadas(context: Context, ids: Set<Long>) {
        // Os ids do banco são crescentes: ao passar do limite, descarta os mais antigos
        val manter = ids.sortedDescending().take(MAX_GUARDADAS).map { it.toString() }.toSet()
        context.getSharedPreferences("notificacoes", Context.MODE_PRIVATE)
            .edit { putStringSet("avisadas", manter) }
    }
}
