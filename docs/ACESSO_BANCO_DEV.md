# Acesso ao banco de desenvolvimento (via Tailscale)

Guia para qualquer pessoa do time conectar no Postgres/PostGIS que roda na máquina do
João, usado para desenvolvimento e testes até o time decidir a hospedagem definitiva
(ver `CRONOGRAMA_STATUS.md`). **Não é o banco de produção** — só existe enquanto o
notebook do João está ligado, com Docker Desktop aberto e conectado à internet.

Contexto técnico: `docker-compose.yml` (raiz do repo) sobe um `postgis/postgis:16-3.4`
na porta 5432 da máquina do João; a porta 5432 só é alcançável por quem estiver na mesma
rede Tailscale (VPN privada) — não está exposta na internet aberta.

## 1. Pré-requisito

Pedir ao João o **link de convite do Tailscale** (gerado em
https://login.tailscale.com/admin/machines, compartilhando o dispositivo
`tcc-alagamentos-joao`) e a **`DATABASE_URL` completa** (com a senha real) — ele manda
isso por um canal privado do time (WhatsApp/Discord), nunca pelo Git.

## 2. Instalar e conectar o Tailscale

1. Baixar em https://tailscale.com/download e instalar (Windows/Mac/Linux)
2. Abrir o Tailscale e fazer login — pode usar **qualquer conta pessoal** (Google, GitHub,
   Microsoft, e-mail), não precisa ser a mesma do João nem institucional
3. Abrir o link de convite que o João mandou e aceitar o compartilhamento
4. Confirmar que a máquina do João aparece:
   ```
   tailscale status
   ```
   Deve listar uma linha parecida com `100.114.69.115  tcc-alagamentos-joao  ...`
   (o IP pode ser outro — usar o que aparecer aqui, ou o que o João passou)

## 3. Testar conectividade básica (antes de tentar o banco)

```powershell
tailscale ping tcc-alagamentos-joao
Test-NetConnection -ComputerName 100.114.69.115 -Port 5432
```
`TcpTestSucceeded : True` confirma que a porta está alcançável. Se der falso ou "sem
resposta", provavelmente o notebook do João está desligado/dormindo, ou o Docker Desktop
dele não está aberto — confirmar com ele antes de investigar mais.

## 4. Testar uma interação real com o banco

Qualquer uma das opções abaixo confirma leitura **e** escrita, não só conexão.

### Opção A — via psql (se tiver o cliente PostgreSQL instalado)
```bash
psql "postgresql://alagamentos:<senha>@100.114.69.115:5432/alagamentos" -c "\dt"
psql "postgresql://alagamentos:<senha>@100.114.69.115:5432/alagamentos" -c \
  "INSERT INTO ocorrencias (latitude, longitude, nivel_risco, fonte) VALUES (-23.5, -46.6, 'Baixo', 'usuario') RETURNING id;"
psql "postgresql://alagamentos:<senha>@100.114.69.115:5432/alagamentos" -c \
  "DELETE FROM ocorrencias WHERE fonte='usuario' AND nivel_risco='Baixo' AND latitude=-23.5;"
```
`\dt` deve listar `estacoes_referencia`, `ocorrencias`, `reportes_colaborativos_agregado`.
O INSERT deve devolver um `id`; o DELETE limpa o registro de teste depois.

### Opção B — via Python (não precisa instalar nada além do requirements.txt do projeto)
Dentro do `.venv` do projeto (`pip install -r requirements.txt` se ainda não tiver):
```python
from sqlalchemy import create_engine, text

url = "postgresql+psycopg2://alagamentos:<senha>@100.114.69.115:5432/alagamentos"
engine = create_engine(url)

with engine.connect() as conn:
    # lista as tabelas
    tabelas = conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
    )).fetchall()
    print("Tabelas:", tabelas)

    # escreve um registro de teste
    conn.execute(text(
        "INSERT INTO ocorrencias (latitude, longitude, nivel_risco, fonte) "
        "VALUES (-23.5, -46.6, 'Baixo', 'usuario')"
    ))
    conn.commit()

    # lê de volta
    linha = conn.execute(text(
        "SELECT id, latitude, longitude FROM ocorrencias "
        "WHERE fonte='usuario' AND nivel_risco='Baixo' ORDER BY id DESC LIMIT 1"
    )).fetchone()
    print("Inserido e lido de volta:", linha)

    # limpa o registro de teste
    conn.execute(text("DELETE FROM ocorrencias WHERE id = :id"), {"id": linha.id})
    conn.commit()
    print("Registro de teste removido — acesso de leitura e escrita confirmado.")
```
Se esse script rodar sem erro e imprimir as 3 tabelas + o registro inserido/lido/removido,
o acesso está funcionando de ponta a ponta.

### Opção C — rodar a suíte de testes do backend contra esse banco
A forma mais próxima do uso real:
```powershell
$env:DATABASE_URL = "postgresql+psycopg2://alagamentos:<senha>@100.114.69.115:5432/alagamentos"
cd backend
python -m pytest tests/ -v
```
Esperado: os 23 testes passando (mesmo resultado validado na máquina do João em
03/09/2026).

## 5. Problemas comuns

| Sintoma | Causa provável |
|---|---|
| `tailscale status` não mostra a máquina do João | Convite não foi aceito, ou o João não compartilhou o dispositivo ainda |
| `TcpTestSucceeded: False` | Notebook do João desligado/dormindo, ou Docker Desktop fechado nele |
| `password authentication failed` | Senha errada/desatualizada — pedir a `DATABASE_URL` atual ao João (ele pode ter recriado o `.env`) |
| Conecta mas `\dt` não lista nada | Schema não foi aplicado — avisar o João, ele reaplica `backend/db/schema.sql` |

## 6. Segurança

- Não commitar a `DATABASE_URL` nem a senha em nenhum arquivo do repositório
- Não repassar o link de convite do Tailscale nem a senha fora do canal privado do time
- Isso é ambiente de desenvolvimento, não produção — não usar dados reais de usuários aqui
