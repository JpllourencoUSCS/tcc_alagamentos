# Dados Cadastrados pelo Usuário

## Formulário de registro de ocorrência

| Campo | Tipo | Obrigatório | Observação |
|---|---|---|---|
| latitude | float | Sim | Capturado pelo GPS |
| longitude | float | Sim | Capturado pelo GPS |
| nivel_risco | enum | Sim | Baixo / Médio / Alto |
| descricao | string | Não | Campo livre, max 300 chars |
| data_hora | datetime | Sim | Gerado automaticamente |
| id_usuario | string | Sim | Gerado pelo sistema |

## Campos descartados nesta versão
- Foto: complexidade de upload, fica como melhoria futura
- Endereço textual: substituído por coordenadas GPS

## Justificativa
Manter o formulário simples aumenta a taxa de registros pelos usuários.