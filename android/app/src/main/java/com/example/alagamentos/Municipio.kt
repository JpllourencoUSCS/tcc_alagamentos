package com.example.alagamentos

import java.text.Normalizer

// Regra "o local pertence a São Caetano do Sul?" do cadastro (07/10/2026), igual para
// endereço digitado, toque no mapa e localização do aparelho. Funções puras (sem Android),
// testadas em FuncoesPurasTest.
object Municipio {
    const val NOME = "São Caetano do Sul"

    // Compara sem acentos nem maiúsculas: o geocodificador pode devolver "Sao Caetano do Sul"
    fun ehSaoCaetano(nomeCidade: String?): Boolean =
        nomeCidade != null && normalizar(nomeCidade) == normalizar(NOME)

    // Decide pela cidade que o geocodificador informou para o ponto (subAdminArea/locality do
    // Address). Sem essa informação (serviço fora do ar, ponto sem endereço), cai no retângulo
    // aproximado do município — que tem folga nas bordas, por isso é só o plano B.
    fun pertence(cidadesInformadas: List<String?>, latitude: Double, longitude: Double): Boolean {
        val cidades = cidadesInformadas.filterNotNull().filter { it.isNotBlank() }
        return if (cidades.isNotEmpty()) cidades.any(::ehSaoCaetano)
        else dentroDoRetangulo(latitude, longitude)
    }

    // Resultado de geocodificação que é só o município (sem rua, bairro nem ponto conhecido):
    // o que o geocodificador devolve para "<rua que não existe>, São Caetano do Sul".
    // Não serve como local de ocorrência.
    fun ehSoOMunicipio(rua: String?, bairro: String?, nome: String?): Boolean =
        rua.isNullOrBlank() && bairro.isNullOrBlank() && (nome.isNullOrBlank() || ehSaoCaetano(nome))

    fun dentroDoRetangulo(latitude: Double, longitude: Double): Boolean =
        AreaBusca.SAO_CAETANO_DO_SUL.let {
            latitude in it.latMin..it.latMax && longitude in it.lonMin..it.lonMax
        }

    private fun normalizar(texto: String): String =
        Normalizer.normalize(texto, Normalizer.Form.NFD)
            .replace(Regex("\\p{M}+"), "")
            .lowercase()
            .trim()
}
