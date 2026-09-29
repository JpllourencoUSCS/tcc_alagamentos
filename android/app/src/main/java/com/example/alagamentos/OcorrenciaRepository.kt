package com.example.alagamentos

object OcorrenciaRepository {

    // Coordenadas de exemplo. Depois trocamos pela região real do seu projeto.
    private val ocorrencias = listOf(
        Ocorrencia(
            id = 1,
            tipo = TipoOcorrencia.ALAGAMENTO,
            titulo = "Alagamento na Av. Principal",
            local = "Av. Principal, altura do nº 1200",
            situacao = Situacao.ATIVA,
            severidade = Severidade.ALTA,
            latitude = -23.5505,
            longitude = -46.6333,
            horarioDeteccao = "13:10",
            ultimaAtualizacao = "13:42",
            minutosAtras = 12,
            chuvaMm = 38.5,
            temperaturaC = 21,
            fonte = "Sensor de nível 03",
            recomendacao = "Evite transitar pela região enquanto o alagamento estiver ativo."
        ),
        Ocorrencia(
            id = 2,
            tipo = TipoOcorrencia.RISCO_ALAGAMENTO,
            titulo = "Risco de alagamento na Região Norte",
            local = "Região Norte, próximo ao córrego",
            situacao = Situacao.EM_OBSERVACAO,
            severidade = Severidade.ALTA,
            latitude = -23.5440,
            longitude = -46.6280,
            horarioDeteccao = "13:05",
            ultimaAtualizacao = "13:30",
            minutosAtras = 25,
            chuvaMm = 31.0,
            temperaturaC = 21,
            fonte = "Monitoramento meteorológico",
            recomendacao = "Fique atento e evite áreas próximas ao córrego."
        ),
        Ocorrencia(
            id = 3,
            tipo = TipoOcorrencia.CHUVA_FORTE,
            titulo = "Chuva forte na Região Sul",
            local = "Região Sul",
            situacao = Situacao.ATIVA,
            severidade = Severidade.MODERADA,
            latitude = -23.5580,
            longitude = -46.6390,
            horarioDeteccao = "13:34",
            ultimaAtualizacao = "13:47",
            minutosAtras = 8,
            chuvaMm = 24.0,
            temperaturaC = 20,
            fonte = "Pluviômetro 02",
            recomendacao = "Redobre a atenção ao dirigir e evite áreas baixas."
        ),
        Ocorrencia(
            id = 4,
            tipo = TipoOcorrencia.AREA_ALERTA,
            titulo = "Alerta na área central",
            local = "Centro, entorno da praça",
            situacao = Situacao.ATIVA,
            severidade = Severidade.MODERADA,
            latitude = -23.5510,
            longitude = -46.6250,
            horarioDeteccao = "12:50",
            ultimaAtualizacao = "13:20",
            minutosAtras = 35,
            chuvaMm = 18.5,
            temperaturaC = 22,
            fonte = "Defesa Civil",
            recomendacao = "Acompanhe as atualizações e evite permanecer em pontos baixos."
        ),
        Ocorrencia(
            id = 5,
            tipo = TipoOcorrencia.OUTROS,
            titulo = "Bueiro entupido na Rua das Flores",
            local = "Rua das Flores, nº 80",
            situacao = Situacao.ENCERRADA,
            severidade = Severidade.BAIXA,
            latitude = -23.5470,
            longitude = -46.6350,
            horarioDeteccao = "11:20",
            ultimaAtualizacao = "12:40",
            minutosAtras = 65,
            chuvaMm = 5.0,
            temperaturaC = 23,
            fonte = "Relato de usuário",
            recomendacao = "Situação normalizada. Nenhuma ação necessária."
        )
    )

    fun getAll(): List<Ocorrencia> = ocorrencias

    fun getById(id: Int): Ocorrencia? = ocorrencias.find { it.id == id }

    fun getAtivas(): List<Ocorrencia> =
        ocorrencias.filter { it.situacao != Situacao.ENCERRADA }
}