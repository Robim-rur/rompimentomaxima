import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="Scanner de Rompimento de Máxima",
    layout="wide"
)

# =====================================================
# LISTA INTEGRAL DE 178 ATIVOS (NÃO ALTERADA)
# =====================================================
ativos_scan = sorted(set([
    "RRRP3.SA","ALOS3.SA","ALPA4.SA","ABEV3.SA","ARZZ3.SA","ASAI3.SA","AZUL4.SA","B3SA3.SA","BBAS3.SA","BBDC3.SA",
    "BBDC4.SA","BBSE3.SA","BEEF3.SA","BPAC11.SA","BRAP4.SA","BRFS3.SA","BRKM5.SA","CCRO3.SA","CMIG4.SA","CMIN3.SA",
    "COGN3.SA","CPFE3.SA","CPLE6.SA","CRFB3.SA","CSAN3.SA","CSNA3.SA","CYRE3.SA","DXCO3.SA","EGIE3.SA","ELET3.SA",
    "ELET6.SA","EMBR3.SA","ENEV3.SA","ENGI11.SA","EQTL3.SA","EZTC3.SA","FLRY3.SA","GGBR4.SA","GOAU4.SA","GOLL4.SA",
    "HAPV3.SA","HYPE3.SA","ITSA4.SA","ITUB4.SA","JBSS3.SA","KLBN11.SA","LREN3.SA","LWSA3.SA","MGLU3.SA","MRFG3.SA",
    "MRVE3.SA","MULT3.SA","NTCO3.SA","PETR3.SA","PETR4.SA","PRIO3.SA","RADL3.SA","RAIL3.SA","RAIZ4.SA","RENT3.SA",
    "RECV3.SA","SANB11.SA","SBSP3.SA","SLCE3.SA","SMTO3.SA","SUZB3.SA","TAEE11.SA","TIMS3.SA","TOTS3.SA","TRPL4.SA",
    "UGPA3.SA","USIM5.SA","VALE3.SA","VIVT3.SA","VIVA3.SA","WEGE3.SA","YDUQ3.SA","AURE3.SA","BHIA3.SA","CASH3.SA",
    "CVCB3.SA","DIRR3.SA","ENAT3.SA","GMAT3.SA","IFCM3.SA","INTB3.SA","JHSF3.SA","KEPL3.SA","MOVI3.SA","ORVR3.SA",
    "PETZ3.SA","PLAS3.SA","POMO4.SA","POSI3.SA","RANI3.SA","RAPT4.SA","STBP3.SA","TEND3.SA","TUPY3.SA",
    "BRSR6.SA","CXSE3.SA","AAPL34.SA","AMZO34.SA","GOGL34.SA","MSFT34.SA","TSLA34.SA","META34.SA","NFLX34.SA",
    "NVDC34.SA","MELI34.SA","BABA34.SA","DISB34.SA","PYPL34.SA","JNJB34.SA","PGCO34.SA","KOCH34.SA","VISA34.SA",
    "WMTB34.SA","NIKE34.SA","ADBE34.SA","AVGO34.SA","CSCO34.SA","COST34.SA","CVSH34.SA","GECO34.SA","GSGI34.SA",
    "HDCO34.SA","INTC34.SA","JPMC34.SA","MAEL34.SA","MCDP34.SA","MDLZ34.SA","MRCK34.SA","ORCL34.SA","PEP334.SA",
    "PFIZ34.SA","PMIC34.SA","QCOM34.SA","SBUX34.SA","TGTB34.SA","TMOS34.SA","TXN34.SA","UNHH34.SA","UPSB34.SA",
    "VZUA34.SA","ABTT34.SA","AMGN34.SA","AXPB34.SA","BAOO34.SA","CATP34.SA","HONB34.SA","BOVA11.SA","IVVB11.SA",
    "SMAL11.SA","HASH11.SA","GOLD11.SA","GARE11.SA","HGLG11.SA","XPLG11.SA","VILG11.SA","BRCO11.SA","BTLG11.SA",
    "XPML11.SA","VISC11.SA","HSML11.SA","MALL11.SA","KNRI11.SA","JSRE11.SA","PVBI11.SA","HGRE11.SA","MXRF11.SA",
    "KNCR11.SA","KNIP11.SA","CPTS11.SA","IRDM11.SA","DIVO11.SA","NDIV11.SA","SPUB11.SA"
]))

# =====================================================
# MOTOR DE SCANNER (AJUSTADO PARA SETUP PURO)
# =====================================================
def executar_scanner(tickers):
    lista_final = []
    barra_progresso = st.progress(0)
    
    for i, ticker in enumerate(tickers):
        try:
            acao = yf.Ticker(ticker)
            # Pegamos os últimos 6 meses
            dados = acao.history(period="6mo")
            
            if len(dados) < 20: continue

            # Valores cruciais para o setup
            ultimo_fechamento = dados['Close'].iloc[-1]
            maxima_anterior = dados['High'].iloc[-2]
            topo_historico_recente = dados['Close'].max()
            
            # FILTRO CORRIGIDO: Rompimento Real (Fechamento atual >= Máxima de ontem)
            # E estar próximo ao topo histórico do período
            if ultimo_fechamento >= maxima_anterior and ultimo_fechamento >= (topo_historico_recente * 0.97):
                
                # Cálculos de Volatilidade e Momentum para Probabilidade
                retornos = dados['Close'].pct_change()
                vol = retornos.tail(20).std()
                mom = retornos.tail(5).sum()
                
                # Probabilidade Normalizada
                score = (mom / vol) if vol > 0 else 0
                prob = round(min(max(score * 10, 0), 100), 2)
                
                # Valores de Operação
                entrada = round(float(dados['High'].iloc[-1] + 0.01), 2)
                stop_preço = round(float(dados['Low'].iloc[-1] - 0.01), 2)
                
                # % de Loss e % de Ganho (Estatístico para 1 semana)
                loss_percent = round(((entrada - stop_preço) / entrada) * 100, 2)
                gain_est = round((vol * 2.5) * 100, 2) # 2.5 desvios para capturar o potencial

                lista_final.append({
                    "Ativo": ticker,
                    "Probabilidade (%)": prob,
                    "Ganho Est. (1 sem)": f"{gain_est}%",
                    "Risco (Loss %)": f"{loss_percent}%",
                    "Entrada (Gatilho)": entrada,
                    "Stop Loss (Preço)": stop_preço
                })
        except:
            continue
        barra_progresso.progress((i + 1) / len(tickers))
    
    return pd.DataFrame(lista_final)

# =====================================================
# INTERFACE
# =====================================================
st.title("🎯 Scanner de Rompimento de Máxima")
st.markdown("---")

if st.button("🚀 EXECUTAR SCANNER AGORA"):
    with st.spinner("Escaneando ativos..."):
        df = executar_scanner(ativos_scan)
        
        if not df.empty:
            # Ordenamos sempre pela maior probabilidade
            df = df.sort_values(by="Probabilidade (%)", ascending=False)
            
            st.subheader("✅ Ativos que Romperam a Máxima")
            st.dataframe(
                df.style.format({
                    "Probabilidade (%)": "{:.2f}%",
                    "Entrada (Gatilho)": "{:.2f}",
                    "Stop Loss (Preço)": "{:.2f}"
                }).background_gradient(subset=['Probabilidade (%)'], cmap='Greens'),
                use_container_width=True
            )
            st.success("Scanner finalizado. Confira o Risco (Loss %) antes de operar.")
        else:
            st.warning("Nenhum ativo rompeu a máxima nas condições do setup hoje.")

st.divider()
st.caption(f"Setup: Rompimento de Máxima | Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
