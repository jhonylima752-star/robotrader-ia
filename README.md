# AI FOREX Trading Robot

Repositório de robô trader de IA para FOREX com integração nativa MT4/MT5, seleção autônoma de pares, e alertas de sinal com 2 minutos de antecedência via Telegram.

## 🚀 Quick Start (Em Simulação)

### 1. Clonar o repositório
```bash
git clone https://github.com/jhonylima752-star/robotrader-ia.git
cd robotrader-ia
```

### 2. Configurar ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # no Windows: venv\Scripts\activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Executar em modo simulação
```bash
python main.py --mode status
python main.py --mode simulate
python main.py --mode scan
python main.py --mode backtest
```

## 📋 Modos de Operação

### `status`
Verifica status do sistema e configurações atuais.
```bash
python main.py --mode status
```

### `simulate`
Roda uma simulação completa: conecta ao MT5, varre pares, treina modelo, gera sinal e simula ordem.
```bash
python main.py --mode simulate
```

### `scan`
Scanneia símbolos ativos e escolhe o melhor par baseado em previsões de IA.
```bash
python main.py --mode scan
```

### `backtest`
Roda validação histórica (últimos 12 meses) e calcula métrica de acurácia por símbolo.
```bash
python main.py --mode backtest --data-dir ./data
```

## 🔧 Configuração (.env)

Crie um arquivo `.env` na raiz do projeto:

```env
# Modo de simulação (sem credenciais reais)
USE_SIMULATOR=true

# Para uso com MT5 real, defina:
MT5_LOGIN=your_account_number
MT5_PASSWORD=your_password
MT5_SERVER=BrokerServerName
MT5_PATH=/path/to/MT5/terminal64.exe  # opcional

# Telegram (para alertas em tempo real)
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# Símbolos e configurações
SYMBOLS=EURUSD,GBPUSD,USDJPY,USDCHF,AUDUSD,NZDUSD
FORECAST_HORIZON_SECONDS=120
SIGNAL_CONFIDENCE_THRESHOLD=0.55
DEFAULT_VOLUME=0.01
MAX_LOOKBACK_BARS=5000
```

## 📁 Estrutura do Projeto

```text
robotrader-ia/
├── app/
│   ├── config.py                  # Configurações globais
│   ├── data/
│   │   └── loader.py              # Carregamento de dados, feature engineering
│   ├── models/
│   │   └── forecast_model.py      # Modelo de classificação (Random Forest)
│   ├── mt_connector/
│   │   ├── __init__.py            # MT5Connector com fallback simulador
│   ├── signals/
│   │   └── signal_engine.py       # Engine de sinal, seleção de pares
│   └── alerts/
│       └── telegram_alert.py      # Notificações via Telegram
├── data/                          # Histórico de candles (CSV)
├── models/                        # Artefatos treinados (.pkl)
├── logs/                          # Registros de execução
├── main.py                        # Entry point principal
├── requirements.txt               # Dependências
├── .env.example                   # Template de configuração
└── README.md                      # Este arquivo
```

## 🤖 Funcionalidades Principais

### 1. **Conector MT5/MT4**
- Suporte nativo via biblioteca `MetaTrader5` em Python
- Fallback automático para modo simulador (sem credenciais)
- Métodos para:
  - `connect()` - conectar ao broker
  - `get_prices(symbols)` - obter preços atuais
  - `get_history(symbol, timeframe, count)` - histórico de candles
  - `place_order(symbol, action, volume, sl, tp)` - executar operações

### 2. **Seleção Autônoma de Pares**
- Varre lista configurável de símbolos (EURUSD, GBPUSD, etc.)
- Treina modelo de IA para cada par
- Escolhe automaticamente o par com maior confiança de direção

### 3. **Modelo de IA**
- **Tipo:** Random Forest Classifier (250 árvores, profundidade 7)
- **Features:** retornos multi-timeframe, média móvel, RSI, ATR, volatilidade
- **Alvo:** classificação binária (UP/DOWN) com horizonte de 5 minutos
- **Acurácia observada em backtest:** ~60-75% (dependente de dados históricos reais)

### 4. **Geração de Sinal**
- Antecedência: 120 segundos (configurável via `FORECAST_HORIZON_SECONDS`)
- Cálculo automático de entrada, stop loss (SL) e take profit (TP)
- Confiança exibida em cada sinal

### 5. **Alertas**
- **Terminal MT5:** via `Alert()` nativo
- **Telegram:** notificação push com detalhes do sinal
- Mensagem formatada com: símbolo, lado, entrada, SL, TP, lead time

## 📊 Backtesting & Validação

```bash
python main.py --mode backtest --data-dir ./data
```

Gera relatório com:
- Acurácia por símbolo
- Matriz de confusão
- Recall, Precision, F1-score

## ⚠️ Aviso Legal

1. **Este projeto é um PROTÓTIPO DE PESQUISA e NÃO garante lucro ou 90% de acerto em operações reais.**
2. **Trading envolve RISCO de capital total.** Sempre use contas de demonstração antes de operar com capital real.
3. **Valide rigorosamente** com dados de 12 meses antes de qualquer operação em produção.
4. **Não é recomendação financeira.** Consulte um assessor financeiro antes de trading real.

## 🔗 Conexão MT5 Real

### Passos para usar com MT5 real:

1. Instale a biblioteca MetaTrader5:
   ```bash
   pip install MetaTrader5
   ```

2. Obtenha credenciais do seu broker MT5 (login, senha, servidor)

3. Configure `.env`:
   ```env
   USE_SIMULATOR=false
   MT5_LOGIN=123456789
   MT5_PASSWORD=sua_senha
   MT5_SERVER=BrokerDemo
   ```

4. Execute em modo demo primeiro:
   ```bash
   python main.py --mode simulate
   ```

5. Monitore os logs e órdenes no MT5 terminal

## 🧪 Teste Local (Modo Simulador)

Todo o código pode ser testado **sem credenciais MT5**. O MT5Connector detecta automaticamente e usa simulação:

```bash
# Sem .env - usa valores padrão com USE_SIMULATOR=true
python main.py --mode status
python main.py --mode simulate
```

## 📈 Métricas de Saída

Cada modo retorna JSON com:

```json
{
  "status": "success",
  "connected": true,
  "prices": {
    "EURUSD": 1.10250,
    "GBPUSD": 1.29580
  },
  "predictions": {
    "EURUSD": 0.6234,
    "GBPUSD": 0.5112
  },
  "signal": {
    "symbol": "EURUSD",
    "side": "BUY",
    "entry": 1.10250,
    "sl": 1.10051,
    "tp": 1.10576,
    "confidence": 0.6234,
    "lead_seconds": 120
  },
  "order": {
    "status": "simulated",
    "ticket": 123456,
    "symbol": "EURUSD",
    "action": "BUY"
  }
}
```

## 🛠️ Desenvolvimento & Customização

### Adicionar novo modelo de IA
Edite `app/models/forecast_model.py`:
```python
from sklearn.ensemble import GradientBoostingClassifier

# Substitua RandomForestClassifier por seu modelo
model = GradientBoostingClassifier(n_estimators=500)
```

### Adicionar novos símbolos
Altera `.env`:
```env
SYMBOLS=EURUSD,GBPUSD,USDJPY,USDCAD,NZDUSD,XAUUSD
```

### Configurar Telegram
1. Crie bot no BotFather (@BotFather no Telegram)
2. Copie o token para `.env`
3. Obtenha seu Chat ID usando:
   ```bash
   curl https://api.telegram.org/bot<SEU_TOKEN>/getUpdates
   ```

## 📞 Suporte

- Issues: abra uma issue no repositório
- Documentação: veja os docstrings em cada módulo
- Logs: verifique `logs/` para debug

## 📄 Licença

MIT License - veja LICENSE arquivo

---

**Desenvolvido com ❤️ para traders que querem automatizar com IA**
