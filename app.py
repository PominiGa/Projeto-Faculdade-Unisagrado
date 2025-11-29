import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Dashboard COVID-19 Brasil", layout="wide")
st.title("📊 Dashboard COVID-19 Brasil - Dados oficiais Brasil.io")

url = "https://data.brasil.io/dataset/covid19/caso_full.csv.gz"
df = pd.read_csv(url, compression="gzip")

df = df[df["place_type"] == "state"]

df.rename(columns={
    "state": "estado",
    "date": "data",
    "last_available_confirmed": "casos_confirmados",
    "last_available_deaths": "obitos_confirmados",
}, inplace=True)

df["data"] = pd.to_datetime(df["data"])

latest_date = df["data"].max()
df_latest = df[df["data"] == latest_date]

st.markdown(f"### Dados mais recentes: **{latest_date.date()}**")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de casos", f"{df_latest['casos_confirmados'].sum():,}".replace(",", "."))
col2.metric("Total de óbitos", f"{df_latest['obitos_confirmados'].sum():,}".replace(",", "."))
col3.metric("Estados Registrados", len(df_latest))
col4.metric("Taxa de Mortalidade (%)",
            round((df_latest["obitos_confirmados"].sum() / df_latest["casos_confirmados"].sum()) * 100, 2))

st.divider()

st.subheader("🏆 Ranking dos Estados (Mais Casos / Mais Óbitos)")

colA, colB = st.columns(2)

top_casos = df_latest.sort_values("casos_confirmados", ascending=False)[["estado", "casos_confirmados"]]
top_obitos = df_latest.sort_values("obitos_confirmados", ascending=False)[["estado", "obitos_confirmados"]]

colA.write("### Estados com mais casos")
colA.dataframe(top_casos, height=300)

colB.write("### Estados com mais óbitos")
colB.dataframe(top_obitos, height=300)

st.divider()

estados = sorted(df_latest["estado"].unique())
estado_selecionado = st.selectbox("Selecione um Estado", estados)

filtro = df[df["estado"] == estado_selecionado].copy()

filtro["media_casos"] = filtro["casos_confirmados"].diff().rolling(7).mean()
filtro["media_obitos"] = filtro["obitos_confirmados"].diff().rolling(7).mean()

st.subheader(f"📈 Evolução no Estado: {estado_selecionado}")

fig1 = px.line(filtro, x="data", y="casos_confirmados",
               title=f"Evolução de Casos Acumulados - {estado_selecionado}")
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(filtro, x="data", y="obitos_confirmados",
               title=f"Óbitos Acumulados - {estado_selecionado}")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📉 Média Móvel (Top 7 maiores picos)")

filtro["media_casos"] = filtro["casos_confirmados"].diff().rolling(7).mean()
filtro["media_obitos"] = filtro["obitos_confirmados"].diff().rolling(7).mean()

filtro_mm = filtro.dropna(subset=["media_casos", "media_obitos"])

top7_casos = filtro_mm.nlargest(7, "media_casos").sort_values("data")
top7_obitos = filtro_mm.nlargest(7, "media_obitos").sort_values("data")

fig3 = px.line(top7_casos, x="data", y="media_casos",
               title="Top 7 maiores picos - Média Móvel de Casos (7 dias)")
st.plotly_chart(fig3, use_container_width=True)

fig4 = px.line(top7_obitos, x="data", y="media_obitos",
               title="Top 7 maiores picos - Média Móvel de Óbitos (7 dias)")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("📊 Comparação entre estados")

fig5 = px.bar(df_latest.sort_values("casos_confirmados", ascending=False),
              x="estado", y="casos_confirmados", title="Casos por Estado")
st.plotly_chart(fig5, use_container_width=True)

fig6 = px.bar(df_latest.sort_values("obitos_confirmados", ascending=False),
              x="estado", y="obitos_confirmados", title="Óbitos por Estado")
st.plotly_chart(fig6, use_container_width=True)

st.divider()

import json
import requests

geo_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
geojson = requests.get(geo_url).json()

df_latest["estado"] = df_latest["estado"].str.upper()

fig7 = px.choropleth(
    df_latest,
    geojson=geojson,
    locations="estado",
    featureidkey="properties.sigla", 
    color="casos_confirmados",
    color_continuous_scale="Reds",
    title="Mapa de Casos Confirmados por Estado",
)

fig7.update_geos(fitbounds="locations", visible=False)

st.plotly_chart(fig7, use_container_width=True)


st.subheader("📌 Evolução Nacional")

df_brasil = df.groupby("data")[["casos_confirmados", "obitos_confirmados"]].sum().reset_index()

fig8 = px.line(df_brasil, x="data", y="casos_confirmados", title="Casos acumulados no Brasil")
fig9 = px.line(df_brasil, x="data", y="obitos_confirmados", title="Óbitos acumulados no Brasil")

st.plotly_chart(fig8, use_container_width=True)
st.plotly_chart(fig9, use_container_width=True)
