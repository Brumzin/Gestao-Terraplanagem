import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

# --- 1. FUNÇÃO DE LOGIN COM TRAVA DE FORMULÁRIO ---
def realizar_login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"] { background-color: #002d4b !important; }
            .login-card {
                background-color: #ffffff; padding: 35px; border-radius: 15px;
                box-shadow: 0px 10px 30px rgba(0,0,0,0.5); text-align: center;
            }
            .stForm { border: none !important; padding: 0 !important; }
            </style>
        """, unsafe_allow_html=True)

        _, col_login, _ = st.columns([1, 1.2, 1])
        
        with col_login:
            st.markdown('<div class="login-card">', unsafe_allow_html=True)
            st.markdown("<h2 style='color: #002d4b; margin-bottom:0;'>🚜 Cristovão Elite</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color: #666; margin-bottom:20px;'>Gestão de Terraplanagem</p>", unsafe_allow_html=True)
            
            with st.form("formulario_login"):
                usuario = st.text_input("Usuário").lower().strip()
                senha = st.text_input("Senha", type="password")
                botao_entrar = st.form_submit_button("Acessar Painel")
                
                if botao_entrar:
                    usuarios_validos = {
                        "cristovao": "admin123",
                        "pai": "sucesso2024"
                    }
                    
                    if usuario in usuarios_validos and senha == usuarios_validos[usuario]:
                        st.session_state["autenticado"] = True
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# --- 2. INÍCIO DO SISTEMA (APÓS LOGIN) ---
if realizar_login():
    st.set_page_config(page_title="Gestão Cristovão Elite", layout="wide", page_icon="🚜")

    # Banco de Dados (CONFIGURADO PARA O DISCO DO RENDER)
    PASTA_SEGURA = '/data'
    DB_FILE = f'{PASTA_SEGURA}/gestao_cristovao_final.csv'
    NOTE_FILE = f'{PASTA_SEGURA}/notas_equipamentos.csv'

    # Garante que a pasta segura é criada se não existir
    if not os.path.exists(PASTA_SEGURA):
        os.makedirs(PASTA_SEGURA, exist_ok=True)

    @st.cache_data
    def carregar_dados():
        if os.path.exists(DB_FILE):
            try:
                d = pd.read_csv(DB_FILE)
                d['Data'] = pd.to_datetime(d['Data'])
                for col in ['Horas', 'Valor', 'Diesel', 'Operador', 'Lucro']:
                    d[col] = pd.to_numeric(d[col], errors='coerce').fillna(0.0)
                return d
            except: pass
        return pd.DataFrame(columns=['Data', 'Cliente', 'Regiao', 'Maquina', 'Servico', 'Horas', 'Valor', 'Diesel', 'Operador', 'Origem', 'Lucro'])

    def carregar_notas():
        if os.path.exists(NOTE_FILE): return pd.read_csv(NOTE_FILE)
        return pd.DataFrame(columns=['Maquina', 'Nota'])

    df = carregar_dados()
    df_notas = carregar_notas()

    # CSS do Painel Principal
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background-color: #F8F9FA !important; }
        .main-header {
            background-color: #002d4b; padding: 25px; border-radius: 12px;
            border-bottom: 6px solid #f7b500; margin-bottom: 25px;
        }
        .main-header h1 { color: #ffffff !important; text-align: center; margin: 0; font-family: 'Arial Black'; }
        .metric-box {
            background-color: #ffffff !important; padding: 15px; border-radius: 12px;
            border-left: 8px solid #002d4b; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); 
            text-align: center; margin-bottom: 15px;
        }
        .m-label { color: #002d4b !important; font-weight: bold; font-size: 14px; display: block; }
        .m-value { color: #002d4b !important; font-size: 24px; font-weight: 800; display: block; }
        .note-card {
            background-color: #ffffff; padding: 12px; border-radius: 8px;
            border-top: 4px solid #f7b500; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
            min-height: 90px; margin-bottom: 10px;
        }
        .stButton>button {
            background-color: #f7b500 !important; color: #002d4b !important;
            width: 100%; font-weight: bold; border-radius: 10px; border: none;
        }
        .row-data { color: #002d4b !important; font-size: 13px !important; font-weight: 600 !important; }
        label, p, h3, span { color: #002d4b !important; font-weight: bold !important; }
        </style>
    """, unsafe_allow_html=True)

    # Listas
    maquinas = ["Retroescavadeira", "Mini Carregadeira (Bobcat)", "Escavadeira Hidráulica", "Pá Carregadeira", "Rolo Compactador", "Caminhão Caçamba"]
    ras_df = sorted(["Águas Claras", "Arniqueira", "Brazlândia", "Candangolândia", "Ceilândia", "Cruzeiro", "Fercal", "Gama", "Guará", "Itapoã", "Jardim Botânico", "Lago Norte", "Lago Sul", "Núcleo Bandeirante", "Paranoá", "Park Way", "Planaltina", "Plano Piloto", "Recanto das Emas", "Riacho Fundo I", "Riacho Fundo II", "Samambaia", "Santa Maria", "São Sebastião", "SCIA/Estrutural", "SIA", "Sobradinho I", "Sobradinho II", "Sol Nascente/Pôr do Sol", "Sudoeste/Octogonal", "Taguatinga", "Varjão", "Vicente Pires"])
    servicos_lista = sorted(["Limpeza de Lote", "Escavação de Piscina", "Nivelamento/Platô", "Abertura de Valas", "Remoção de Entulho", "Transporte de Terra", "Drenagem", "Demolição", "Compactação", "Aterro", "Corte de Terreno", "Escavação de Baldrame", "Escavação de Tanque", "Outro"])
    origens_lista = sorted(["Google Ads", "Instagram", "Facebook", "Indicação Direta", "WhatsApp Business", "Placa no Local", "Cliente Antigo", "Indicação de Engenheiro/Arquiteto"])

    st.markdown('<div class="main-header"><h1>🚜 CRISTOVÃO TERRAPLANAGEM | GESTÃO ELITE</h1></div>', unsafe_allow_html=True)
    if st.sidebar.button("🔒 Sair do Sistema"):
        st.session_state["autenticado"] = False
        st.rerun()

    # Notas
    st.subheader("📋 Notas das Máquinas")
    cols_n = st.columns(6)
    for i, m in enumerate(maquinas):
        nota_val = df_notas[df_notas['Maquina'] == m]['Nota'].values if not df_notas.empty else []
        txt_n = nota_val[0] if len(nota_val) > 0 else "Sem avisos."
        with cols_n[i]:
            st.markdown(f'<div class="note-card"><b style="color:#002d4b;">{m}</b><br><i style="color:#333;">"{txt_n}"</i></div>', unsafe_allow_html=True)
            if st.button(f"Editar {m.split()[0]}", key=f"ed_{i}"):
                st.session_state['edit_m'] = m

    if 'edit_m' in st.session_state:
        with st.form("form_nota"):
            nova = st.text_input(f"Anotação para {st.session_state['edit_m']}")
            if st.form_submit_button("Salvar Nota"):
                if not df_notas.empty:
                    df_notas = df_notas[df_notas['Maquina'] != st.session_state['edit_m']]
                df_notas = pd.concat([df_notas, pd.DataFrame([[st.session_state['edit_m'], nova]], columns=['Maquina', 'Nota'])])
                df_notas.to_csv(NOTE_FILE, index=False)
                del st.session_state['edit_m']
                st.rerun()

    st.divider()

    # Registro
    with st.expander("➕ REGISTRAR NOVO TRABALHO", expanded=True):
        with st.form("form_trabalho", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                f_data = st.date_input("Data", date.today())
                f_cliente = st.text_input("Cliente/Obra")
                f_regiao = st.selectbox("Região do DF (RA)", ras_df)
                f_origem = st.selectbox("Como chegou?", origens_lista)
            with c2:
                f_maquina = st.selectbox("Equipamento", maquinas)
                f_servico = st.selectbox("Serviço Realizado", servicos_lista)
                f_horas = st.text_input("Horas")
            with c3:
                f_valor = st.text_input("Valor Recebido (R$)")
                f_diesel = st.text_input("Gasto Diesel (R$)")
                f_operador = st.text_input("Custo Operador (R$)")
                submit = st.form_submit_button("✅ SALVAR NO SISTEMA")

            if submit:
                def conv(x):
                    try: return float(x.replace(',', '.')) if x and x.strip() else 0.0
                    except: return 0.0
                
                h, v, d, o = conv(f_horas), conv(f_valor), conv(f_diesel), conv(f_operador)
                if v == 0 and h == 0:
                    st.warning("Preencha os valores!")
                else:
                    lucro = v - d - o
                    novo = pd.DataFrame([[f_data, f_cliente, f_regiao, f_maquina, f_servico, h, v, d, o, f_origem, lucro]], columns=df.columns if not df.empty else ['Data', 'Cliente', 'Regiao', 'Maquina', 'Servico', 'Horas', 'Valor', 'Diesel', 'Operador', 'Origem', 'Lucro'])
                    novo.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                    st.cache_data.clear()
                    st.toast("✅ Salvo com sucesso!")
                    st.rerun()

    # Dashboards
    if not df.empty:
        st.subheader("📊 Performance Cristovão")
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-box"><span class="m-label">Faturamento</span><span class="m-value">R$ {df["Valor"].sum():,.2f}</span></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-box" style="border-left-color:#f7b500"><span class="m-label">Diesel</span><span class="m-value">R$ {df["Diesel"].sum():,.2f}</span></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-box" style="border-left-color:#f7b500"><span class="m-label">Operador</span><span class="m-value">R$ {df["Operador"].sum():,.2f}</span></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-box" style="border-left-color:#28a745"><span class="m-label">LUCRO REAL</span><span class="m-value" style="color:#28a745 !important">R$ {df["Lucro"].sum():,.2f}</span></div>', unsafe_allow_html=True)

        g1, g2 = st.columns(2)
        with g1:
            fig1 = px.bar(df.groupby('Regiao')['Lucro'].sum().reset_index(), x='Regiao', y='Lucro', title="Lucro por Bairro", template="plotly_white", color_discrete_sequence=['#002d4b'])
            st.plotly_chart(fig1, use_container_width=True)
        with g2:
            fig2 = px.pie(df, values='Lucro', names='Maquina', title="Equipamentos", hole=.4, template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📋 Histórico")
        for i, row in df.sort_index(ascending=False).iterrows():
            r = st.columns([1, 1.2, 1.2, 0.8, 1, 1, 1, 1, 0.5])
            r[0].write(pd.to_datetime(row['Data']).strftime('%d/%m/%Y'))
            r[1].write(row['Cliente'])
            r[2].write(row['Maquina'])
            r[3].write(f"{row['Horas']}h")
            r[4].write(f"R${row['Valor']:,.0f}")
            r[7].write(f"**R${row['Lucro']:,.0f}**")
            if r[8].button("🗑️", key=f"del_{i}"):
                df.drop(i).to_csv(DB_FILE, index=False)
                st.cache_data.clear()
                st.rerun()
        
        st.download_button("📥 BAIXAR PLANILHA", df.to_csv(index=False).encode('utf-8'), f"gestao_{date.today()}.csv", "text/csv")
    else:
        st.info("Aguardando lançamentos...")