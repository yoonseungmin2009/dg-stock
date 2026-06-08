import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 커스텀 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 전체 배경 */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%);
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: rgba(13, 27, 42, 0.95) !important;
    border-right: 1px solid rgba(0, 200, 150, 0.2);
}
section[data-testid="stSidebar"] * {
    color: #e0e8f0 !important;
}

/* 메인 헤더 */
.main-header {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00c896, #00a8ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
    margin-bottom: 4px;
}

.sub-header {
    color: #6b8fa8;
    font-size: 0.9rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 28px;
}

/* 메트릭 카드 */
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px 24px;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}
.metric-card:hover {
    border-color: rgba(0, 200, 150, 0.4);
    background: rgba(0, 200, 150, 0.05);
    transform: translateY(-2px);
}
.metric-label {
    font-size: 0.72rem;
    color: #6b8fa8;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.metric-ticker {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: #a0b4c8;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    color: #e8f0f8;
    line-height: 1;
}
.metric-delta-up {
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem;
    color: #00c896;
    margin-top: 6px;
}
.metric-delta-down {
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem;
    color: #ff5572;
    margin-top: 6px;
}

/* 섹션 제목 */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #00c896;
    letter-spacing: 3px;
    text-transform: uppercase;
    border-left: 3px solid #00c896;
    padding-left: 12px;
    margin: 28px 0 16px 0;
}

/* 탭 스타일 오버라이드 */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.08);
}
.stTabs [data-baseweb="tab"] {
    color: #6b8fa8;
    border-radius: 8px;
}
.stTabs [aria-selected="true"] {
    background: rgba(0, 200, 150, 0.15) !important;
    color: #00c896 !important;
}

/* plotly 차트 배경 통일 */
.js-plotly-plot .plotly .bg {
    fill: transparent !important;
}

/* 구분선 */
hr {
    border-color: rgba(255,255,255,0.07) !important;
}

/* 텍스트 색상 */
p, label, .stMarkdown {
    color: #c8d8e8 !important;
}

/* 선택 박스 */
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(0, 200, 150, 0.2) !important;
    border: 1px solid rgba(0, 200, 150, 0.5) !important;
}
</style>
""", unsafe_allow_html=True)

# ── 종목 데이터 ───────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "현대자동차": "005380.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "삼성바이오로직스": "207940.KS",
    "KB금융": "105560.KS",
    "셀트리온": "068270.KS",
    "포스코홀딩스": "005490.KS",
    "LG화학": "051910.KS",
    "기아": "000270.KS",
}

US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta": "META",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B",
    "TSMC": "TSM",
    "Taiwan Semi": "TSM",
    "Broadcom": "AVGO",
    "JPMorgan Chase": "JPM",
    "Netflix": "NFLX",
}

PERIOD_MAP = {
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
    "5년": "5y",
}

CHART_COLORS = [
    "#00c896", "#00a8ff", "#ff6b6b", "#ffd93d",
    "#c77dff", "#ff9f43", "#54a0ff", "#5f27cd",
    "#ff6b9d", "#48dbfb", "#1dd1a1", "#feca57",
]

# ── 데이터 로딩 ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_stock_data(tickers: list, period: str) -> dict:
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if not hist.empty:
                data[ticker] = hist
        except Exception:
            pass
    return data

@st.cache_data(ttl=300)
def get_stock_info(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "name": info.get("longName", ticker),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "currency": info.get("currency", ""),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
        }
    except Exception:
        return {}

def calc_returns(hist_df: pd.DataFrame) -> pd.Series:
    """누적 수익률(%) 계산"""
    close = hist_df["Close"]
    return (close / close.iloc[0] - 1) * 100

def fmt_market_cap(val, currency):
    if val is None:
        return "N/A"
    if currency == "KRW":
        if val >= 1e12:
            return f"{val/1e12:.1f}조원"
        return f"{val/1e8:.0f}억원"
    else:
        if val >= 1e12:
            return f"${val/1e12:.2f}T"
        elif val >= 1e9:
            return f"${val/1e9:.1f}B"
        return f"${val/1e6:.0f}M"

# ── 사이드바 ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 종목 설정")
    st.markdown("---")

    period_label = st.selectbox(
        "📅 기간 선택",
        list(PERIOD_MAP.keys()),
        index=3,
    )
    period = PERIOD_MAP[period_label]

    st.markdown("**🇰🇷 한국 주식**")
    selected_kr = st.multiselect(
        "종목 선택",
        list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "현대자동차"],
        key="kr",
    )

    st.markdown("**🇺🇸 미국 주식**")
    selected_us = st.multiselect(
        "종목 선택",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Tesla"],
        key="us",
    )

    st.markdown("---")
    chart_type = st.radio(
        "📈 차트 타입",
        ["수익률 비교", "캔들스틱"],
        index=0,
    )

    show_volume = st.checkbox("거래량 표시", value=True)

    st.markdown("---")
    st.markdown(
        "<div style='color:#4a6a80;font-size:0.75rem;'>⏱ 데이터 5분 캐시<br>출처: Yahoo Finance</div>",
        unsafe_allow_html=True,
    )

# ── 메인 ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">글로벌 주식 비교 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">한국 · 미국 주요 종목 실시간 분석</div>', unsafe_allow_html=True)

# 선택 종목 통합
all_selected = {}
for name in selected_kr:
    all_selected[name] = KR_STOCKS[name]
for name in selected_us:
    all_selected[name] = US_STOCKS[name]

if not all_selected:
    st.info("👈 사이드바에서 종목을 1개 이상 선택해 주세요.")
    st.stop()

# 데이터 로딩
with st.spinner("📡 데이터 불러오는 중..."):
    tickers = list(all_selected.values())
    hist_data = load_stock_data(tickers, period)

# 실패 종목 필터
valid = {name: ticker for name, ticker in all_selected.items() if ticker in hist_data}
if not valid:
    st.error("선택한 종목의 데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()

# ── 메트릭 카드 ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">현재 시세 & 수익률</div>', unsafe_allow_html=True)

cols = st.columns(min(len(valid), 4))
for i, (name, ticker) in enumerate(valid.items()):
    hist = hist_data[ticker]
    ret = calc_returns(hist)
    total_ret = ret.iloc[-1]
    delta_1d = ((hist["Close"].iloc[-1] / hist["Close"].iloc[-2]) - 1) * 100 if len(hist) >= 2 else 0
    last_price = hist["Close"].iloc[-1]
    currency = "KRW" if ticker.endswith(".KS") or ticker.endswith(".KQ") else "USD"
    price_fmt = f"₩{last_price:,.0f}" if currency == "KRW" else f"${last_price:.2f}"

    ret_class = "metric-delta-up" if total_ret >= 0 else "metric-delta-down"
    d1_class  = "metric-delta-up" if delta_1d  >= 0 else "metric-delta-down"
    ret_arrow = "▲" if total_ret >= 0 else "▼"
    d1_arrow  = "▲" if delta_1d  >= 0 else "▼"

    col = cols[i % 4]
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{'🇰🇷 한국' if currency=='KRW' else '🇺🇸 미국'}</div>
            <div class="metric-ticker">{ticker}</div>
            <div style="font-weight:600;color:#e8f0f8;margin-bottom:4px;">{name}</div>
            <div class="metric-value">{price_fmt}</div>
            <div class="{ret_class}">{ret_arrow} {period_label} {abs(total_ret):.2f}%</div>
            <div class="{d1_class}" style="font-size:0.78rem;">{d1_arrow} 1일 {abs(delta_1d):.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# ── 탭 ────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 수익률 비교", "🕯 캔들 차트", "📊 상세 분석"])

# ─────────────── TAB 1: 수익률 비교 ───────────────
with tab1:
    fig = go.Figure()

    for i, (name, ticker) in enumerate(valid.items()):
        hist = hist_data[ticker]
        ret  = calc_returns(hist)
        color = CHART_COLORS[i % len(CHART_COLORS)]

        fig.add_trace(go.Scatter(
            x=ret.index,
            y=ret.values,
            name=name,
            line=dict(color=color, width=2),
            mode="lines",
            hovertemplate=(
                f"<b>{name}</b><br>"
                "날짜: %{x|%Y-%m-%d}<br>"
                "누적수익률: %{y:.2f}%<extra></extra>"
            ),
        ))

    fig.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.2)", line_width=1)

    fig.update_layout(
        title=dict(text=f"누적 수익률 비교 ({period_label})", font=dict(size=16, color="#e8f0f8"), x=0.01),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Noto Sans KR", color="#a0b4c8"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", showgrid=True, zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", ticksuffix="%", showgrid=True, zeroline=False),
        legend=dict(
            bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            font=dict(size=12),
        ),
        hovermode="x unified",
        height=520,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 수익률 랭킹 바 차트
    st.markdown('<div class="section-title">수익률 랭킹</div>', unsafe_allow_html=True)
    rank_data = []
    for name, ticker in valid.items():
        hist = hist_data[ticker]
        ret  = calc_returns(hist).iloc[-1]
        rank_data.append({"종목": name, "수익률(%)": round(ret, 2)})

    rank_df = pd.DataFrame(rank_data).sort_values("수익률(%)", ascending=True)
    colors_bar = ["#ff5572" if v < 0 else "#00c896" for v in rank_df["수익률(%)"]]

    fig_bar = go.Figure(go.Bar(
        x=rank_df["수익률(%)"],
        y=rank_df["종목"],
        orientation="h",
        marker_color=colors_bar,
        text=[f"{v:+.2f}%" for v in rank_df["수익률(%)"]],
        textposition="outside",
        textfont=dict(color="#e8f0f8", size=12),
        hovertemplate="<b>%{y}</b><br>수익률: %{x:.2f}%<extra></extra>",
    ))
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Noto Sans KR", color="#a0b4c8"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", ticksuffix="%", zeroline=True,
                   zerolinecolor="rgba(255,255,255,0.2)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        height=max(250, len(rank_df) * 45),
        margin=dict(l=10, r=80, t=10, b=10),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ─────────────── TAB 2: 캔들 차트 ───────────────
with tab2:
    candle_target = st.selectbox(
        "종목 선택",
        list(valid.keys()),
        key="candle_select",
    )
    ticker_c = valid[candle_target]
    hist_c   = hist_data[ticker_c]

    if show_volume:
        fig_c = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.75, 0.25],
        )
    else:
        fig_c = make_subplots(rows=1, cols=1)

    fig_c.add_trace(go.Candlestick(
        x=hist_c.index,
        open=hist_c["Open"],
        high=hist_c["High"],
        low=hist_c["Low"],
        close=hist_c["Close"],
        name=candle_target,
        increasing_line_color="#00c896",
        decreasing_line_color="#ff5572",
        increasing_fillcolor="rgba(0,200,150,0.8)",
        decreasing_fillcolor="rgba(255,85,114,0.8)",
    ), row=1, col=1)

    # 이동평균선
    for ma, color_ma in [(20, "#ffd93d"), (60, "#c77dff")]:
        if len(hist_c) >= ma:
            ma_series = hist_c["Close"].rolling(ma).mean()
            fig_c.add_trace(go.Scatter(
                x=hist_c.index, y=ma_series,
                name=f"MA{ma}",
                line=dict(color=color_ma, width=1.5, dash="dot"),
                mode="lines",
            ), row=1, col=1)

    if show_volume:
        vol_colors = [
            "#00c896" if hist_c["Close"].iloc[i] >= hist_c["Open"].iloc[i]
            else "#ff5572"
            for i in range(len(hist_c))
        ]
        fig_c.add_trace(go.Bar(
            x=hist_c.index,
            y=hist_c["Volume"],
            name="거래량",
            marker_color=vol_colors,
            opacity=0.7,
            showlegend=False,
        ), row=2, col=1)
        fig_c.update_yaxes(title_text="거래량", row=2, col=1,
                            gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=10))

    fig_c.update_layout(
        title=dict(text=f"{candle_target} 캔들스틱 차트 ({period_label})", font=dict(size=16, color="#e8f0f8"), x=0.01),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Noto Sans KR", color="#a0b4c8"),
        xaxis_rangeslider_visible=False,
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickformat=",.0f"),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
        height=600,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(fig_c, use_container_width=True)

# ─────────────── TAB 3: 상세 분석 ───────────────
with tab3:
    # 상관관계 히트맵
    st.markdown('<div class="section-title">종목 간 수익률 상관관계</div>', unsafe_allow_html=True)

    if len(valid) >= 2:
        ret_df = pd.DataFrame()
        for name, ticker in valid.items():
            hist = hist_data[ticker]
            # 날짜 인덱스 정규화 (tz 제거)
            hist_copy = hist.copy()
            if hist_copy.index.tz is not None:
                hist_copy.index = hist_copy.index.tz_localize(None)
            r = (hist_copy["Close"].pct_change() * 100).rename(name)
            ret_df = pd.concat([ret_df, r], axis=1)

        corr = ret_df.corr().round(2)
        fig_hm = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.columns.tolist(),
            colorscale=[
                [0.0, "#ff5572"], [0.5, "#1a2744"], [1.0, "#00c896"]
            ],
            zmin=-1, zmax=1,
            text=corr.values,
            texttemplate="%{text}",
            textfont=dict(size=12, color="white"),
            hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>상관계수: %{z:.2f}<extra></extra>",
        ))
        fig_hm.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Noto Sans KR", color="#a0b4c8"),
            height=max(350, len(valid) * 60),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_hm, use_container_width=True)
    else:
        st.info("상관관계 분석을 위해 종목을 2개 이상 선택해 주세요.")

    # 변동성 & 수익률 산포도
    st.markdown('<div class="section-title">리스크-수익률 분석 (기간 내)</div>', unsafe_allow_html=True)

    scatter_data = []
    for i, (name, ticker) in enumerate(valid.items()):
        hist = hist_data[ticker]
        daily_ret = hist["Close"].pct_change().dropna() * 100
        total_ret = calc_returns(hist).iloc[-1]
        vol = daily_ret.std() * (252 ** 0.5)  # 연환산 변동성
        currency = "KRW" if ticker.endswith(".KS") or ticker.endswith(".KQ") else "USD"
        scatter_data.append({
            "종목": name,
            "연환산 변동성(%)": round(vol, 2),
            "누적수익률(%)": round(total_ret, 2),
            "시장": "한국" if currency == "KRW" else "미국",
            "color": CHART_COLORS[i % len(CHART_COLORS)],
        })

    sc_df = pd.DataFrame(scatter_data)

    fig_sc = go.Figure()
    for _, row in sc_df.iterrows():
        fig_sc.add_trace(go.Scatter(
            x=[row["연환산 변동성(%)"]],
            y=[row["누적수익률(%)"]],
            mode="markers+text",
            name=row["종목"],
            text=[row["종목"]],
            textposition="top center",
            textfont=dict(size=11, color=row["color"]),
            marker=dict(size=16, color=row["color"], opacity=0.85,
                        line=dict(width=2, color="rgba(255,255,255,0.3)")),
            hovertemplate=(
                f"<b>{row['종목']}</b><br>"
                "변동성: %{x:.2f}%<br>"
                "수익률: %{y:.2f}%<extra></extra>"
            ),
            showlegend=False,
        ))

    fig_sc.add_hline(y=0, line_dash="dot", line_color="rgba(255,255,255,0.2)")
    fig_sc.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(family="Noto Sans KR", color="#a0b4c8"),
        xaxis=dict(title="연환산 변동성 (%)", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title="누적 수익률 (%)", gridcolor="rgba(255,255,255,0.06)", ticksuffix="%"),
        height=460,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    # 요약 테이블
    st.markdown('<div class="section-title">종목 요약 테이블</div>', unsafe_allow_html=True)
    table_rows = []
    for name, ticker in valid.items():
        hist = hist_data[ticker]
        daily_ret = hist["Close"].pct_change().dropna() * 100
        total_ret  = calc_returns(hist).iloc[-1]
        vol = daily_ret.std() * (252 ** 0.5)
        max_dd_val = ((hist["Close"] / hist["Close"].cummax()) - 1).min() * 100
        currency = "KRW" if ticker.endswith(".KS") or ticker.endswith(".KQ") else "USD"
        last_p = hist["Close"].iloc[-1]
        price_str = f"₩{last_p:,.0f}" if currency == "KRW" else f"${last_p:.2f}"

        table_rows.append({
            "종목": name,
            "시장": "🇰🇷 한국" if currency == "KRW" else "🇺🇸 미국",
            "현재가": price_str,
            f"수익률({period_label})": f"{total_ret:+.2f}%",
            "연환산 변동성": f"{vol:.1f}%",
            "최대낙폭(MDD)": f"{max_dd_val:.2f}%",
        })

    tbl_df = pd.DataFrame(table_rows)
    st.dataframe(
        tbl_df.style.applymap(
            lambda v: "color: #00c896" if isinstance(v, str) and v.startswith("+")
            else ("color: #ff5572" if isinstance(v, str) and v.startswith("-") else ""),
        ),
        use_container_width=True,
        hide_index=True,
    )

# ── 푸터 ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#3a5a70;font-size:0.8rem;padding:8px'>"
    "📡 데이터 출처: Yahoo Finance via yfinance &nbsp;|&nbsp; "
    f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M')} KST"
    "</div>",
    unsafe_allow_html=True,
)
