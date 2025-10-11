# Sistema de Gestão de Coleta e Preços

Este projeto fornece uma ferramenta completa para coletar automaticamente cotações recebidas por e-mail (Outlook/Office 365), armazenar os valores em um banco SQLite e gerar análises consolidadas por produto.

## Recursos

- Coleta automática de e-mails via IMAP (Outlook) com autenticação configurada por variáveis de ambiente.
- Interpretador inteligente que entende diferentes formatos de e-mail (CSV, linhas separadas por ponto e vírgula ou blocos "chave: valor").
- Armazenamento estruturado em banco de dados SQLite com histórico de preços.
- Relatórios agregados com média, mínimo, máximo, última cotação e variação percentual.
- Interface de linha de comando (`price-manager`) para executar a coleta, listar registros e visualizar análises.

## Requisitos

- Python 3.10 ou superior.
- Dependências padrão da biblioteca padrão (não é necessário instalar pacotes externos).

## Configuração

1. Clone este repositório e acesse a pasta do projeto.
2. Crie e ative um ambiente virtual (opcional, mas recomendado).
3. Instale o projeto em modo editável:

   ```bash
   pip install -e .
   ```

4. Configure as credenciais de e-mail através das variáveis de ambiente:

   ```bash
   export PRICE_MANAGER_EMAIL="flavio@quimport.com.br"
   export PRICE_MANAGER_PASSWORD="<sua-senha-ou-token>"
   ```

   > **Dica:** Utilize uma senha de aplicativo para contas com autenticação em duas etapas.

## Uso da linha de comando

O comando principal instalado é `price-manager`. Os subcomandos disponíveis são:

### Coleta de novos preços

```bash
price-manager dados.db ingest --search "SUBJECT \"cotação\"" --limit 20
```

- `--search`: filtro IMAP para localizar apenas e-mails relevantes.
- `--limit`: controla a quantidade máxima de e-mails processados por execução.

### Análise dos preços armazenados

```bash
price-manager dados.db analyze --format table
```

- `--format`: escolha entre `table` (padrão) ou `json` para exportar os dados.

### Listagem dos registros brutos

```bash
price-manager dados.db list --limit 10
```

Mostra as últimas cotações gravadas no banco de dados.

## Estrutura Interna

- `price_manager/config.py`: carrega as configurações a partir de variáveis de ambiente.
- `price_manager/email_client.py`: conecta ao Outlook via IMAP e baixa os e-mails.
- `price_manager/parsing.py`: transforma corpos de e-mail em registros estruturados.
- `price_manager/storage.py`: lida com a persistência em SQLite.
- `price_manager/analysis.py`: gera estatísticas por produto.
- `price_manager/manager.py`: orquestra o fluxo de ingestão e análise.
- `price_manager/cli.py`: disponibiliza a interface de linha de comando.

## Testes

Execute a suíte de testes com:

```bash
pytest
```

## Próximos Passos Sugestões

- Suporte a anexos em CSV ou planilhas.
- Integração com dashboards (Power BI, Google Data Studio).
- Notificações automáticas quando houver variações relevantes de preço.
