"""
Swing Trading Screener - Nifty 150
8-Factor Technical + Fundamental Framework
Deploy on Streamlit Cloud
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time

st.set_page_config(
    page_title="Swing Trading Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; text-align: center; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .score-green { background: #d4edda; color: #155724; padding: 4px 12px; border-radius: 20px; font-weight: 700; }
    .score-yellow { background: #fff3cd; color: #856404; padding: 4px 12px; border-radius: 20px; font-weight: 700; }
    .score-red { background: #f8d7da; color: #721c24; padding: 4px 12px; border-radius: 20px; font-weight: 700; }
    .info-box { background: #e7f3ff; border: 1px solid #b8daff; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .warn-box { background: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

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
def fetch_price_data(ticker):
    """Fetch 1 year price data using yf.Ticker (more reliable than download)"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        if hist is None or hist.empty or len(hist) < 50:
            return None
        # Ensure standard column names
        hist = hist.rename(columns={
            'Open': 'Open', 'High': 'High', 'Low': 'Low',
            'Close': 'Close', 'Volume': 'Volume'
        })
        return hist
    except Exception as e:
        return None

@st.cache_data(ttl=3600)
def fetch_fundamentals(ticker):
    """Fetch fundamental data"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if not info or len(info) < 5:
            return None
        return {
            'roe': info.get('returnOnEquity'),
            'debt_to_equity': info.get('debtToEquity'),
            'earnings_growth': info.get('earningsGrowth'),
            'revenue_growth': info.get('revenueGrowth'),
            'institutional_holding': info.get('heldPercentInstitutions'),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'pb_ratio': info.get('priceToBook'),
            'sector': info.get('sector'),
        }
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_nifty():
    """Fetch Nifty 50 index"""
    try:
        idx = yf.Ticker("^NSEI")
        hist = idx.history(period="1y")
        if hist is None or hist.empty:
            return None
        return hist
    except:
        return None

def calc_technical(df, nifty_df):
    """Calculate technical indicators"""
    if df is None or len(df) < 50:
        return None

    try:
        latest_close = float(df['Close'].iloc[-1])
        latest_volume = float(df['Volume'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else latest_close

        # Moving Averages
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        ma50 = float(df['MA50'].iloc[-1]) if not pd.isna(df['MA50'].iloc[-1]) else 0
        ma200 = float(df['MA200'].iloc[-1]) if not pd.isna(df['MA200'].iloc[-1]) else 0

        price_above_50 = latest_close > ma50 if ma50 > 0 else False
        ma50_above_200 = ma50 > ma200 if ma50 > 0 and ma200 > 0 else False
        trend_score = int(price_above_50) + int(ma50_above_200)
        trend_pass = price_above_50 and ma50_above_200

        # ATR%
        df['TR1'] = df['High'] - df['Low']
        df['TR2'] = abs(df['High'] - df['Close'].shift(1))
        df['TR3'] = abs(df['Low'] - df['Close'].shift(1))
        df['TR'] = df[['TR1', 'TR2', 'TR3']].max(axis=1)
        df['ATR14'] = df['TR'].rolling(window=14).mean()
        atr_val = df['ATR14'].iloc[-1]
        atr = float(atr_val) if not pd.isna(atr_val) else 0
        atr_pct = (atr / latest_close) * 100 if latest_close > 0 else 999

        # RS vs Nifty
        rs_6m = None
        rs_3m = None
        if nifty_df is not None and len(nifty_df) >= 63 and len(df) >= 63:
            try:
                nifty_6m = float(nifty_df['Close'].iloc[-1] / nifty_df['Close'].iloc[-126] - 1) * 100 if len(nifty_df) >= 126 else None
                stock_6m = float(df['Close'].iloc[-1] / df['Close'].iloc[-126] - 1) * 100 if len(df) >= 126 else None
                if nifty_6m is not None and stock_6m is not None:
                    rs_6m = stock_6m - nifty_6m

                nifty_3m = float(nifty_df['Close'].iloc[-1] / nifty_df['Close'].iloc[-63] - 1) * 100
                stock_3m = float(df['Close'].iloc[-1] / df['Close'].iloc[-63] - 1) * 100
                rs_3m = stock_3m - nifty_3m
            except:
                pass

        # Volume
        df['Vol20'] = df['Volume'].rolling(window=20).mean()
        vol20_val = df['Vol20'].iloc[-1]
        vol20 = float(vol20_val) if not pd.isna(vol20_val) else 0
        vol_pass = latest_volume > vol20 if vol20 > 0 else False
        vol_ratio = latest_volume / vol20 if vol20 > 0 else 0

        # Tech score
        tech_score = trend_score
        if rs_6m is not None and rs_6m > 0:
            tech_score += 1
        if vol_pass:
            tech_score += 1

        return {
            'price': latest_close,
            'prev_close': prev_close,
            'daily_change_pct': ((latest_close / prev_close) - 1) * 100 if prev_close > 0 else 0,
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
            'data_points': len(df),
        }
    except Exception as e:
        return None

def calc_fundamental(info, filters):
    """Calculate fundamental score"""
    if info is None:
        return {'fund_score': 0, 'fund_pass_count': 0, 'fund_details': {}}

    score = 0
    passed = 0
    details = {}

    # ROE
    roe = info.get('roe')
    if roe is not None and not pd.isna(roe):
        roe_pct = roe * 100
        roe_pass = roe_pct >= filters['min_roe']
        if roe_pass: score += 1; passed += 1
        details['roe'] = round(roe_pct, 2)
        details['roe_pass'] = roe_pass
    else:
        details['roe'] = None
        details['roe_pass'] = False

    # Earnings Growth
    eg = info.get('earnings_growth')
    if eg is not None and not pd.isna(eg):
        eg_pct = eg * 100
        eg_pass = eg_pct >= filters['min_pat_growth']
        if eg_pass: score += 1; passed += 1
        details['pat_growth'] = round(eg_pct, 2)
        details['pat_growth_pass'] = eg_pass
    else:
        details['pat_growth'] = None
        details['pat_growth_pass'] = False

    # Debt/Equity
    de = info.get('debt_to_equity')
    if de is not None and not pd.isna(de):
        de_ratio = de / 100
        de_pass = de_ratio <= filters['max_debt_equity']
        if de_pass: score += 1; passed += 1
        details['debt_equity'] = round(de_ratio, 2)
        details['debt_equity_pass'] = de_pass
    else:
        details['debt_equity'] = None
        details['debt_equity_pass'] = False

    # Institutional
    ih = info.get('institutional_holding')
    if ih is not None and not pd.isna(ih):
        ih_pct = ih * 100
        ih_pass = ih_pct >= filters['min_institutional']
        if ih_pass: score += 1; passed += 1
        details['institutional_pct'] = round(ih_pct, 2)
        details['institutional_pass'] = ih_pass
    else:
        details['institutional_pct'] = None
        details['institutional_pass'] = False

    details['market_cap'] = info.get('market_cap')
    details['pe_ratio'] = info.get('pe_ratio')
    details['pb_ratio'] = info.get('pb_ratio')
    details['sector'] = info.get('sector')

    return {'fund_score': score, 'fund_pass_count': passed, 'fund_details': details}

def main():
    st.markdown('<div class="main-header">📈 Swing Trading Screener</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">8-Factor Technical + Fundamental | Nifty 150</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Filters")

        st.subheader("📊 Technical")
        min_trend_score = st.slider("Min Trend Score", 0, 2, 0, help="0=Any, 1=Partial, 2=Full")
        require_trend_pass = st.checkbox("Require Full Trend", value=False)
        max_atr = st.slider("Max ATR%", 0.5, 10.0, 5.0, 0.5)
        min_rs = st.slider("Min RS vs Nifty (6M)", -30.0, 30.0, -30.0, 1.0)
        require_volume = st.checkbox("Require Volume Spike", value=False)
        min_vol_ratio = st.slider("Min Vol Ratio", 0.0, 3.0, 0.0, 0.1)
        min_tech_score = st.slider("Min Tech Score", 0, 4, 0, 1)

        st.markdown("---")

        st.subheader("🏛️ Fundamental")
        min_roe = st.slider("Min ROE (%)", 0.0, 50.0, 0.0, 1.0)
        min_pat_growth = st.slider("Min PAT Growth (%)", -50.0, 100.0, -50.0, 1.0)
        max_debt_equity = st.slider("Max D/E Ratio", 0.0, 5.0, 5.0, 0.1)
        min_institutional = st.slider("Min Inst. Holding (%)", 0.0, 50.0, 0.0, 1.0)
        min_fund_score = st.slider("Min Fund Score", 0, 4, 0, 1)

        st.markdown("---")

        st.subheader("🎯 Combined")
        min_total_score = st.slider("Min Total Score", 0, 8, 0, 1)

        st.markdown("---")

        # Quick presets
        st.subheader("⚡ Quick Presets")
        preset = st.selectbox("Load Preset", [
            "Custom (manual)",
            "🟢 Strict: Score >= 6, Trend Pass, ROE>15, D/E<1",
            "🟡 Moderate: Score >= 4, Trend Score>=1, ROE>10",
            "🔴 Lenient: Score >= 2, Any Trend, ROE>5",
            "📈 Momentum Only: Tech Score>=3, No Fund Filter",
            "🏛️ Quality Only: Fund Score>=3, No Tech Filter",
        ])

    # Main
    col1, col2, col3 = st.columns(3)

    if st.button("🚀 Run Screener", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        fund_filters = {
            'min_roe': min_roe,
            'min_pat_growth': min_pat_growth,
            'max_debt_equity': max_debt_equity,
            'min_institutional': min_institutional,
        }

        with st.spinner("Fetching data for 150 stocks... ~3-4 minutes"):
            nifty_df = fetch_nifty()
            results = []
            failed_stocks = []

            total = len(NIFTY_150_STOCKS)
            for i, ticker in enumerate(NIFTY_150_STOCKS):
                status_text.text(f"Processing {ticker}... ({i+1}/{total})")
                progress_bar.progress((i + 1) / total)

                # Price data
                price_df = fetch_price_data(ticker)
                tech = calc_technical(price_df, nifty_df)

                if tech is None:
                    failed_stocks.append(ticker)
                    continue

                # Fundamental data
                fund_info = fetch_fundamentals(ticker)
                fund = calc_fundamental(fund_info, fund_filters)

                row = {
                    'Ticker': ticker.replace('.NS', ''),
                    **tech,
                    **fund,
                    'total_score': tech['tech_score'] + fund['fund_score'],
                }
                results.append(row)
                time.sleep(0.1)

        if not results:
            st.error("❌ No stock data could be fetched. Check internet or try again.")
            return

        df_all = pd.DataFrame(results)

        # Apply filters
        filtered = df_all.copy()

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
        filtered = filtered[filtered['fund_score'] >= min_fund_score]
        filtered = filtered[filtered['total_score'] >= min_total_score]

        filtered = filtered.sort_values(['total_score', 'tech_score', 'fund_score'], ascending=[False, False, False])

        total_ok = len(df_all)
        total_pass = len(filtered)

        col1.metric("📊 Data Fetched", total_ok)
        col2.metric("✅ Passed Filters", total_pass)
        col3.metric("❌ Fetch Failed", len(failed_stocks))

        st.markdown("---")

        # Show failed stocks if any
        if failed_stocks:
            with st.expander(f"⚠️ {len(failed_stocks)} stocks failed to fetch data"):
                st.write(", ".join([s.replace('.NS','') for s in failed_stocks[:20]]) + ("..." if len(failed_stocks)>20 else ""))

        if total_pass == 0:
            st.warning("⚠️ No stocks matched your filters. Showing ALL fetched stocks below for reference.")

            # Show all with relaxed view
            show_df = df_all.sort_values('total_score', ascending=False)
            st.info(f"**Tip:** Try setting all sliders to 0 (minimum) and uncheck all checkboxes. Current best stock: **{show_df.iloc[0]['Ticker']}** with score **{show_df.iloc[0]['total_score']}/8**")

            # Show top 10 anyway
            st.subheader("📋 Top 10 Stocks (All Data, No Filter)")
            display_all(show_df.head(10))
        else:
            st.success(f"🎉 Found **{total_pass}** stocks matching your criteria!")

            # Top picks
            st.subheader("🏆 Top Picks")
            top5 = filtered.head(5)
            for idx, (_, row) in enumerate(top5.iterrows()):
                score = row['total_score']
                color = "#28a745" if score >= 6 else "#ffc107" if score >= 4 else "#dc3545"
                fd = row['fund_details']

                st.markdown(f"""
                <div style="background: {color}10; border-left: 4px solid {color}; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                    <div style="display: flex; justify-content: space-between;">
                        <h3 style="margin:0; color: {color};">#{idx+1} {row['Ticker']}</h3>
                        <span class="score-green">{score}/8</span>
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
                        <b>RS:</b> {row['rs_6m'] or 0:+.2f}% | 
                        <b>ATR:</b> {row['atr_pct']:.2f}% | 
                        <b>Vol:</b> {row['vol_ratio']:.2f}x
                    </p>
                    <p style="margin: 0.2rem 0 0 0; font-size: 0.85rem; color: #666;">
                        <b>Fundamentals:</b> 
                        ROE: {fd.get('roe') or 'N/A'}% | 
                        PAT Gr: {fd.get('pat_growth') or 'N/A'}% | 
                        D/E: {fd.get('debt_equity') or 'N/A'} | 
                        Inst: {fd.get('institutional_pct') or 'N/A'}%
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Full table
            st.subheader("📋 Complete Results")
            display_all(filtered)

            # Download
            csv = filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

    else:
        st.info("👈 **Set filters in sidebar** (default = show all), then click **Run Screener**")

        st.markdown("""
        <div class="info-box">
        <h4>📚 8-Factor Framework</h4>
        <p><b>Technical (4 points):</b> Trend (2) + RS vs Nifty (1) + Volume (1)</p>
        <p><b>Fundamental (4 points):</b> ROE>15% (1) + PAT Growth>15% (1) + D/E<1 (1) + Inst.>25% (1)</p>
        <p><b>Max Score: 8/8</b></p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="warn-box">
        <h4>⚠️ Important</h4>
        <p>yfinance provides <b>Institutional Holding %</b> as combined FII+DII proxy.</p>
        <p>For exact FII/DII breakdown, integrate NSE/BSE data APIs.</p>
        <p><b>Default filter settings = 0 (show all stocks).</b> Increase sliders to filter strictly.</p>
        </div>
        """, unsafe_allow_html=True)

def display_all(df):
    """Display results in a clean table"""
    rows = []
    for _, row in df.iterrows():
        fd = row['fund_details']
        rows.append({
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
            'Inst%': fd.get('institutional_pct'),
            'Sector': fd.get('sector', 'N/A'),
        })

    display_df = pd.DataFrame(rows)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
