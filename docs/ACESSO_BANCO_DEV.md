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
Esperado: todos os testes passando — 61 em 03/10/2026 (eram 23 em 03/09/2026). Os testes
de integração não dependem do banco estar vazio: cada um desfaz o que criou e só consulta
os próprios dados.

## 4b. API para o app (desde 03/10/2026)

O mesmo `docker compose up -d` sobe também a API (serviço `api`) na porta **8000**:

- **Antes de o time usar:** o João precisa criar a regra de firewall da porta 8000 (seção 6).
  Sem ela, a API só responde na própria máquina dele — a interface do Tailscale está no
  perfil de rede Privado, onde nenhuma regra libera a 8000.
- Navegador: `http://100.114.69.115:8000/docs` (documentação interativa) e
  `http://100.114.69.115:8000/health` (deve responder `{"status":"ok"}`).
- App Android num celular físico: instalar o Tailscale no celular, aceitar o mesmo convite
  e gerar o APK com `API_BASE_URL=http://100.114.69.115:8000/` no `android/local.properties`.
  No emulador rodando no próprio notebook do João, o padrão `http://10.0.2.2:8000/` já
  funciona.
- O banco tem 30 ocorrências **de demonstração** em São Caetano do Sul
  (`id_usuario = 'demo-seed'`), criadas por `backend/dados_demo.py`. Recriar com datas
  atualizadas: `python -m dados_demo --limpar` e depois `python -m dados_demo` (em
  `backend/`, com a `DATABASE_URL` definida).

## 5. Problemas comuns

| Sintoma | Causa provável |
|---|---|
| `tailscale status` não mostra a máquina do João | Convite não foi aceito, ou o João não compartilhou o dispositivo ainda |
| `TcpTestSucceeded: False` | Notebook do João desligado/dormindo, ou Docker Desktop fechado nele |
| `password authentication failed` | Senha errada/desatualizada — pedir a `DATABASE_URL` atual ao João (ele pode ter recriado o `.env`) |
| Conecta mas `\dt` não lista nada | Schema não foi aplicado — avisar o João, ele reaplica `backend/db/schema.sql` |

## 6. Segurança

**Achado de 03/10/2026 — as portas não estão restritas ao Tailscale.** A regra
"TCC Alagamentos - PostgreSQL (Tailscale)" do Firewall do Windows vale para qualquer
interface, qualquer endereço remoto e qualquer perfil de rede, inclusive o **Público**.
Além disso, existe uma regra "Docker Desktop Backend" que libera **todas as portas** do
Docker no perfil Público. Na prática, o Postgres (5432) e a API (8000) ficam acessíveis a
qualquer pessoa na mesma rede local do notebook (por exemplo, um Wi-Fi público), protegidos
só pela senha do banco — a API não tem senha. Não ficam expostos na internet aberta (o
roteador/NAT impede), mas o texto acima ("só pelo Tailscale") não era verdade.

Correção recomendada, num PowerShell **como administrador** no notebook do João:

```powershell
# Restringe a regra do banco aos endereços do Tailscale (100.64.0.0/10)
Set-NetFirewallRule -DisplayName "TCC Alagamentos - PostgreSQL (Tailscale)" -RemoteAddress 100.64.0.0/10
# Regra equivalente para a API
New-NetFirewallRule -DisplayName "TCC Alagamentos - API (Tailscale)" -Direction Inbound `
  -Protocol TCP -LocalPort 8000 -RemoteAddress 100.64.0.0/10 -Action Allow
# Tira do perfil Público a liberação geral do Docker (o Docker continua funcionando localmente)
Get-NetFirewallRule -DisplayName "Docker Desktop Backend" | Where-Object Profile -eq Public |
  Set-NetFirewallRule -Action Block
```

Depois, testar a partir de outra máquina do time (`Test-NetConnection 100.114.69.115 -Port 5432`
e `-Port 8000`) para confirmar que o acesso pelo Tailscale continua funcionando.

- Não commitar a `DATABASE_URL` nem a senha em nenhum arquivo do repositório
- Não repassar o link de convite do Tailscale nem a senha fora do canal privado do time
- Isso é ambiente de desenvolvimento, não produção — não usar dados reais de usuários aqui
