# FinPulse - Project Report
**Assignment**: AlgoLabs - 1  
**Project**: Stock Market Monitoring Platform

## 1. Project Architecture
The FinPulse application follows a clean 3-tier architecture to ensure modularity and scalability:
- **Data Layer (SQLite)**: A relational database (`finpulse.db`) stores tracked tickers, fundamental data (Market Cap, P/E, EPS), and historical daily prices. It uses foreign keys and cascading deletes to maintain data integrity.
- **Backend API (FastAPI)**: Serves as the intermediary between the database/data-sources and the frontend. It exposes RESTful endpoints, handles dynamic ticker additions, performs data validation, and manages asynchronous background tasks (for fetching large historical datasets without blocking the API).
- **Frontend (Streamlit)**: A highly interactive, multi-tab web application that consumes the FastAPI endpoints to render dynamic charts, metrics, and manage user portfolios.

## 2. APIs and Libraries Used
- **yFinance**: Used as the primary data ingestion source to fetch real-time and historical financial data from Yahoo Finance.
- **FastAPI / Uvicorn**: Chosen for building a high-performance REST API with automatic Swagger documentation.
- **Streamlit**: Selected for rapid development of the frontend dashboard and handling UI state.
- **Plotly, Seaborn, Matplotlib**: Leveraged for rich visualizations like Candlestick charts, bar charts, and correlation heatmaps.
- **Pandas**: Crucial for data wrangling, moving average calculations, and managing time-series data.

## 3. Database Design
The SQLite database consists of three interconnected tables:
1. `tracked_tickers`: `ticker (TEXT PRIMARY KEY)` - Stores the master list of tracked stocks.
2. `fundamental_data`: `ticker (PK/FK), name, sector, market_cap, pe_ratio, eps, current_price` - Stores snapshot fundamentals.
3. `historical_prices`: `ticker (FK), date (TEXT), open, high, low, close, volume` - Stores daily price action. Composite Primary Key on `(ticker, date)`.

## 4. Features Implemented
The project fulfills all MVP requirements and heavily incorporates the requested bonus features:
- **Dynamic Watchlist**: Add/remove any listed NSE/BSE stock dynamically; no hardcoded lists.
- **Dashboard**: Displays key metrics and Interactive Candlestick Charts with Volume Overlays.
- **Screener**: Custom sliders to filter stocks based on P/E Ratio and Market Cap.
- **AI-Powered Insights**: A mock AI engine that uses 50-day Moving Averages to predict Bullish/Bearish trends.
- **Comparisons**: Sector-wise pie charts, Market Cap bar charts, and a Financial Ratio Heatmap.
- **Portfolio Tracker**: Allows users to input mock shares owned and calculates total portfolio value.
- **Exportable Reports**: Generates and downloads a CSV report of the tracked portfolio.
- **Authentication & Aesthetics**: Simple password gateway and native Streamlit Dark Mode.

## 5. Challenges Faced
- **Data Retrieval Delays**: Fetching years of historical data for newly added tickers could cause timeout issues on the frontend. *Solution*: Utilized FastAPI's `BackgroundTasks` to fetch historical data asynchronously, returning an immediate success response for fundamental data to keep the UI snappy.
- **Data Quality (yFinance)**: `yfinance` occasionally returns empty data or lacks specific metrics (like P/E) for certain illiquid Indian stocks. *Solution*: Added robust error handling and null-coalescing defaults (falling back to `0` or `"Unknown"`) to prevent the dashboard from crashing.

## 6. Future Improvements
- **Migration to PostgreSQL/Supabase**: While SQLite is great for MVPs, a production environment tracking hundreds of stocks simultaneously across many users would benefit from PostgreSQL.
- **Real-time WebSockets**: Replacing static API polling with WebSockets for live, ticking price updates.
- **Proper User Authentication**: Integrating OAuth2 or JWT-based authentication for multi-tenant portfolio tracking.
- **Advanced ML Models**: Replacing the simple moving-average insights with actual predictive ML models (e.g., LSTMs or XGBoost) for price forecasting.
