import streamlit as st

import pandas as pd
import plotly.graph_objects as go

import networkx as nx


st.set_page_config(page_title="Global Conflict Dashboard",
                   layout="wide")
from pathlib import Path
st.markdown(f"<style>{Path('style.css').read_text(encoding='utf-8')}</style>",
             unsafe_allow_html=True)

with st.sidebar:
    st.title("Global Conflict Dashboard")
    st.caption("데이터로 보는 세계의 관계")
    page = st.radio('메뉴',['개요','국가 간 관계 분석','분쟁 원인 분석','무기 거래 추이','데이터 소개'])
    st.divider()
    st.subheader('필터')
    period = st.slider("기간", 2020, 2025, (2020,2025))
    region = st.selectbox('지역',['전체','영토','정치','이념','종교','민족'])
    cause = st.selectbox('분쟁 원인',['전체','영토','정치','이념','종교','민족'])
    st.button('적용하기', type='primary', use_container_width=True)

def kpi_card(icon, label, value, delta, tone):
    return f"""
<div class="kpi {tone}">
  <div class="ico">{icon}</div>
  <div>
    <div class="lbl">{label}</div>
    <div class="val">{value}<span class="delta">{delta}</span></div>
  </div>
</div>
"""

def sparkline(values, width=90, height=32, color="#ef4444"):
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    pts = []
    for i, v in enumerate(values):
        x = i / (len(values) - 1) * width
        y = height - (v - lo) / span * height
        pts.append(f"{x:.1f},{y:.1f}")
    return f'<svg width="{width}" height="{height}"><polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2"/></svg>'

def page_overview():
    st.title('분쟁의 원인과 국가 간 관계, 데이터로 보다')
    st.caption('정치, 영토, 이념, 종교, 민족 등 다양한 이유로 발생하는 국제 분쟁을 분석합니다.')

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card("🌐", "진행 중인 주요 분쟁", "7건", "▲ 2", "blue"), unsafe_allow_html=True)
    c2.markdown(kpi_card("👥", "집중 분석 국가 수", "17개국", "+ 상대국 7", ""), unsafe_allow_html=True)
    c3.markdown(kpi_card("⚠️", "분쟁 이벤트 수 (GDELT)", "210,842건", "▲ 18.7%", "red"), unsafe_allow_html=True)
    c4.markdown(kpi_card("🪖", "관련 무기 거래 규모", "98.3 B", "▲ 11.4%", "green"), unsafe_allow_html=True)



    left, right = st.columns([1.2, 1])

    with left:
        with st.container(border=True):
            st.subheader('세계 분쟁 현황 지도')

            df = pd.DataFrame({
                "iso3": ["ISR", "PSE", "LBN", "SYR", "IRN", "YEM", "KOR", "PRK"],
                "intensity": [4, 4, 3, 3, 3, 3, 2, 2],})

            markers = pd.DataFrame({
                "name": ["이스라엘-팔레스타인", "예멘 내전", "시리아", "한반도"],
                "lat": [31.5, 15.5, 35.0, 38.3],
                "lon": [34.8, 47.5, 38.5, 127.0],
            })


            fig = go.Figure(go.Choropleth(
                locations=df['iso3'],
                z=df['intensity'],
                colorscale='Reds',
                showscale=False
            ))

            fig.add_trace(go.Scattergeo(
                lat=markers["lat"],
                lon=markers["lon"],
                text=markers["name"],
                mode="markers+text",
                textposition=["bottom right", "bottom center", "top right", "top center"],
                textfont=dict(color="#ffffff", size=11),
                marker=dict(size=12, color="#ef4444", line=dict(color="#ffffff", width=2)),
            ))

            fig.update_geos(
                fitbounds="locations",
                bgcolor="rgba(0,0,0,0)",
                showland=True, landcolor="#243247",
                showocean=True, oceancolor="#0f1a2e",
                showcountries=True, countrycolor="#1e293b",
            )
            fig.update_layout(height=400, margin=dict(l=0,r=0,t=0,b=0),
                               paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#cbd5e1"))
            st.plotly_chart(fig, use_container_width=True)

        with st.container(border=True):
            st.subheader('분쟁 원인별 국가 간 관계 네트워크')

            G = nx.Graph()
            G.add_edge("이스라엘", "팔레스타인", rel="적대")
            G.add_edge("이스라엘", "이란", rel="적대")
            G.add_edge("이스라엘", "미국", rel="우호")
            G.add_edge("팔레스타인", "이란", rel="우호")
            G.add_edge("팔레스타인", "카타르", rel="우호")

            role = {"이스라엘": "분쟁국", "팔레스타인": "분쟁국",
                    "이란": "관련국", "미국": "관련국", "카타르": "중재국"}
            pos = nx.spring_layout(G, seed=7)
            pos = nx.spring_layout(G, seed=7)
            fig = go.Figure()

            rel_color = {"적대": "#ef4444", "우호": "#3b82f6"}
            for rel, color in rel_color.items():
                xs, ys = [], []
                for a, b, d in G.edges(data=True):
                    if d["rel"] == rel:
                        xs += [pos[a][0], pos[b][0], None]
                        ys += [pos[a][1], pos[b][1], None]
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines",
                                         line=dict(color=color, width=2),
                                         name=f"{rel} 관계", hoverinfo="skip"))

            role_color = {"분쟁국": "#ef4444", "관련국": "#3b82f6", "중재국": "#22c55e"}
            for r, color in role_color.items():
                nodes = [n for n in G.nodes() if role[n] == r]
                fig.add_trace(go.Scatter(
                    x=[pos[n][0] for n in nodes],
                    y=[pos[n][1] for n in nodes],
                    mode="markers+text",
                    text=nodes,
                    textposition="bottom center",
                    textfont=dict(color="#e5eaf3"),
                    marker=dict(size=24, color=color, line=dict(color="#ffffff", width=2)),
                    name=r,
                ))

            fig.update_layout(height=350, showlegend=True,
                              legend=dict(x=1.02, y=1, bgcolor="rgba(17,26,46,0.8)"),
                              xaxis=dict(visible=False), yaxis=dict(visible=False),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#cbd5e1"))
            st.plotly_chart(fig, use_container_width=True)

    with right:
        with st.container(border=True):
            st.subheader('주요 분쟁 사례')

            cases = [
                ("이스라엘-팔레스타인", "1948 - 현재", 32417, ["영토", "종교", "민족"], [2, 2, 3, 3, 4, 5, 9, 12, 11, 13, 14, 15]),
                ("예멘 내전", "2014 - 현재", 9500, ["종교", "권력", "지정학"], [6, 6, 5, 5, 4, 4, 5, 6, 6, 5, 5, 5]),
                ("시리아", "2011 - 현재", 12000, ["정치", "종교", "민족"], [7, 6, 6, 5, 5, 4, 4, 5, 8, 7, 6, 6]),
                ("한반도", "1953 - 현재", 6100, ["이념", "영토", "정치"], [3, 3, 4, 4, 5, 4, 5, 6, 6, 7, 7, 8]),
            ]
            for name, period, events, tags, trend in cases:
                a, b = st.columns([2, 1])
                tag_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
                a.markdown(f"**{name}** <span class='period'>{period}</span><br>{tag_html}", unsafe_allow_html=True)
                b.markdown(f"<div class='ev'><div class='l'>이벤트 수</div><div class='v'>{events:,}</div>{sparkline(trend)}</div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.subheader("선택한 분쟁의 상세 분석")
            selected = st.selectbox("분쟁 선택", [c[0] for c in cases])
            st.markdown(f"""
    | 항목 | 내용 |
    |---|---|
    | 분쟁 | {selected} |
    | 주요 원인 | 영토, 종교 |
    | 관련 국가 | 미국, 이란 |
    """)
            months = pd.date_range("2020-01-01", "2025-06-01", freq="MS")
            values = [200 + i * 40 for i in range(len(months))]

            fig = go.Figure(go.Scatter(x=months, y=values, mode="lines",
                                    fill="tozeroy", line=dict(color="#ef4444")))
            fig.update_layout(height=200, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)

def page_placeholder(title):
    st.title(title)
    st.info("이 페이지는 준비 중입니다. 데이터가 추가되면 여기에 분석이 들어갑니다.")


if page == "개요":
    page_overview()
else:
    page_placeholder(page)