# Crypto Arbitrage Bot

Professional cryptocurrency arbitrage trading system with Azure integration, AI analysis, and comprehensive monitoring.

## Features

- **Multi-Exchange Support**: Binance, Bybit, Gate.io, Kraken
- **AI-Powered Analysis**: OpenAI integration for intelligent trading decisions
- **Azure Cloud Integration**:
  - Key Vault for secure credential management
  - Storage Accounts & Data Lake for data persistence
  - Application Insights for monitoring
  - Azure SQL for relational data
- **Observability**:
  - OpenTelemetry for distributed tracing
  - Grafana dashboards
  - Prometheus metrics
  - Application Insights integration
- **CI/CD**: Azure DevOps pipelines with automated testing and deployment
- **Containerization**: Docker & Kubernetes ready
- **Infrastructure as Code**: Terraform templates

## Architecture

```
┌─────────────────┐
│   Exchanges     │
│  Binance/Bybit  │
│  Gateio/Kraken  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  Arbitrage Bot  │─────▶│   OpenAI     │
│  (Async Python) │      │   Analysis   │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│         Azure Services              │
│  ┌──────────┐  ┌────────────────┐  │
│  │Key Vault │  │  Storage/Lake  │  │
│  └──────────┘  └────────────────┘  │
│  ┌──────────┐  ┌────────────────┐  │
│  │Azure SQL │  │App Insights    │  │
│  └──────────┘  └────────────────┘  │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│      Monitoring Stack               │
│  Grafana | Prometheus | OTel        │
└─────────────────────────────────────┘
```

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Azure subscription
- Exchange API keys (stored in Azure Key Vault)
- OpenAI API key

## Quick Start

### Local Development

```bash
pip install -r requirements.txt

cp .env.example .env

python -m src.main
```

### Docker

```bash
docker-compose up -d

docker logs -f crypto-arbitrage-bot
```

### Azure Deployment

```bash
cd deployment/terraform
terraform init
terraform apply

az acr build --registry youracr --image crypto-arbitrage-bot:latest .

az container create --resource-group rg-crypto-arbitrage \
  --name crypto-arbitrage-bot \
  --image youracr.azurecr.io/crypto-arbitrage-bot:latest \
  --assign-identity
```

## Configuration

### Environment Variables

- `AZURE_KEY_VAULT_URL`: Key Vault URL for secrets
- `AZURE_STORAGE_CONNECTION_STRING`: Storage account connection
- `AZURE_APPLICATION_INSIGHTS_CONNECTION_STRING`: App Insights
- `AZURE_SQL_CONNECTION_STRING`: SQL database connection
- `AZURE_DATALAKE_ACCOUNT_NAME`: Data Lake account
- `OPENAI_API_KEY`: OpenAI API key

### Azure Key Vault Secrets

Store these secrets in Key Vault:
- `binance-api-key`, `binance-api-secret`
- `bybit-api-key`, `bybit-api-secret`
- `gateio-api-key`, `gateio-api-secret`
- `kraken-api-key`, `kraken-api-secret`
- `openai-api-key`

## Project Structure

```
.
├── src/
│   ├── main.py                 # Main application
│   ├── config.py               # Configuration
│   ├── exchanges/              # Exchange integrations
│   ├── arbitrage/              # Arbitrage logic
│   ├── ai/                     # AI analysis
│   ├── azure/                  # Azure services
│   └── monitoring/             # Telemetry
├── tests/                      # Unit tests
├── deployment/
│   ├── grafana/                # Grafana configs
│   ├── prometheus/             # Prometheus configs
│   ├── otel/                   # OpenTelemetry configs
│   ├── kubernetes/             # K8s manifests
│   ├── terraform/              # IaC templates
│   └── sql/                    # SQL schemas
├── Dockerfile
├── docker-compose.yml
├── azure-pipelines.yml
└── requirements.txt
```

## Monitoring

### Grafana Dashboards

Access at `http://localhost:3000` (default credentials: admin/admin)

- Arbitrage opportunities tracking
- Profit distribution analysis
- Exchange performance metrics
- System health monitoring

### Application Insights

Query examples:

```kusto
customEvents
| where name == "arbitrage_opportunity_simulated"
| project timestamp, properties

customMetrics
| where name == "arbitrage_profit_percent"
| summarize avg(value), max(value) by bin(timestamp, 1h)
```

## CI/CD Pipeline

Azure DevOps pipeline stages:

1. **Build**: Install dependencies, run linters, execute tests
2. **Docker Build**: Build and push Docker image to ACR
3. **Deploy**: Deploy to Azure Container Instances
4. **Integration Tests**: Validate deployment

## Testing

```bash
pytest tests/ -v --cov=src

black --check src/

docker run --rm crypto-arbitrage-bot pytest
```

## Database Schema

Key tables:
- `arbitrage_opportunities`: Discovered opportunities
- `trades`: Executed trades
- `market_data`: Real-time market data

Views:
- `v_best_opportunities`: Top opportunities by profit
- `v_exchange_performance`: Exchange statistics

## Security

- All credentials stored in Azure Key Vault
- Managed Identity for Azure authentication
- Encrypted connections to exchanges
- No hardcoded secrets in code

## Performance

- Async I/O for concurrent exchange queries
- Connection pooling
- Rate limiting compliance
- Efficient data storage in Data Lake

## License

MIT License

## Support

For technical interview demonstration purposes.

