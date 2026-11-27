# Operational Intelligence

Plataforma de inteligência operacional para análise de dados, monitoramento de KPIs e SLAs, automação de processos e geração de insights com Python, SQL e IA generativa.

## Contexto

Empresas recebem milhares de solicitações de diferentes departamentos, e essas informações ficam espalhadas em planilhas, sistemas e controles operacionais. Isso dificulta identificar atrasos, descumprimentos de SLA, registros duplicados e gargalos.

Este projeto simula esse cenário na **Nexus Serviços Corporativos**, empresa fictícia com sete departamentos: Financeiro, Suprimentos, Operações, Logística, Administrativo, Tecnologia e Gestão de Ativos.

## Perguntas que a plataforma responde

- Qual departamento possui mais solicitações atrasadas?
- Qual é o percentual de cumprimento dos SLAs?
- Qual é o tempo médio de atendimento?
- Quais tipos de solicitação apresentam mais gargalos?
- Quantas solicitações estão pendentes?
- Existem registros duplicados?
- Qual foi a evolução da operação nos últimos meses?

## Arquitetura

| Camada | Ferramenta | Responsabilidade |
|---|---|---|
| Fonte de dados | CSV, Excel, dados sintéticos | Base operacional fictícia |
| Preparação | Python + Pandas | Limpeza, validação, transformação, automação |
| Análise | SQL + Databricks | Consultas, modelagem, agregações, indicadores |
| Visualização | Excel, Looker Studio | Dashboard, KPIs, SLAs |
| Inteligência | IA generativa | Interpretação, insights, recomendações |
| Governança | GitHub | Documentação, versionamento, evolução |

## Fases

| Fase | Desenvolvimento | Status |
|---|---|---|
| 0 | Estruturação do projeto e regras de negócio | Concluída |
| 1 | Criação da base operacional sintética | Concluída |
| 2 | Qualidade e tratamento dos dados | Concluída |
| 3 | Modelagem e consultas analíticas | Concluída |
| 4 | Indicadores operacionais | Concluída |
| 5 | Dashboard gerencial | Em andamento |
| 6 | Automação de relatórios | Pendente |
| 7 | Camada de inteligência artificial | Pendente |

## Documentação

- [Regras de negócio](docs/regras-de-negocio.md)
- [Dicionário de dados](docs/dicionario-de-dados.md)
- [Indicadores](docs/indicadores.md)
- [Geração da base sintética](docs/geracao-da-base.md)
- [Qualidade e tratamento dos dados](docs/qualidade-de-dados.md)
- [Modelagem e consultas analíticas](docs/modelagem-e-consultas.md)

## Como executar

```bash
git clone https://github.com/nevvesdev/operational-intelligence.git
cd operational-intelligence
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Convenções

- Commits semânticos, de uma linha, em português.
- Dados 100% sintéticos, sem qualquer informação real de empresa.
- Cada fase entrega artefatos versionados e documentados.

## Desenvolvido por

João Victor · [GitHub](https://github.com/nevvesdev) · [LinkedIn](https://www.linkedin.com/in/nevvesdev/)

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).