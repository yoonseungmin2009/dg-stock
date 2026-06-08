import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

# ── 페이지 설정
st.set_page_config(
    page_title="MARKETSIGHT — 글로벌 주식 분석",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

:root {
    --bg-base:      #18191e;
    --bg-surface:   #1e2028;
    --bg-elevated:  #252830;
    --bg-hover:     #2c2f3a;
    --border:       #2e3140;
    --border-sub:   #232633;

    --txt-primary:  #eef0f8;
    --txt-second:   #8890aa;
    --txt-muted:    #505870;

    --gold:         #c9a84c;
    --teal:         #3ecfb2;
    --red:          #e05c6a;
    --purple:       #8b8ede;
}

html, body, [class*="css"], .stApp {
    font-family: 'Pretendard', -apple-system, sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--txt-primary) !important;
}

/* ── 사이드바 ── */
section[data-testid="stSidebar"] {
    background-color: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: var(--txt-second) !important;
    font-family: 'Pretendard', sans-serif !important;
}
/* selectbox / multiselect 컨테이너 */
[data-baseweb="select"] > div {
    background-color: var(--bg-elevated) !important;
    border-color: var(--border) !important;
    color: var(--txt-primary) !important;
}
[data-baseweb="select"] * { color: var(--txt-primary) !important; }
[data-baseweb="menu"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="menu"] li { color: var(--txt-primary) !important; }
[data-baseweb="menu"] li:hover { background: var(--bg-hover) !important; }
[data-baseweb="tag"] {
    background: rgba(201,168,76,.15) !important;
    border: 1px solid rgba(201,168,76,.35) !important;
    color: var(--gold) !important;
    border-radius: 4px !important;
}

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Pretendard', sans-serif !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: var(--txt-muted) !important;
    border-radius: 7px !important;
    padding: 8px 20px !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-elevated) !important;
    color: var(--txt-primary) !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display:none !important; }

hr { border-color: var(--border) !important; }
p, li, .stMarkdown p { color: var(--txt-second) !important; }

/* ── 헤더 ── */
.ms-logo {
    display: inline-block;
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: .22em;
    color: var(--gold);
    background: rgba(201,168,76,.1);
    border: 1px solid rgba(201,168,76,.3);
    border-radius: 4px;
    padding: 3px 9px;
    margin-right: 12px;
    vertical-align: middle;
}
.ms-title {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--txt-primary);
    letter-spacing: -.03em;
    vertical-align: middle;
}
.ms-sub {
    font-size: .78rem;
    color: var(--txt-muted);
    letter-spacing: .07em;
    margin: 4px 0 28px;
}

/* ── 섹션 라벨 ── */
.ms-section {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: .68rem;
    font-weight: 700;
    letter-spacing: .2em;
    text-transform: uppercase;
    color: var(--txt-muted);
    margin: 26px 0 14px;
}
.ms-section::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── 메트릭 카드 ── */
.ms-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.ms-card::before {
    content: '';
    position: absolute;
    inset: 0 0 auto 0;
    height: 2px;
    background: linear-gradient(90deg, var(--gold), transparent);
}
.ms-card-mkt   { font-size:.63rem; font-weight:700; letter-spacing:.15em;
                  text-transform:uppercase; color:var(--txt-muted); margin-bottom:8px; }
.ms-card-name  { font-size:.9rem; font-weight:600; color:var(--txt-primary);
                  margin-bottom:1px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.ms-card-tick  { font-size:.68rem; color:var(--txt-muted); letter-spacing:.04em; margin-bottom:12px; }
.ms-card-price { font-size:1.42rem; font-weight:700; color:var(--txt-primary);
                  letter-spacing:-.02em; margin-bottom:10px;
                  font-family:'SF Mono','Fira Code',monospace; }
.ms-divider    { height:1px; background:var(--border-sub); margin:10px 0; }
.badge-up   { display:inline-block; font-size:.75rem; font-weight:700; color:var(--teal);
               background:rgba(62,207,178,.12); border:1px solid rgba(62,207,178,.3);
               border-radius:4px; padding:2px 7px; margin-right:5px;
               font-family:'SF Mono','Fira Code',monospace; }
.badge-dn   { display:inline-block; font-size:.75rem; font-weight:700; color:var(--red);
               background:rgba(224,92,106,.12); border:1px solid rgba(224,92,106,.3);
               border-radius:4px; padding:2px 7px; margin-right:5px;
               font-family:'SF Mono','Fira Code',monospace; }
.ms-card-lbl   { font-size:.65rem; color:var(--txt-muted); margin-top:4px; }

/* ── 사이드바 유틸 ── */
.sb-div { height:1px; background:var(--border); margin:14px 0; }
.sb-lbl { font-size:.67rem; font-weight:700; letter-spacing:.15em;
           text-transform:uppercase; color:var(--txt-muted) !important; margin-bottom:5px; }

/* ── 푸터 ── */
.ms-footer { text-align:center; font-size:.7rem; color:var(--txt-muted);
              padding:14px 0 6px; letter-spacing:.05em; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ─────────────────────────── 종목 사전 ───────────────────────────────────────
KR_STOCKS = {
    "삼성전자":         "005930.KS",
    "SK하이닉스":       "000660.KS",
    "LG에너지솔루션":   "373220.KS",
    "현대자동차":       "005380.KS",
    "NAVER":            "035420.KS",
    "카카오":           "035720.KS",
    "삼성바이오로직스": "207940.KS",
    "KB금융":           "105560.KS",
    "셀트리온":         "068270.KS",
    "포스코홀딩스":     "005490.KS",
    "LG화학":           "051910.KS",
    "기아":             "000270.KS",
}
US_STOCKS = {
    "Apple":             "AAPL",
    "Microsoft":         "MSFT",
    "NVIDIA":            "NVDA",
    "Amazon":            "AMZN",
    "Alphabet (Google)": "GOOGL",
    "Meta":              "META",
    "Tesla":             "TSLA",
    "Berkshire Hathaway":"BRK-B",
    "Broadcom":          "AVGO",
    "JPMorgan Chase":    "JPM",
    "Netflix":           "NFLX",
    "TSMC":              "TSM",
}
PERIOD_MAP = {
    "1개월":"1mo","3개월":"3mo","6개월":"6mo",
    "1년":"1y","2년":"2y","5년":"5y",
}
PALETTE = [
    "#c9a84c","#3ecfb2","#e05c6a","#8b8ede",
    "#f0a070","#6ec6a0","#d08cc8","#80b8d8",
    "#e8c870","#90d890","#c87878","#a0a8d8",
]

# ─────────────────────────── 유틸 ────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data(tickers: tuple, period: str) -> dict:
    out = {}
    for t in tickers:
        try:
            h = yf.Ticker(t).history(period=period)
            if not h.empty:
                out[t] = h
        except Exception:
            pass
    return out

def returns(df):
    c = df["Close"]; return (c/c.iloc[0]-1)*100

def is_kr(t): return t.endswith(".KS") or t.endswith(".KQ")

def pfmt(p, kr): return f"₩{p:,.0f}" if kr else f"${p:.2f}"

def base_layout(h=500, extra_margins=None):
    m = dict(l=14,r=14,t=44,b=14)
    if extra_margins: m.update(extra_margins)
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#1e2028",
        font=dict(family="Pretendard, sans-serif", color="#8890aa", size=12),
        height=h, margin=m,
        legend=dict(bgcolor="#252830",bordercolor="#2e3140",borderwidth=1,
                    font=dict(size=12,color="#eef0f8")),
        xaxis=dict(gridcolor="#232633",zerolinecolor="#2e3140",linecolor="#2e3140"),
        yaxis=dict(gridcolor="#232633",zerolinecolor="#2e3140",linecolor="#2e3140"),
    )

# ─────────────────────────── 사이드바 ────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sb-lbl">◈ MARKETSIGHT</p>', unsafe_allow_html=True)
    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)

    st.markdown('<p class="sb-lbl">조회 기간</p>', unsafe_allow_html=True)
    period_label = st.selectbox("기간",list(PERIOD_MAP.keys()),index=3,label_visibility="collapsed")
    period = PERIOD_MAP[period_label]

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sb-lbl">🇰🇷 한국 종목</p>', unsafe_allow_html=True)
    sel_kr = st.multiselect("KR",list(KR_STOCKS.keys()),
                             default=["삼성전자","SK하이닉스","현대자동차"],
                             label_visibility="collapsed")

    st.markdown('<p class="sb-lbl">🇺🇸 미국 종목</p>', unsafe_allow_html=True)
    sel_us = st.multiselect("US",list(US_STOCKS.keys()),
                             default=["Apple","NVIDIA","Tesla"],
                             label_visibility="collapsed")

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)
    show_vol = st.checkbox("거래량 표시", value=True)
    show_ma  = st.checkbox("이동평균선 (MA20 / MA60)", value=True)

    st.markdown('<div class="sb-div"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:.68rem;color:#505870;line-height:1.8">'
                '데이터: Yahoo Finance<br>캐시: 5분 갱신</p>', unsafe_allow_html=True)

# ─────────────────────────── 헤더 ────────────────────────────────────────────
st.markdown('<span class="ms-logo">MARKETSIGHT</span>'
            '<span class="ms-title">글로벌 주식 비교 대시보드</span>', unsafe_allow_html=True)
st.markdown('<p class="ms-sub">한국 · 미국 주요 종목 수익률 &amp; 리스크 통합 분석</p>',
            unsafe_allow_html=True)

# ─────────────────────────── 데이터 로드 ─────────────────────────────────────
all_sel = {n:KR_STOCKS[n] for n in sel_kr}
all_sel.update({n:US_STOCKS[n] for n in sel_us})

if not all_sel:
    st.info("← 사이드바에서 종목을 하나 이상 선택해 주세요.")
    st.stop()

with st.spinner("시세 데이터를 불러오는 중..."):
    hdata = load_data(tuple(all_sel.values()), period)

valid = {n:t for n,t in all_sel.items() if t in hdata}
if not valid:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()

# ─────────────────────────── 메트릭 카드 ─────────────────────────────────────
st.markdown('<div class="ms-section">현재 시세</div>', unsafe_allow_html=True)

cols = st.columns(min(len(valid),4))
for i,(name,ticker) in enumerate(valid.items()):
    hist     = hdata[ticker]
    tot      = returns(hist).iloc[-1]
    d1       = ((hist["Close"].iloc[-1]/hist["Close"].iloc[-2])-1)*100 if len(hist)>=2 else 0
    kr       = is_kr(ticker)

    b_tot = (f'<span class="badge-up">▲ {abs(tot):.2f}%</span>' if tot>=0
             else f'<span class="badge-dn">▼ {abs(tot):.2f}%</span>')
    b_d1  = (f'<span class="badge-up" style="font-size:.68rem">▲ {abs(d1):.2f}%</span>' if d1>=0
             else f'<span class="badge-dn" style="font-size:.68rem">▼ {abs(d1):.2f}%</span>')

    with cols[i%4]:
        st.markdown(f"""
        <div class="ms-card">
            <div class="ms-card-mkt">{"🇰🇷  KOSPI" if kr else "🇺🇸  NASDAQ / NYSE"}</div>
            <div class="ms-card-name">{name}</div>
            <div class="ms-card-tick">{ticker}</div>
            <div class="ms-card-price">{pfmt(hist["Close"].iloc[-1],kr)}</div>
            <div class="ms-divider"></div>
            {b_tot}
            <div class="ms-card-lbl">{period_label} 누적수익률</div>
            <div style="margin-top:7px">{b_d1}
              <span style="font-size:.65rem;color:#505870">전일 대비</span></div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────── 탭 ──────────────────────────────────────────────
st.markdown("")
tab1, tab2, tab3 = st.tabs(["  수익률 비교  ","  캔들 차트  ","  상세 분석  "])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="ms-section">누적 수익률 추이</div>', unsafe_allow_html=True)

    fig = go.Figure()
    for i,(name,ticker) in enumerate(valid.items()):
        ret = returns(hdata[ticker])
        fig.add_trace(go.Scatter(
            x=ret.index, y=ret.values, name=name, mode="lines",
            line=dict(color=PALETTE[i%len(PALETTE)], width=2),
            hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>수익률: %{{y:.2f}}%<extra></extra>",
        ))
    fig.add_hline(y=0, line_dash="dot", line_color="#3d4460", line_width=1)
    lay = base_layout(520)
    lay.update(dict(
        title=dict(text=f"누적 수익률 비교 · {period_label}",
                   font=dict(size=14,color="#eef0f8"),x=0.01),
        hovermode="x unified",
    ))
    lay["yaxis"]["ticksuffix"] = "%"
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="ms-section">수익률 랭킹</div>', unsafe_allow_html=True)
    ranks = sorted([{"종목":n,"ret":returns(hdata[t]).iloc[-1]} for n,t in valid.items()],
                   key=lambda x:x["ret"])
    rdf   = pd.DataFrame(ranks)
    fig_b = go.Figure(go.Bar(
        x=rdf["ret"], y=rdf["종목"], orientation="h",
        marker_color=["#e05c6a" if v<0 else "#3ecfb2" for v in rdf["ret"]],
        marker_opacity=0.82,
        text=[f"{v:+.2f}%" for v in rdf["ret"]],
        textposition="outside",
        textfont=dict(color="#eef0f8",size=11,family="SF Mono, Fira Code, monospace"),
        hovertemplate="<b>%{y}</b><br>%{x:.2f}%<extra></extra>",
    ))
    lay_b = base_layout(max(220,len(rdf)*44), extra_margins=dict(r=72))
    lay_b["xaxis"]["ticksuffix"] = "%"
    lay_b["xaxis"]["zerolinecolor"] = "#3d4460"
    fig_b.update_layout(**lay_b)
    st.plotly_chart(fig_b, use_container_width=True)

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="ms-section">캔들스틱 차트</div>', unsafe_allow_html=True)
    cn   = st.selectbox("종목 선택", list(valid.keys()), key="candle")
    ct   = valid[cn]
    hc   = hdata[ct]

    rows = 2 if show_vol else 1
    fig_c = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                          vertical_spacing=0.03,
                          row_heights=[0.74,0.26] if show_vol else [1.0])

    fig_c.add_trace(go.Candlestick(
        x=hc.index, open=hc["Open"], high=hc["High"], low=hc["Low"], close=hc["Close"],
        name=cn,
        increasing_line_color="#3ecfb2", decreasing_line_color="#e05c6a",
        increasing_fillcolor="rgba(62,207,178,.75)", decreasing_fillcolor="rgba(224,92,106,.75)",
    ), row=1, col=1)

    if show_ma:
        for mn, mc in [(20,"#c9a84c"),(60,"#8b8ede")]:
            if len(hc)>=mn:
                fig_c.add_trace(go.Scatter(
                    x=hc.index, y=hc["Close"].rolling(mn).mean(),
                    name=f"MA{mn}", mode="lines",
                    line=dict(color=mc, width=1.5, dash="dot"),
                ), row=1, col=1)

    if show_vol:
        vc = ["#3ecfb2" if hc["Close"].iloc[j]>=hc["Open"].iloc[j] else "#e05c6a"
              for j in range(len(hc))]
        fig_c.add_trace(go.Bar(
            x=hc.index, y=hc["Volume"], marker_color=vc, marker_opacity=0.6,
            name="거래량", showlegend=False,
        ), row=2, col=1)
        fig_c.update_yaxes(gridcolor="#232633",linecolor="#2e3140",
                            tickfont=dict(size=10,color="#8890aa"), row=2, col=1)

    lay_c = base_layout(600)
    lay_c.update(dict(
        title=dict(text=f"{cn} · {period_label}", font=dict(size=14,color="#eef0f8"), x=0.01),
        xaxis_rangeslider_visible=False,
    ))
    lay_c["yaxis"].update(dict(tickformat=",.0f", tickfont=dict(color="#8890aa")))
    fig_c.update_layout(**lay_c)
    st.plotly_chart(fig_c, use_container_width=True)

# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    # 상관관계
    st.markdown('<div class="ms-section">종목 간 수익률 상관관계</div>', unsafe_allow_html=True)
    if len(valid)>=2:
        rdf2 = pd.DataFrame()
        for name,ticker in valid.items():
            h2 = hdata[ticker].copy()
            if h2.index.tz is not None: h2.index = h2.index.tz_localize(None)
            rdf2[name] = h2["Close"].pct_change()*100
        corr = rdf2.corr().round(2)
        fig_hm = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns.tolist(), y=corr.columns.tolist(),
            colorscale=[[0.0,"#e05c6a"],[0.5,"#252830"],[1.0,"#3ecfb2"]],
            zmin=-1, zmax=1,
            text=corr.values, texttemplate="%{text}",
            textfont=dict(size=11, color="#eef0f8"),
            hovertemplate="<b>%{x}</b> vs <b>%{y}</b><br>상관계수: %{z:.2f}<extra></extra>",
        ))
        lay_hm = base_layout(max(320,len(valid)*58), extra_margins=dict(l=14,r=14,t=14,b=14))
        fig_hm.update_layout(**lay_hm)
        st.plotly_chart(fig_hm, use_container_width=True)
    else:
        st.info("종목 2개 이상 선택 시 상관관계 분석이 표시됩니다.")

    # 리스크-수익률
    st.markdown('<div class="ms-section">리스크 — 수익률 분석</div>', unsafe_allow_html=True)
    sc = []
    for i,(name,ticker) in enumerate(valid.items()):
        h = hdata[ticker]
        d = h["Close"].pct_change().dropna()*100
        sc.append({"종목":name,"vol":d.std()*(252**.5),"ret":returns(h).iloc[-1],
                   "c":PALETTE[i%len(PALETTE)]})
    sc_df = pd.DataFrame(sc)

    fig_sc = go.Figure()
    for _,r in sc_df.iterrows():
        fig_sc.add_trace(go.Scatter(
            x=[r["vol"]],y=[r["ret"]], mode="markers+text",
            text=[r["종목"]], textposition="top center",
            textfont=dict(size=11,color=r["c"]),
            marker=dict(size=18,color=r["c"],opacity=.85,
                        line=dict(width=1.5,color="rgba(238,240,248,.2)")),
            hovertemplate=f"<b>{r['종목']}</b><br>변동성: %{{x:.1f}}%<br>수익률: %{{y:.2f}}%<extra></extra>",
            showlegend=False,
        ))
    fig_sc.add_hline(y=0, line_dash="dot", line_color="#3d4460", line_width=1)
    lay_sc = base_layout(440)
    lay_sc["xaxis"]["title"] = "연환산 변동성 (%)"
    lay_sc["yaxis"]["title"] = "누적 수익률 (%)"
    lay_sc["yaxis"]["ticksuffix"] = "%"
    fig_sc.update_layout(**lay_sc)
    st.plotly_chart(fig_sc, use_container_width=True)

    # 요약 테이블
    st.markdown('<div class="ms-section">종목 요약</div>', unsafe_allow_html=True)
    tbl = []
    for name,ticker in valid.items():
        h   = hdata[ticker]
        d   = h["Close"].pct_change().dropna()*100
        ret = returns(h).iloc[-1]
        vol = d.std()*(252**.5)
        mdd = ((h["Close"]/h["Close"].cummax())-1).min()*100
        kr  = is_kr(ticker)
        tbl.append({
            "종목":name, "시장":"🇰🇷 한국" if kr else "🇺🇸 미국",
            "현재가":pfmt(h["Close"].iloc[-1],kr),
            f"수익률 ({period_label})":f"{ret:+.2f}%",
            "연환산 변동성":f"{vol:.1f}%",
            "MDD":f"{mdd:.2f}%",
        })
    tdf = pd.DataFrame(tbl)
    def cret(v):
        if isinstance(v,str) and v.startswith("+"): return "color:#3ecfb2;font-weight:600"
        if isinstance(v,str) and v.startswith("-"): return "color:#e05c6a;font-weight:600"
        return ""
    st.dataframe(tdf.style.applymap(cret), use_container_width=True, hide_index=True)

# ── 푸터 ──────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f'<div class="ms-footer">데이터 출처: Yahoo Finance &nbsp;/&nbsp; '
    f'마지막 갱신: {datetime.now().strftime("%Y-%m-%d %H:%M")} KST</div>',
    unsafe_allow_html=True,
)
