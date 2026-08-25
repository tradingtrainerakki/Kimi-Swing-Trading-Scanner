"""
Swing Trading Screener - Nifty 150
Technical + Fundamental 8-Factor Framework
Deploy on Streamlit Cloud
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Page config
st.set_page_config(
    page_title="Swing Trading Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stock-card {
        background: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .stock-card-weak { border-left-color: #dc3545; }
    .stock-card-moderate { border-left-color: #ffc107; }
    .info-box {
        background: #e7f3ff;
        border: 1px solid #b8daff;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .fundamental-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .score-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .score-green { background: #d4edda; color: #155724; }
    .score-yellow { background: #fff3cd; color: #856404; }
    .score-red { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# Nifty 150 Stock Universe
NIFTY_150_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "BAJFINANCE.NS",
    "TITAN.NS", "WIPRO.NS", "NESTLEIND.NS", "ULTRACEMCO.NS", "SUNPHARMA.NS",
    "HCLTECH.NS", "ADANIENT.NS", "POWERGRID.NS", "NTPC.NS", "ONGC.NS",
    "TATAMOTORS.NS", "COALINDIA.NS", "ADANIPORTS.NS", "BAJAJFINSV.NS", "M&M.NS",
    "TECHM.NS", "GRASIM.NS", "CIPLA.NS", "BRITANNIA.NS", "DRREDDY.NS",
    "APOLLOHOSP.NS", "EICHERMOT.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "HEROMOTOCO.NS",
    "INDUSINDBK.NS", "HDFCLIFE.NS", "SBILIFE.NS", "BPCL.NS", "DIVISLAB.NS",
    "HINDALCO.NS", "UPL.NS", "TATACONSUM.NS", "SBICARD.NS", "DABUR.NS",
    "ADANIGREEN.NS", "ADANIPOWER.NS", "ATGL.NS", "AWL.NS", "BAJAJ-AUTO.NS",
    "BANKBARODA.NS", "BERGEPAINT.NS", "BEL.NS", "CANBK.NS", "CHOLAFIN.NS",
    "COLPAL.NS", "CONCOR.NS", "CUMMINSIND.NS", "DLF.NS", "DMART.NS",
    "GAIL.NS", "GODREJCP.NS", "GODREJPROP.NS", "HAL.NS", "HAVELLS.NS",
    "HDFCAMC.NS", "HINDPETRO.NS", "HINDZINC.NS", "IDFCFIRSTB.NS", "INDIGO.NS",
    "IOC.NS", "IRCTC.NS", "JINDALSTEL.NS", "JUBLFOOD.NS", "LICI.NS",
    "LODHA.NS", "MCDOWELL-N.NS", "MOTHERSON.NS", "MUTHOOTFIN.NS", "NAUKRI.NS",
    "NHPC.NS", "NMDC.NS", "OBEROIRLTY.NS", "PAYTM.NS", "PIDILITIND.NS",
    "PNB.NS", "POLYCAB.NS", "RECLTD.NS", "SHREECEM.NS", "SIEMENS.NS",
    "SRF.NS", "TATAPOWER.NS", "TORNTPHARM.NS", "TVSMOTOR.NS", "VEDL.NS",
    "ZOMATO.NS", "ZYDUSLIFE.NS", "AMBUJACEM.NS", "BOSCHLTD.NS", "DEEPAKNTR.NS",
    "ESCORTS.NS", "FEDERALBNK.NS", "GLAND.NS", "GUJGASLTD.NS", "ICICIGI.NS",
    "ICICIPRULI.NS", "INDUSTOWER.NS", "LUPIN.NS", "MARICO.NS", "MFSL.NS",
    "MRF.NS", "PAGEIND.NS", "PEL.NS", "PFC.NS", "PIIND.NS",
    "RAMCOCEM.NS", "SAIL.NS", "TATACOMM.NS", "TORNTPOWER.NS", "TRENT.NS",
    "VBL.NS", "YESBANK.NS", "AUBANK.NS", "ABB.NS", "ALKEM.NS",
    "BANDHANBNK.NS", "BATAINDIA.NS", "BHARATFORG.NS", "CGPOWER.NS", "COROMANDEL.NS",
    "CROMPTON.NS", "DIXON.NS", "FLUOROCHEM.NS", "GLENMARK.NS", "HONAUT.NS",
    "IDBI.NS", "IGL.NS", "INDHOTEL.NS", "IRFC.NS", "JSL.NS",
    "KEI.NS", "LALPATHLAB.NS", "LAURUSLABS.NS", "LINDEINDIA.NS", "MANAPPURAM.NS",
    "MAXHEALTH.NS", "METROBRAND.NS", "MINDTREE.NS", "MPHASIS.NS", "OFSS.NS",
    "PERSISTENT.NS", "PETRONET.NS", "PHOENIXLTD.NS", "RBLBANK.NS", "RENUKA.NS",
    "SANOFI.NS", "SJVN.NS", "SOLARINDS.NS", "SONACOMS.NS", "SUMICHEM.NS",
    "SUPREMEIND.NS", "SYNGENE.NS", "TANLA.NS", "TIMKEN.NS", "UBL.NS",
    "UNOMINDA.NS", "VOLTAS.NS", "WHIRLPOOL.NS", "WOCKPHARMA.NS", "3MINDIA.NS"
]

@st.cache_data(ttl=3600)
def fetch_stock_data(ticker, period="1y"):
    """Fetch historical price data for a single stock"""
    try:
        data = yf.download(ticker, period=period, interval="1d", progress=False)
        if data.empty or len(data) < 200:
            return None
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_fundamental_data(ticker):
    """Fetch fundamental data from yfinance info"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info:
            return None
        return {
            'roe': info.get('returnOnEquity'),
            'debt_to_equity': info.get('debtToEquity'),
            'earnings_growth': info.get('earningsGrowth'),
            'revenue_growth': info.get('revenueGrowth'),
            'institutional_holding': info.get('heldPercentInstitutions'),
            'promoter_holding': info.get('heldPercentInsiders'),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
        }
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_nifty_data():
    """Fetch Nifty 50 index data for RS calculation"""
    try:
        data = yf.download("^NSEI", period="1y", interval="1d", progress=False)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except:
        return None

def calculate_technical_indicators(df, nifty_df=None):
    """Calculate all 4 technical indicators"""
    if df is None or len(df) < 200:
        return None

    required = ['Close', 'High', 'Low', 'Volume']
    for col in required:
        if col not in df.columns:
            return None

    latest_close = float(df['Close'].iloc[-1])
    latest_volume = float(df['Volume'].iloc[-1])
    prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else latest_close

    # Moving Averages
    df['MA50'] = df['Close'].rolling(window=50).mean()
    df['MA200'] = df['Close'].rolling(window=200).mean()
    ma50 = float(df['MA50'].iloc[-1])
    ma200 = float(df['MA200'].iloc[-1])

    price_above_50 = latest_close > ma50
    ma50_above_200 = ma50 > ma200
    trend_score = int(price_above_50) + int(ma50_above_200)
    trend_pass = price_above_50 and ma50_above_200

    # ATR%
    df['TR1'] = df['High'] - df['Low']
    df['TR2'] = abs(df['High'] - df['Close'].shift(1))
    df['TR3'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['TR1', 'TR2', 'TR3']].max(axis=1)
    df['ATR14'] = df['TR'].rolling(window=14).mean()
    atr = float(df['ATR14'].iloc[-1])
    atr_pct = (atr / latest_close) * 100 if latest_close > 0 else 0

    # RS vs Nifty
    rs_6m = None
    rs_3m = None
    if nifty_df is not None and len(nifty_df) >= 126 and len(df) >= 126:
        try:
            nifty_6m = float(nifty_df['Close'].iloc[-1] / nifty_df['Close'].iloc[-126] - 1) * 100
            stock_6m = float(df['Close'].iloc[-1] / df['Close'].iloc[-126] - 1) * 100
            rs_6m = stock_6m - nifty_6m

            nifty_3m = float(nifty_df['Close'].iloc[-1] / nifty_df['Close'].iloc[-63] - 1) * 100
            stock_3m = float(df['Close'].iloc[-1] / df['Close'].iloc[-63] - 1) * 100
            rs_3m = stock_3m - nifty_3m
        except:
            pass

    # Volume
    df['Vol20'] = df['Volume'].rolling(window=20).mean()
    vol20 = float(df['Vol20'].iloc[-1])
    vol_pass = latest_volume > vol20
    vol_ratio = latest_volume / vol20 if vol20 > 0 else 0

    tech_score = trend_score
    if rs_6m is not None and rs_6m > 0:
        tech_score += 1
    if vol_pass:
        tech_score += 1

    return {
        'price': latest_close,
        'prev_close': prev_close,
        'daily_change_pct': ((latest_close / prev_close) - 1) * 100,
        'ma50': ma50,
        'ma200': ma200,
        'price_above_50': price_above_50,
        'ma50_above_200': ma50_above_200,
        'trend_pass': trend_pass,
        'trend_score': trend_score,
        'atr': atr,
        'atr_pct': atr_pct,
        'rs_6m': rs_6m,
        'rs_3m': rs_3m,
        'volume': latest_volume,
        'vol20_avg': vol20,
        'vol_ratio': vol_ratio,
        'vol_pass': vol_pass,
        'tech_score': tech_score,
    }

def calculate_fundamental_score(fund_data, filters):
    """Calculate fundamental score based on filters"""
    if fund_data is None:
        return {'fund_score': 0, 'fund_pass_count': 0, 'details': {}}

    score = 0
    passed = 0
    details = {}

    # ROE > threshold
    roe = fund_data.get('roe')
    if roe is not None:
        roe_pct = roe * 100  # yfinance returns as decimal
        roe_pass = roe_pct >= filters['min_roe']
        if roe_pass:
            score += 1
            passed += 1
        details['roe'] = round(roe_pct, 2)
        details['roe_pass'] = roe_pass
    else:
        details['roe'] = None
        details['roe_pass'] = False

    # Earnings Growth > threshold (proxy for PAT growth)
    eg = fund_data.get('earnings_growth')
    if eg is not None:
        eg_pct = eg * 100
        eg_pass = eg_pct >= filters['min_pat_growth']
        if eg_pass:
            score += 1
            passed += 1
        details['pat_growth'] = round(eg_pct, 2)
        details['pat_growth_pass'] = eg_pass
    else:
        details['pat_growth'] = None
        details['pat_growth_pass'] = False

    # Debt to Equity < threshold
    de = fund_data.get('debt_to_equity')
    if de is not None:
        de_ratio = de / 100  # yfinance returns as percentage
        de_pass = de_ratio <= filters['max_debt_equity']
        if de_pass:
            score += 1
            passed += 1
        details['debt_equity'] = round(de_ratio, 2)
        details['debt_equity_pass'] = de_pass
    else:
        details['debt_equity'] = None
        details['debt_equity_pass'] = False

    # Institutional Holding >= threshold (proxy for FII+DII)
    ih = fund_data.get('institutional_holding')
    if ih is not None:
        ih_pct = ih * 100
        ih_pass = ih_pct >= filters['min_institutional']
        if ih_pass:
            score += 1
            passed += 1
        details['institutional_pct'] = round(ih_pct, 2)
        details['institutional_pass'] = ih_pass
    else:
        details['institutional_pct'] = None
        details['institutional_pass'] = False

    details['market_cap'] = fund_data.get('market_cap')
    details['pe_ratio'] = fund_data.get('pe_ratio')
    details['pb_ratio'] = fund_data.get('pb_ratio')
    details['sector'] = fund_data.get('sector')

    return {
        'fund_score': score,
        'fund_pass_count': passed,
        'fund_details': details
    }

def screen_stocks(stock_list, tech_filters, fund_filters, progress_bar, status_text):
    """Screen all stocks and return results"""
    results = []
    nifty_df = fetch_nifty_data()

    total = len(stock_list)
    for i, ticker in enumerate(stock_list):
        status_text.text(f"Analyzing {ticker}... ({i+1}/{total})")
        progress_bar.progress((i + 1) / total)

        # Fetch technical data
        price_df = fetch_stock_data(ticker)
        tech_indicators = calculate_technical_indicators(price_df, nifty_df)

        # Fetch fundamental data
        fund_data = fetch_fundamental_data(ticker)
        fund_indicators = calculate_fundamental_score(fund_data, fund_filters)

        if tech_indicators is not None:
            row = {
                'Ticker': ticker.replace('.NS', ''),
                **tech_indicators,
                **fund_indicators,
            }
            # Combined score
            row['total_score'] = row['tech_score'] + row['fund_score']
            row['max_possible'] = 8  # 4 tech + 4 fund
            results.append(row)

        time.sleep(0.15)  # Be nice to Yahoo Finance

    return pd.DataFrame(results)

def main():
    # Header
    st.markdown('<div class="main-header">📈 Swing Trading Screener</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">8-Factor Technical + Fundamental Framework | Nifty 150</div>', unsafe_allow_html=True)

    # Sidebar - Filters
    with st.sidebar:
        st.header("⚙️ Filters")

        # Technical Filters
        st.subheader("📊 Technical Filters")

        min_trend_score = st.slider("Min Trend Score", 0, 2, 1, 
                                     help="0=Weak, 1=Price>50DMA OR 50>200, 2=Price>50>200")
        require_trend_pass = st.checkbox("Require Full Trend (Price>50>200)", value=False)

        max_atr = st.slider("Max ATR% (Volatility)", 0.5, 5.0, 3.0, 0.1,
                           help="Lower = less volatile")

        min_rs = st.slider("Min RS vs Nifty (6M)", -20.0, 20.0, 0.0, 1.0,
                          help="Positive = outperforming Nifty")

        require_volume = st.checkbox("Require Volume > 20-day Avg", value=False)
        min_vol_ratio = st.slider("Min Volume Ratio", 0.5, 3.0, 0.8, 0.1)

        min_tech_score = st.slider("Min Technical Score", 0, 4, 2, 1,
                                  help="Max 4: Trend(2)+RS(1)+Vol(1)")

        st.markdown("---")

        # Fundamental Filters
        st.subheader("🏛️ Fundamental Filters")

        min_roe = st.slider("Min ROE (%)", 5.0, 30.0, 15.0, 1.0,
                           help="Return on Equity threshold")

        min_pat_growth = st.slider("Min PAT/Earnings Growth (%)", 0.0, 50.0, 15.0, 1.0,
                                  help="Earnings growth threshold")

        max_debt_equity = st.slider("Max Debt/Equity Ratio", 0.1, 3.0, 1.0, 0.1,
                                   help="Lower = less debt")

        min_institutional = st.slider("Min Institutional Holding (%)", 5.0, 50.0, 25.0, 1.0,
                                     help="FII + DII proxy via yfinance")

        min_fund_score = st.slider("Min Fundamental Score", 0, 4, 2, 1,
                                  help="Max 4: ROE+PAT Growth+D/E+Institutional")

        st.markdown("---")

        # Combined Score
        st.subheader("🎯 Combined Score")
        min_total_score = st.slider("Min Total Score (Tech+Fund)", 0, 8, 4, 1,
                                   help="Max 8: 4 Technical + 4 Fundamental")

        st.markdown("---")
        st.info("""
        **Note:** FII/DII exact breakdown requires NSE/BSE data. 
        This app uses yfinance's `heldPercentInstitutions` as proxy.
        For exact FII+DII %, integrate NSE data API.
        """)

    # Main content
    col1, col2, col3 = st.columns(3)

    # Run Screener Button
    if st.button("🚀 Run Screener", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        tech_filters = {
            'min_trend_score': min_trend_score,
            'require_trend_pass': require_trend_pass,
            'max_atr': max_atr,
            'min_rs': min_rs,
            'require_volume': require_volume,
            'min_vol_ratio': min_vol_ratio,
            'min_tech_score': min_tech_score,
        }

        fund_filters = {
            'min_roe': min_roe,
            'min_pat_growth': min_pat_growth,
            'max_debt_equity': max_debt_equity,
            'min_institutional': min_institutional,
            'min_fund_score': min_fund_score,
        }

        with st.spinner("Fetching and analyzing Nifty 150 stocks... This may take 3-4 minutes"):
            df_results = screen_stocks(NIFTY_150_STOCKS, tech_filters, fund_filters, progress_bar, status_text)

        if df_results.empty:
            st.error("No data fetched. Please check internet connection or try again later.")
            return

        # Apply all filters
        filtered = df_results.copy()

        # Technical filters
        if require_trend_pass:
            filtered = filtered[filtered['trend_pass'] == True]
        else:
            filtered = filtered[filtered['trend_score'] >= min_trend_score]

        filtered = filtered[filtered['atr_pct'] <= max_atr]

        if 'rs_6m' in filtered.columns:
            filtered = filtered[filtered['rs_6m'].notna()]
            filtered = filtered[filtered['rs_6m'] >= min_rs]

        if require_volume:
            filtered = filtered[filtered['vol_pass'] == True]
        else:
            filtered = filtered[filtered['vol_ratio'] >= min_vol_ratio]

        filtered = filtered[filtered['tech_score'] >= min_tech_score]

        # Fundamental filters
        filtered = filtered[filtered['fund_score'] >= min_fund_score]

        # Combined score
        filtered = filtered[filtered['total_score'] >= min_total_score]

        # Sort by total score descending
        filtered = filtered.sort_values(['total_score', 'tech_score', 'fund_score'], ascending=[False, False, False])

        # Summary metrics
        total_screened = len(df_results)
        total_passed = len(filtered)

        col1.metric("📊 Stocks Screened", total_screened)
        col2.metric("✅ Passed All Filters", total_passed)
        col3.metric("📉 Filtered Out", total_screened - total_passed)

        st.markdown("---")

        if total_passed == 0:
            st.warning("No stocks matched your filter criteria. Try relaxing the filters.")
        else:
            st.success(f"Found **{total_passed}** stocks matching all your criteria!")

            # Top Picks
            st.subheader("🏆 Top Swing Trade Picks")
            top5 = filtered.head(5)

            for idx, (_, row) in enumerate(top5.iterrows()):
                score = row['total_score']
                score_color = "#28a745" if score >= 6 else "#ffc107" if score >= 4 else "#dc3545"

                fund_deets = row['fund_details']

                st.markdown(f"""
                <div style="background: {score_color}10; border-left: 4px solid {score_color}; 
                            padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin:0; color: {score_color};">#{idx+1} {row['Ticker']}</h3>
                        <span class="score-badge score-green">{score}/8</span>
                    </div>
                    <p style="font-size: 1.3rem; font-weight: bold; margin: 0.3rem 0;">
                        ₹{row['price']:.2f} 
                        <span style="font-size: 0.9rem; color: {'#28a745' if row['daily_change_pct'] >= 0 else '#dc3545'};">
                            ({row['daily_change_pct']:+.2f}%)
                        </span>
                    </p>
                    <p style="margin: 0; font-size: 0.9rem;">
                        <b>Tech:</b> {row['tech_score']}/4 | 
                        <b>Fund:</b> {row['fund_score']}/4 | 
                        <b>RS:</b> {row['rs_6m']:+.2f}% | 
                        <b>ATR:</b> {row['atr_pct']:.2f}% | 
                        <b>Vol:</b> {row['vol_ratio']:.2f}x
                    </p>
                    <p style="margin: 0.2rem 0 0 0; font-size: 0.85rem; color: #666;">
                        <b>Fundamentals:</b> 
                        ROE: {fund_deets.get('roe', 'N/A')}% | 
                        PAT Growth: {fund_deets.get('pat_growth', 'N/A')}% | 
                        D/E: {fund_deets.get('debt_equity', 'N/A')} | 
                        Inst. Hold: {fund_deets.get('institutional_pct', 'N/A')}%
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Full Results Table
            st.subheader("📋 Complete Results Table")

            # Prepare display dataframe
            display_rows = []
            for _, row in filtered.iterrows():
                fd = row['fund_details']
                display_rows.append({
                    'Rank': len(display_rows) + 1,
                    'Stock': row['Ticker'],
                    'Price': round(row['price'], 2),
                    'Change%': round(row['daily_change_pct'], 2),
                    'Total': f"{row['total_score']}/8",
                    'Tech': f"{row['tech_score']}/4",
                    'Fund': f"{row['fund_score']}/4",
                    'Trend': '✅' if row['trend_pass'] else '❌',
                    'RS 6M': round(row['rs_6m'], 2) if row['rs_6m'] is not None else None,
                    'ATR%': round(row['atr_pct'], 2),
                    'VolRatio': round(row['vol_ratio'], 2),
                    'ROE%': fd.get('roe'),
                    'PAT Gr%': fd.get('pat_growth'),
                    'D/E': fd.get('debt_equity'),
                    'Inst Hold%': fd.get('institutional_pct'),
                    'Sector': fd.get('sector', 'N/A'),
                })

            display_df = pd.DataFrame(display_rows)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Total": st.column_config.TextColumn(help="Combined Technical + Fundamental Score"),
                    "Tech": st.column_config.TextColumn(help="Technical Score: Trend(2)+RS(1)+Vol(1)"),
                    "Fund": st.column_config.TextColumn(help="Fundamental Score: ROE+PAT+D/E+Institutional"),
                }
            )

            # Download button
            csv = filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Results (CSV)",
                data=csv,
                file_name=f"swing_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

            # Factor Breakdown
            st.subheader("📊 Factor Breakdown")

            breakdown_rows = []
            for _, row in filtered.iterrows():
                fd = row['fund_details']
                breakdown_rows.append({
                    'Stock': row['Ticker'],
                    'T1-Price>50': '✅' if row['price_above_50'] else '❌',
                    'T2-50>200': '✅' if row['ma50_above_200'] else '❌',
                    'T3-RS>0': '✅' if row['rs_6m'] and row['rs_6m'] > 0 else '❌',
                    'T4-VolSpike': '✅' if row['vol_pass'] else '❌',
                    'F1-ROE>15': '✅' if fd.get('roe_pass') else '❌',
                    'F2-PAT>15': '✅' if fd.get('pat_growth_pass') else '❌',
                    'F3-D/E<1': '✅' if fd.get('debt_equity_pass') else '❌',
                    'F4-Inst>25': '✅' if fd.get('institutional_pass') else '❌',
                    'Total': row['total_score'],
                })

            st.dataframe(pd.DataFrame(breakdown_rows), use_container_width=True, hide_index=True)

    else:
        # Show instructions when not running
        st.info("""
        👈 **Set your filters in the sidebar**, then click **Run Screener** above.

        The app will:
        1. Fetch 1-year price data + fundamentals for all **150 Nifty stocks**
        2. Calculate **4 Technical + 4 Fundamental factors** for each
        3. Rank and filter based on your criteria
        4. Show the **best swing trade candidates**

        *Takes 3-4 minutes to fetch all data.*
        """)

        st.markdown("""
        <div class="info-box">
        <h4>📚 8-Factor Framework</h4>
        <p><b>Technical (4 points):</b></p>
        <p>① Trend: Price > 50 DMA > 200 DMA (2 points)</p>
        <p>② ATR%: 14-day volatility gauge (filter only)</p>
        <p>③ RS vs Nifty: 6M outperformance (+1 point)</p>
        <p>④ Volume: Above 20-day average (+1 point)</p>
        <br>
        <p><b>Fundamental (4 points):</b></p>
        <p>⑤ ROE > 15% (+1 point)</p>
        <p>⑥ PAT/Earnings Growth > 15% (+1 point)</p>
        <p>⑦ Debt/Equity < 1 (+1 point)</p>
        <p>⑧ Institutional Holding > 25% (+1 point)</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="fundamental-box">
        <h4>⚠️ Important Note on FII/DII Data</h4>
        <p>yfinance (free API) provides <b>Institutional Holding %</b> as a combined metric, 
        but does NOT separate FII vs DII for Indian stocks.</p>
        <p>For exact FII+DII breakdown and buying trend analysis, integrate:</p>
        <ul>
            <li>NSE/BSE shareholding data API</li>
            <li>Prime Database / BSE Analytics</li>
            <li>StockEdge / Trendlyne premium APIs</li>
        </ul>
        <p>This app uses Institutional Holding % as a proxy for FII+DII combined.</p>
        </div>
        """, unsafe_allow_html=True)

        # Show sample universe
        st.subheader("🎯 Stock Universe (Nifty 150)")
        sample = [t.replace('.NS', '') for t in NIFTY_150_STOCKS[:15]]
        st.write("Sample: " + ", ".join(sample) + " ... and 135 more")
        st.caption(f"Total: {len(NIFTY_150_STOCKS)} stocks from Nifty 50 + Next 50 + 100")

if __name__ == "__main__":
    main()
