# 🚀 AlphaForge Trading System

**Institutional-Grade Algorithmic Trading System powered by Python, Docker, and Gemini AI.**

AlphaForge is a sophisticated automated trading platform designed for the OANDA brokerage ecosystem. It leverages multi-timeframe technical analysis, adaptive market regime detection, and Large Language Model (LLM) validation to generate high-probability trading signals.

![System Status](https://img.shields.io/badge/System-Operational-green)
![Python](https://img.shields.io/badge/Backend-Python_3.11-blue)
![React](https://img.shields.io/badge/Frontend-React_18-cyan)
![Docker](https://img.shields.io/badge/Deployment-Docker-blue)
![AI](https://img.shields.io/badge/AI-Gemini_Pro-orange)

---

## 🌟 Key Features

### 🧠 Intelligent Analysis
*   **Multi-Timeframe Confluence:** Simultaneously analyzes M5, M15, and H1 timeframes to confirm trends.
*   **Adaptive Regime Detection:** Automatically identifies market conditions (Trending Bullish/Bearish, Ranging, Volatile) and adjusts strategy parameters dynamically.
*   **Gemini AI Validation:** Uses Google's Gemini Pro AI to validate technical setups, filtering out false positives based on complex pattern recognition.

### ⚡ Robust Architecture
*   **Microservices Design:** Separated Backend (FastAPI) and Scheduler (Strategy Engine) containers.
*   **Dockerized Deployment:** Fully containerized for consistent deployment across any environment (Local/VPS/Cloud).
*   **Resilient Networking:** Internal Docker network for secure inter-service communication.
*   **Automated Recovery:** Self-healing containers with automatic restart policies.

### 📊 Comprehensive Monitoring
*   **Real-Time Dashboard:** React-based frontend for monitoring active signals and system health.
*   **Telegram Integration:** Instant notifications for new signals and trade management updates.
*   **Detailed Logging:** Extensive logging of all analysis cycles and decision logic.

---

## 🏗️ System Architecture

```mermaid
graph TD
    User[User / Frontend] -->|HTTP| Nginx[Nginx Reverse Proxy]
    Nginx -->|API Requests| Backend[Backend API (FastAPI)]
    
    subgraph Docker Network
        Backend
        Scheduler[Signal Scheduler]
        DB[(SQLite Database)]
    end
    
    Scheduler -->|Generate Signals| Backend
    Scheduler -->|Fetch Data| OANDA[OANDA API]
    Scheduler -->|Validate| Gemini[Gemini AI]
    Backend -->|Store/Retrieve| DB
```

---

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   OANDA Trading Account (Demo or Live)
*   Google Cloud API Key (for Gemini AI)

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/sadaru2002/AlphaForge.git
    cd AlphaForge
    ```

2.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```env
    # OANDA Configuration
    OANDA_API_KEY=your_oanda_key
    OANDA_ACCOUNT_ID=your_account_id
    OANDA_BASE_URL=https://api-fxpractice.oanda.com/v3
    
    # AI Configuration
    GEMINI_API_KEY=your_gemini_key
    
    # System
    FLASK_ENV=production
    ```

3.  **Deploy with Docker**
    ```bash
    # Build and start services
    docker-compose up -d --build
    ```

4.  **Access the System**
    *   **Backend API:** `http://localhost:5000`
    *   **Health Check:** `http://localhost:5000/health`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health status |
| `GET` | `/api/status` | Detailed component status |
| `GET` | `/api/signals` | Retrieve generated signals |
| `POST` | `/api/signals/enhanced/generate` | Trigger manual analysis cycle |

---

## 🛡️ Risk Disclaimer

*Trading Forex and CFDs carries a high level of risk and may not be suitable for all investors. The high degree of leverage can work against you as well as for you. Before deciding to trade, you should carefully consider your investment objectives, level of experience, and risk appetite. The possibility exists that you could sustain a loss of some or all of your initial investment.*

---

© 2025 AlphaForge. All Rights Reserved.
