# Architecture Documentation

## System Overview

Stock Screener Agent is a multi-agent system designed for AI-powered stock screening. The system follows a modular architecture with clear separation of concerns.

## Components

### 1. Agent Layer

#### Base Agent
- Abstract base class for all agents
- Provides common functionality:
  - Input validation
  - Logging
  - Error handling

#### Data Fetcher Agent
- **Responsibility**: Retrieve fundamental stock data
- **Data Sources**:
  - Yahoo Finance (yfinance)
  - Finnhub API (optional)
- **Output**: Structured fundamental data for each stock

#### Analysis Agent
- **Responsibility**: AI-powered stock analysis
- **Technology**: OpenAI GPT models
- **Process**:
  1. Receives fundamental data
  2. Constructs detailed analysis prompts
  3. Calls OpenAI API
  4. Extracts structured insights
- **Output**: AI-generated investment thesis and recommendations

#### Ranking Agent
- **Responsibility**: Score and rank stocks
- **Scoring Components**:
  - Growth metrics (30 points)
  - Valuation metrics (25 points)
  - Financial health (20 points)
  - AI analysis (25 points)
- **Output**: Ranked list of stocks with detailed breakdowns

#### Multi-Agent Coordinator
- **Responsibility**: Orchestrate the workflow
- **Features**:
  - Sequential processing
  - Parallel batch processing
  - Error handling and recovery
- **Output**: Complete screening results

### 2. API Layer

#### Flask REST API
- **Purpose**: Expose screening functionality via HTTP
- **Endpoints**:
  - `/health`: Health check
  - `/api/screen`: Custom stock screening
  - `/api/screen/quick`: Pre-defined universe screening

### 3. CLI Layer

#### Command-Line Interface
- **Purpose**: Direct command-line access
- **Features**:
  - Stock symbol input
  - Custom parameters
  - Result export to JSON
  - Formatted table output

### 4. Integration Layer

#### n8n Workflows
- **Purpose**: Automation and integration
- **Workflows**:
  - Webhook-triggered screening
  - Scheduled daily screening
  - Email notifications
  - Google Sheets integration

### 5. Utility Layer

#### Cache Manager
- **Purpose**: Reduce API calls and improve performance
- **Features**:
  - TTL-based caching
  - Automatic expiration
  - Cache cleanup

#### Validators
- **Purpose**: Input validation
- **Functions**:
  - Symbol validation
  - Configuration validation

## Data Flow

```
Input (Stock Symbols)
        ↓
Multi-Agent Coordinator
        ↓
┌───────┴───────┐
│               │
Data Fetcher    │
│               │
└───────┬───────┘
        ↓
  [Stock Data]
        ↓
   Analysis Agent
        ↓
  [AI Analysis]
        ↓
   Ranking Agent
        ↓
  [Ranked Results]
        ↓
Output (Top Picks)
```

## Scalability Considerations

### Current Implementation
- Synchronous processing with async support
- Batch processing for parallel execution
- Single-server deployment

### Future Enhancements
- Distributed processing with task queues (Celery)
- Redis caching for multi-instance deployments
- Kubernetes orchestration
- Horizontal scaling of API servers

## Security Considerations

### Current Implementation
- Environment variable-based configuration
- No authentication required
- Input validation

### Production Recommendations
- Implement API authentication
- Rate limiting
- HTTPS/TLS encryption
- Secrets management (AWS Secrets Manager, HashiCorp Vault)
- Input sanitization
- CORS configuration

## Monitoring and Logging

### Current Implementation
- File-based logging with Loguru
- Log rotation (daily)
- Log retention (7 days)
- Structured logging

### Production Recommendations
- Centralized logging (ELK stack, CloudWatch)
- Application Performance Monitoring (APM)
- Error tracking (Sentry)
- Metrics collection (Prometheus)
- Dashboards (Grafana)

## Configuration Management

### Environment Variables
All configuration is managed through environment variables:
- API credentials
- Model selection
- Screening parameters
- Server configuration

### Best Practices
- Use `.env` files for local development
- Use secrets management for production
- Separate configs per environment
- Version control `.env.example`
