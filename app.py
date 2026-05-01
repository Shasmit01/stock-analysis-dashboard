import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
from data_fetcher import fetch_stock_data
from data_cleaner import clean_stock_data, get_portfolio_stats
import pandas as pd
from datetime import datetime

app = dash.Dash(__name__)

PORTFOLIO = ["AAPL", "MSFT", "JPM", "JNJ", "XOM"]

print("Loading stock data...")
using_live_data = True

try:
    raw_data = fetch_stock_data(PORTFOLIO, period_years=3)
    if not raw_data or len(raw_data) < len(PORTFOLIO):
        raise ValueError(f"Only got data for {len(raw_data)}/{len(PORTFOLIO)} tickers")
    cleaned_data = clean_stock_data(raw_data)
    portfolio_stats = get_portfolio_stats(cleaned_data)
    print("[OK] Live data loaded successfully")
except Exception as e:
    print(f"[WARN] Live data failed: {e}. Falling back to mock data.")
    using_live_data = False
    from data_fetcher_mock import fetch_stock_data as fetch_mock
    raw_data = fetch_mock(PORTFOLIO, period_years=3)
    cleaned_data = clean_stock_data(raw_data)
    portfolio_stats = get_portfolio_stats(cleaned_data)

combined_df = pd.concat(
    [cleaned_data[ticker] for ticker in PORTFOLIO],
    ignore_index=False
)

data_source_label = "Real-time data from Yahoo Finance" if using_live_data else "Sample data (live data unavailable)"
data_source_color = "#28a745" if using_live_data else "#ff6b6b"

app.layout = html.Div([
    html.Div([
        html.H1("Stock Portfolio Dashboard", style={'textAlign': 'center', 'marginBottom': 10}),
        html.P(data_source_label,
               style={'textAlign': 'center', 'color': data_source_color, 'fontSize': '14px', 'marginBottom': 10}),
        html.P(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
               style={'textAlign': 'center', 'color': '#666'}),
    ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'marginBottom': '30px'}),

    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0),

    html.Div([
        html.Div([
            html.Div([
                html.H3(ticker, style={'color': '#1f77b4', 'marginBottom': 5}),
                html.P(f"Price: ${portfolio_stats.loc[ticker, 'Current_Price']:.2f}",
                       style={'fontSize': '16px', 'fontWeight': 'bold'}),
                html.P(f"3Y Return: {portfolio_stats.loc[ticker, 'Total_Return_3Y']*100:.2f}%",
                       style={'color': 'green' if portfolio_stats.loc[ticker, 'Total_Return_3Y'] > 0 else 'red'}),
                html.P(f"Volatility: {portfolio_stats.loc[ticker, 'Annual_Volatility']*100:.2f}%",
                       style={'fontSize': '12px', 'color': '#666'}),
            ], style={
                'backgroundColor': '#fff',
                'padding': '15px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'border': '1px solid #ddd'
            })
            for ticker in PORTFOLIO
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(150px, 1fr))',
            'gap': '15px',
            'marginBottom': '30px'
        }),
    ], style={'padding': '0 20px'}),

    html.Div([
        html.Div([dcc.Graph(id='price-chart')], style={'flex': '1'}),
        html.Div([dcc.Graph(id='returns-chart')], style={'flex': '1'}),
    ], style={'display': 'flex', 'gap': '20px', 'padding': '0 20px', 'marginBottom': '30px'}),

    html.Div([
        html.Div([dcc.Graph(id='volatility-chart')], style={'flex': '1'}),
        html.Div([dcc.Graph(id='ma-chart')], style={'flex': '1'}),
    ], style={'display': 'flex', 'gap': '20px', 'padding': '0 20px'}),

], style={'backgroundColor': '#fff', 'fontFamily': 'Arial, sans-serif'})

@callback(Output('price-chart', 'figure'), Input('interval-component', 'n_intervals'))
def update_price_chart(n):
    fig = go.Figure()
    for ticker in PORTFOLIO:
        df = cleaned_data[ticker]
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Adj Close'], mode='lines', name=ticker,
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x|%Y-%m-%d}<br>Price: $%{y:.2f}<extra></extra>'
        ))
    fig.update_layout(
        title='Adjusted Close Prices - 3 Year History',
        xaxis_title='Date', yaxis_title='Price (USD)',
        hovermode='x unified', plot_bgcolor='#f8f9fa', height=400
    )
    return fig

@callback(Output('returns-chart', 'figure'), Input('interval-component', 'n_intervals'))
def update_returns_chart(n):
    fig = go.Figure()
    for ticker in PORTFOLIO:
        df = cleaned_data[ticker]
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Cumulative_Return'] * 100, mode='lines', name=ticker,
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x|%Y-%m-%d}<br>Return: %{y:.2f}%<extra></extra>'
        ))
    fig.update_layout(
        title='Cumulative Returns - $100 Investment Growth',
        xaxis_title='Date', yaxis_title='Return (%)',
        hovermode='x unified', plot_bgcolor='#f8f9fa', height=400
    )
    return fig

@callback(Output('volatility-chart', 'figure'), Input('interval-component', 'n_intervals'))
def update_volatility_chart(n):
    fig = go.Figure()
    for ticker in PORTFOLIO:
        df = cleaned_data[ticker]
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Volatility'] * 100, mode='lines', name=ticker,
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x|%Y-%m-%d}<br>Volatility: %{y:.2f}%<extra></extra>'
        ))
    fig.update_layout(
        title='Rolling 20-Day Volatility - Risk Indicator',
        xaxis_title='Date', yaxis_title='Volatility (%)',
        hovermode='x unified', plot_bgcolor='#f8f9fa', height=400
    )
    return fig

@callback(Output('ma-chart', 'figure'), Input('interval-component', 'n_intervals'))
def update_ma_chart(n):
    ticker = "AAPL"
    df = cleaned_data[ticker]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Adj Close'], mode='lines', name='Price', line=dict(color='black', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_20'], mode='lines', name='20-Day MA', line=dict(color='orange', dash='dash')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_50'], mode='lines', name='50-Day MA', line=dict(color='red', dash='dash')))
    fig.update_layout(
        title=f'{ticker} Price with Moving Averages',
        xaxis_title='Date', yaxis_title='Price (USD)',
        hovermode='x unified', plot_bgcolor='#f8f9fa', height=400
    )
    return fig

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Starting Dashboard...")
    print("="*50 + "\n")
    app.run_server(debug=False, host='0.0.0.0', port=5000)
