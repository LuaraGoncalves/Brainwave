# Brainwave BI Assistant

O Brainwave e um AI Data Analyst Dashboard para portifolio. A ideia e simples: a pessoa pergunta em portugues, o backend transforma a pergunta em uma consulta SQL segura, executa em um dataset de vendas, e o frontend mostra resposta, tabela, grafico, SQL gerado e insights.

## Implementado

- API FastAPI com Swagger em `/docs`.
- Login com token JWT simples.
- Dataset real de vendas ficticias salvo no banco.
- Perguntas em portugues convertidas para SQL por regras controladas.
- Bloqueio de comandos perigosos: `DELETE`, `UPDATE`, `DROP`, `ALTER`, `TRUNCATE`, entre outros.
- Historico de chats e mensagens.
- Listagem de datasets.
- Amostra dos dados no dashboard.
- Exportacao CSV.
- Frontend Vue com grafico real em SVG, tabela de resultados, SQL e insights.
- Testes com Pytest para health check, seguranca SQL, analise e dataset.

## Stack

- Backend: FastAPI, SQLAlchemy, PostgreSQL, Pytest.
- Frontend: Vue 3, Vite, TypeScript, Tailwind.
- Infraestrutura: Docker Compose, GitHub Actions.

## Como Rodar Com Docker

```bash
docker-compose up -d --build
```

Acesse:

- Frontend: `http://localhost:8080`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

Usuarios de demonstracao:

```text
analyst@brainwave.bi / analyst123
admin@brainwave.bi / admin123
```

## Como Rodar Localmente

Backend:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Perguntas De Exemplo

- Qual produto vendeu mais?
- Mostre o faturamento por regiao.
- Como foi o faturamento mensal?
- Qual categoria teve maior receita?
- Mostre o ticket medio por categoria.

## Principais Endpoints

- `POST /api/v1/auth/login`
- `POST /api/v1/chat/ask`
- `GET /api/v1/chat/history`
- `GET /api/v1/analytics/overview`
- `GET /api/v1/analytics/connections`
- `POST /api/v1/analytics/connections`
- `GET /api/v1/analytics/saved`
- `POST /api/v1/analytics/saved`
- `GET /api/v1/alerts`
- `POST /api/v1/alerts`
- `POST /api/v1/reports`
- `GET /api/v1/reports`
- `GET /api/v1/reports/{report_id}/export`
- `GET /api/v1/datasets`
- `GET /api/v1/datasets/sales/sample`
- `GET /api/v1/datasets/sales/export`
- `POST /api/v1/query/sql`

## Modulos Do Backend

- Auth: cadastro, login, token e usuario atual.
- Chat: pergunta em portugues, SQL seguro, resposta, tabela, grafico e historico.
- Analytics: overview executivo, conexoes de dados e analises salvas.
- Datasets: catalogo, amostra, upload CSV e exportacao.
- Documents: dicionario de dados, mapa do sistema e preview simples de embedding.
- Alerts: regras simples de monitoramento para receita e pedidos.
- Reports: geracao, listagem, detalhe e exportacao CSV de relatorios.
- Query: execucao controlada de `SELECT`.

## Roadmap

- Adicionar upload visual de CSV no frontend.
- Trocar o tradutor por regras por Text-to-SQL com LLM, mantendo o validador de SQL seguro.
- Adicionar permissao por usuario e datasets privados.
- Gerar relatorios PDF.
- Publicar uma demo online e colocar GIF do fluxo no README.
