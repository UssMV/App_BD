import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import io
import zipfile
import warnings
warnings.filterwarnings('ignore')

# =====================================================================
# CONFIGURAÇÕES POR TIPO
# =====================================================================

# ---------- SOLO (SO) ----------
MAPA_HEADERS_SO = {
    'REMESSA':                    'REMESSA_MT',
    'Project':                    'Project',
    'ANM_ID':                     'ANM_ID_MT',
    'ALVO':                       'ALVO_MT',
    'MATRIZ':                     'MATRIZ_MT',
    'coordinates.Grid':           'coordinates.Grid',
    'converted.coordinates.Grid': 'converted.coordinates.Grid',
    'DATA':                       'DATA',
    'coordinates.Easting':        'coordinates.Easting',
    'coordinates.Northing':       'coordinates.Northing',
    'coordinates.Elevation':      'coordinates.Elevation',
    'Point number':               'Point number',
    'Sample Number':              'Sample Number',
    'coordinates.Type':           'coordinates.Type',
    'COLETOR':                    'COLETOR_MT',
    'RESPONSAVEL':                'RESPONSAVEL_MT',
    'VEGETACAO':                  'VEGETACAO_MT',
    'REGIME':                     'REGIME_MT',
    'LITOLOGIA':                  'LITOLOGIA_MT',
    'ACAO_ANTROPICA':             'ACAO_ANTROPICA_MT',
    'SOLO':                       'SOLO',
    'COR':                        'COR_MT',
    'GRANULOMETRIA':              'GRANULOMETRIA',
    'MASSA_KG':                   'MASSA_KG',
    'AFLORAMENTO':                'AFLORAMENTO',
    'MAGNETISMO':                 'MAGNETISMO_MT',
    'DESCRICAO':                  'DESCRICAO',
    'RESPONSAVEL_BATEIA':         'RESPONSAVEL_BATEIA_MT',
    'FINISSIMAS':                 'FINISSIMAS',
    'FINAS':                      'FINAS',
    'MEDIA':                      'MEDIA',
    'GROSSA':                     'GROSSA',
    'LABORATORIO':                'LABORATORIO_MT',
    'PREPARACAO':                 'PREPARACAO_MT',
    'METODOLOGIA_1':              'METODOLOGIA_1_MT',
    'METODOLOGIA_2':              'METODOLOGIA_2_MT',
    'METODOLOGIA_3':              'METODOLOGIA_3_MT',
}

ABAS_SO = ('DEPOSITY_HEADERS_SOLO', 'DEPOSITY_SAMPLE_SOLO')

COLUNAS_OBRIGATORIAS_SO = [
    'REMESSA_MT', 'Project', 'ANM_ID_MT', 'ALVO_MT', 'DATA',
    'Sample Number', 'coordinates.Easting', 'coordinates.Northing',
    'coordinates.Elevation', 'COLETOR_MT', 'RESPONSAVEL_MT',
]

# ---------- ROCHA (RK) ----------
MAPA_HEADERS_RK = {
    'REMESSA':                         'REMESSA_MT',
    'Project':                         'Project',
    'ANM_ID':                          'ANM_ID_MT',
    'ALVO':                            'ALVO_MT',
    'TIPO_MATRIZ':                     'TIPO_MATRIZ',
    'coordinates.Grid':                'coordinates.Grid',
    'DATA':                            'DATA',
    'coordinates.Easting':             'coordinates.Easting',
    'coordinates.Northing':            'coordinates.Northing',
    'coordinates.Elevation':           'coordinates.Elevation',
    'Point number':                    'Point number',
    'Sample Number':                   'Sample Number',
    'coordinates.Type':                'coordinates.Type',
    'COLETOR':                         'COLETOR_MT',
    'RESPONSAVEL':                     'RESPONSAVEL_MT',
    'LITOLOGIA':                       'LITOLOGIA_MT',
    'FORMA_DE_OCORRENCIA':             'FORMAS_DE_OCORRENCIA_MT',
    'GRAU_DE_INTEMPERISMO':            'GRAU_DE_INTEMPERISMO_MT',
    'SULFETOS_OXIDOS_MINERAIS_NATIVOS':'SULFETOS_OXIDOS_MINERAIS_NATIVOS',
    'MAGNETISMO':                      'MAGNETISMO_MT',
    'OBSERVACAO':                      'OBSERVACAO',
    'RESPONSAVEL_BATEIA':              'RESPONSAVEL_BATEIA_MT',
    'FINISSIMAS':                      'FINISSIMAS',
    'FINAS':                           'FINAS',
    'MEDIA':                           'MEDIA',
    'GROSSA':                          'GROSSA',
    'LABORATORIO':                     'LABORATORIO_MT',
    'PREPARACAO':                      'PREPARACAO_MT',
    'METODOLOGIA_1':                   'METODOLOGIA_1_MT',
    'METODOLOGIA_2':                   'METODOLOGIA_2_MT',
    'METODOLOGIA_3':                   'METODOLOGIA_3_MT',
}

COLUNAS_EXTRA_RK = [
    'converted.coordinates.Grid',
    'converted.coordinates.Northing',
    'converted.coordinates.Easting',
]

ORDEM_HEADERS_RK = [
    'Project', 'Point number', 'TIPO_MATRIZ',
    'ANM_ID_MT', 'ALVO_MT', 'DATA', 'REMESSA_MT', 'COLETOR_MT',
    'RESPONSAVEL_MT', 'LITOLOGIA_MT', 'FORMAS_DE_OCORRENCIA_MT',
    'GRAU_DE_INTEMPERISMO_MT', 'SULFETOS_OXIDOS_MINERAIS_NATIVOS',
    'MAGNETISMO_MT', 'OBSERVACAO', 'RESPONSAVEL_BATEIA_MT',
    'FINISSIMAS', 'FINAS', 'MEDIA', 'GROSSA',
    'LABORATORIO_MT', 'PREPARACAO_MT',
    'METODOLOGIA_1_MT', 'METODOLOGIA_2_MT', 'METODOLOGIA_3_MT',
    'Sample Number', 'coordinates.Type', 'coordinates.Grid',
    'converted.coordinates.Grid', 'coordinates.Northing',
    'converted.coordinates.Northing', 'coordinates.Easting',
    'converted.coordinates.Easting', 'coordinates.Elevation',
]

ABAS_RK = ('DEPOSITY_HEADERS_ROCHA', 'DEPOSITY_SAMPLE_ROCHA')

COLUNAS_OBRIGATORIAS_RK = [
    'REMESSA_MT', 'Project', 'ANM_ID_MT', 'ALVO_MT', 'DATA',
    'Sample Number', 'coordinates.Easting', 'coordinates.Northing',
    'coordinates.Elevation', 'COLETOR_MT', 'RESPONSAVEL_MT',
]

COLUNAS_COORDENADAS   = ['coordinates.Easting', 'coordinates.Northing', 'coordinates.Elevation']
COLUNAS_GRANULOMETRIA = ['FINISSIMAS', 'FINAS', 'MEDIA', 'GROSSA']


# =====================================================================
# FUNÇÕES DE PROCESSAMENTO (mesmas do original, sem tkinter)
# =====================================================================

def corrigir_litologia(df: pd.DataFrame) -> dict:
    correcoes = {
        'total_alteracoes': 0,
        'linhas_alteradas': [],
        'valores_originais': {}
    }
    if 'LITOLOGIA_MT' not in df.columns:
        return correcoes
    for idx in df.index:
        valor = df.at[idx, 'LITOLOGIA_MT']
        if pd.notna(valor) and isinstance(valor, str):
            if valor.lower().strip() == 'gran' and valor != 'GRAN':
                correcoes['total_alteracoes'] += 1
                correcoes['linhas_alteradas'].append(idx + 2)
                correcoes['valores_originais'][idx + 2] = valor
                df.at[idx, 'LITOLOGIA_MT'] = 'GRAN'
    return correcoes


def adaptar_headers(df_raw: pd.DataFrame, tipo: str):
    df   = df_raw.copy()
    mapa = MAPA_HEADERS_RK if tipo == 'RK' else MAPA_HEADERS_SO

    df = df.rename(columns=mapa)

    if tipo == 'RK':
        for col in COLUNAS_EXTRA_RK:
            if col not in df.columns:
                df[col] = np.nan
        df = df[[c for c in ORDEM_HEADERS_RK if c in df.columns]]

        if 'FORMAS_DE_OCORRENCIA_MT' in df.columns:
            df['FORMAS_DE_OCORRENCIA_MT'] = (
                df['FORMAS_DE_OCORRENCIA_MT']
                .astype(str)
                .str.replace('SUPERFÍCIE', 'SUPERFICIE', regex=False)
                .str.replace('SUPERFICE',  'SUPERFICIE', regex=False)
            )
            df['FORMAS_DE_OCORRENCIA_MT'] = df['FORMAS_DE_OCORRENCIA_MT'].replace('nan', np.nan)

        correcoes_litologia = corrigir_litologia(df)
    else:
        colunas_alvo = list(MAPA_HEADERS_SO.values())
        df = df[[c for c in colunas_alvo if c in df.columns]]

        if 'MASSA_KG' in df.columns:
            df['MASSA_KG'] = df['MASSA_KG'].astype(str).str.replace(',', '.', regex=False)
            df['MASSA_KG'] = pd.to_numeric(df['MASSA_KG'], errors='coerce')
            mask = (df['MASSA_KG'] > 1) & (df['MASSA_KG'] < 1000)
            df.loc[mask, 'MASSA_KG'] = df.loc[mask, 'MASSA_KG'] / 1000

        for col in COLUNAS_GRANULOMETRIA:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')

        correcoes_litologia = {'total_alteracoes': 0, 'linhas_alteradas': [], 'valores_originais': {}}

    if 'DATA' in df.columns:
        df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce').dt.strftime('%d/%m/%Y')

    if 'coordinates.Type' in df.columns:
        era_control = (
            df['coordinates.Type'].astype(str).str.strip().str.upper() == 'CONTROL'
        )
        df['coordinates.Type'] = 'ATUAL'
    else:
        era_control = pd.Series(False, index=df.index)

    for col in COLUNAS_COORDENADAS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    for col_desc in ['DESCRICAO', 'OBSERVACAO']:
        if col_desc in df.columns:
            mask_curto = (
                df[col_desc].notna() &
                (df[col_desc].astype(str).str.strip().str.len() <= 2) &
                (df[col_desc].astype(str).str.strip() != '')
            )
            df.loc[mask_curto, col_desc] = np.nan

    df = df.replace({'#ERROR!': np.nan, '': np.nan, ' ': np.nan, 'nan': np.nan})
    df['Point Status'] = 'inprogress'
    return df, era_control, correcoes_litologia


def adaptar_sample(df_raw: pd.DataFrame, tipo: str) -> pd.DataFrame:
    df = df_raw.copy()

    if 'parent sample number' not in df.columns:
        for alt in ['parent_sample_number', 'parent', 'Parent']:
            if alt in df.columns:
                df['parent sample number'] = df[alt]
                break
        else:
            df['parent sample number'] = np.nan

    colunas_esperadas = ['Point number', 'Sample Number', 'Sample Type',
                         'Control Type', 'COMENTARIOS', 'parent sample number']

    df = df[[c for c in colunas_esperadas if c in df.columns]]

    if 'Point number' in df.columns:
        df['Point number'] = df['Point number'].astype(str).str.strip()
        df['Point number'] = df['Point number'].replace({'nan': '', 'None': '', '<NA>': ''})

    if 'Sample Number' in df.columns:
        df['Sample Number'] = pd.to_numeric(df['Sample Number'], errors='coerce').astype('Int64')

    if 'parent sample number' in df.columns:
        df['parent sample number'] = pd.to_numeric(
            df['parent sample number'], errors='coerce'
        ).astype('Int64')

    if 'Control Type' in df.columns:
        df['Control Type'] = df['Control Type'].replace('BLK1', 'BLKM1')

    if 'Sample Type' in df.columns and 'Point number' in df.columns:
        mask_dup1 = df['Sample Type'] == 'DUP1'
        df.loc[mask_dup1, 'Sample Type'] = 'DUP'

        mask_todos_dup = df['Sample Type'] == 'DUP'
        if mask_todos_dup.any() and 'parent sample number' in df.columns and 'Sample Number' in df.columns:
            mask_originais = ~mask_todos_dup & df['Sample Number'].notna() & (df['Point number'] != '')
            mapa_samplenum_pointnum = (
                df.loc[mask_originais]
                .set_index('Sample Number')['Point number']
                .to_dict()
            )
            for idx in df.index[mask_todos_dup]:
                parent_num = df.at[idx, 'parent sample number']
                if pd.isna(parent_num):
                    continue
                point_original = mapa_samplenum_pointnum.get(parent_num)
                if point_original:
                    df.at[idx, 'Point number'] = point_original

    for col in df.columns:
        if pd.api.types.is_extension_array_dtype(df[col]):
            df[col] = df[col].astype(object).where(df[col].notna(), other='')
            df[col] = df[col].apply(lambda x: str(x) if x != '' else '')

    df = df.fillna('')
    return df


def validar_campos_obrigatorios(df_headers: pd.DataFrame,
                                era_control: pd.Series,
                                tipo: str) -> dict:
    colunas_obrig = COLUNAS_OBRIGATORIAS_RK if tipo == 'RK' else COLUNAS_OBRIGATORIAS_SO
    df_val = df_headers[~era_control]
    problemas = {}
    for col in colunas_obrig:
        if col not in df_val.columns:
            problemas[col] = ['COLUNA AUSENTE NA PLANILHA']
            continue
        vazias = df_val.index[
            df_val[col].isna() |
            (df_val[col].astype(str).str.strip() == '')
        ].tolist()
        if vazias:
            problemas[col] = [i + 2 for i in vazias]
    return problemas


def processar_excel(arquivo_bytes, nome_arquivo, tipo):
    """Processa o arquivo Excel e retorna os DataFrames e problemas encontrados."""
    tipo = tipo.upper()
    aba_h, aba_s = ABAS_RK if tipo == 'RK' else ABAS_SO

    abas = pd.read_excel(io.BytesIO(arquivo_bytes), sheet_name=None)

    abas_faltando = [n for n in (aba_h, aba_s) if n not in abas]
    if abas_faltando:
        raise KeyError(f"Aba(s) não encontrada(s): {abas_faltando}. Disponíveis: {list(abas.keys())}")

    df_headers, era_control, correcoes_litologia = adaptar_headers(abas[aba_h], tipo)
    df_sample = adaptar_sample(abas[aba_s], tipo)

    problemas = validar_campos_obrigatorios(df_headers, era_control, tipo)
    df_headers['Point Status'] = 'inprogress'

    return df_headers, df_sample, problemas, correcoes_litologia, list(abas.keys())


def gerar_zip(df_headers, df_sample, problemas, correcoes_litologia, nome_base, tipo):
    """Empacota os CSVs e o relatório texto num arquivo ZIP em memória."""
    tipo_label = 'ROCHA' if tipo == 'RK' else 'SOLO'
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        # CSV HEADERS
        csv_h = df_headers.to_csv(index=False, encoding='utf-8-sig')
        zf.writestr(f'{nome_base}_header.csv', csv_h)

        # CSV SAMPLE
        csv_s = df_sample.to_csv(index=False, encoding='utf-8-sig')
        zf.writestr(f'{nome_base}_DEPOSITY_SAMPLE_{tipo_label}.csv', csv_s)

        # Relatório TXT
        relatorio = gerar_relatorio_txt(df_headers, df_sample, problemas,
                                        correcoes_litologia, nome_base, tipo)
        zf.writestr(f'{nome_base}_Relatorio_{tipo_label}.txt', relatorio)

    buf.seek(0)
    return buf


def gerar_relatorio_txt(df_headers, df_sample, problemas, correcoes_litologia,
                        nome_arquivo, tipo):
    """Gera um relatório de texto simples (substitui o PDF no ambiente web)."""
    tipo_label = 'ROCHA' if tipo == 'RK' else 'SOLO'
    aba_h = ABAS_RK[0] if tipo == 'RK' else ABAS_SO[0]
    aba_s = ABAS_RK[1] if tipo == 'RK' else ABAS_SO[1]
    now = datetime.now().strftime('%d/%m/%Y %H:%M')
    n_erros = sum(len(v) for v in problemas.values() if v != ['COLUNA AUSENTE NA PLANILHA'])
    status = 'APROVADO' if not problemas else 'REPROVADO'

    linhas = [
        '=' * 70,
        f'  RELATÓRIO DE REVISÃO DE PLANILHAS — {tipo_label}',
        f'  Arquivo : {nome_arquivo}',
        f'  Gerado  : {now}',
        '=' * 70,
        '',
        '[ RESUMO ]',
        f'  Registros HEADERS  : {len(df_headers)}',
        f'  Registros SAMPLE   : {len(df_sample)}',
        f'  Campos c/ problema : {len(problemas)}',
        f'  Células vazias     : {n_erros}',
        f'  Status geral       : {status}',
        '',
    ]

    if tipo == 'RK' and correcoes_litologia['total_alteracoes'] > 0:
        linhas += [
            '[ CORREÇÕES LITOLOGIA_MT ]',
            f'  {correcoes_litologia["total_alteracoes"]} ocorrência(s) de "gran" → "GRAN"',
            f'  Linhas alteradas: {correcoes_litologia["linhas_alteradas"][:50]}',
            '',
        ]

    linhas += [
        f'[ 1. PLANILHA {aba_h} ]',
        f'  Total registros: {len(df_headers)} | Total colunas: {len(df_headers.columns)}',
        '',
        '  Verificação de campos obrigatórios:',
    ]

    colunas_obrig = COLUNAS_OBRIGATORIAS_RK if tipo == 'RK' else COLUNAS_OBRIGATORIAS_SO
    for col in colunas_obrig:
        if col in problemas:
            v = problemas[col]
            if v == ['COLUNA AUSENTE NA PLANILHA']:
                linhas.append(f'  ✗ {col}: COLUNA AUSENTE')
            else:
                linhas.append(f'  ✗ {col}: {len(v)} célula(s) vazia(s) → linhas {v[:10]}{"..." if len(v)>10 else ""}')
        else:
            linhas.append(f'  ✓ {col}: OK')

    linhas += [
        '',
        f'[ 2. PLANILHA {aba_s} ]',
        f'  Total registros: {len(df_sample)} | Total colunas: {len(df_sample.columns)}',
    ]

    if 'Control Type' in df_sample.columns:
        n_blk = int((df_sample['Control Type'] == 'BLKM1').sum())
        linhas.append(f'  Correções BLK1 → BLKM1: {n_blk}')
    if 'Sample Type' in df_sample.columns:
        n_dup = int((df_sample['Sample Type'] == 'DUP').sum())
        linhas.append(f'  Amostras DUP resolvidas: {n_dup}')

    linhas += [
        '',
        '=' * 70,
        '  Relatório gerado automaticamente pelo Sistema Deposity — Streamlit',
        '=' * 70,
    ]

    return '\n'.join(linhas)


# =====================================================================
# INTERFACE STREAMLIT
# =====================================================================

st.set_page_config(
    page_title="Verificação Deposity",
    page_icon="🪨",
    layout="wide",
)

st.title("🪨 Sistema de Verificação de Planilhas Deposity")
st.markdown("Faça o upload do arquivo Excel, escolha o tipo e processe automaticamente.")

# --- Sidebar: configurações ---
with st.sidebar:
    st.header("⚙️ Configurações")
    tipo_planilha = st.radio(
        "Tipo de planilha",
        options=["SO — Solo", "RK — Rocha"],
        index=0,
    )
    tipo = "SO" if tipo_planilha.startswith("SO") else "RK"
    st.markdown("---")
    st.caption("Abas esperadas no Excel:")
    if tipo == "SO":
        st.code("\n".join(ABAS_SO))
    else:
        st.code("\n".join(ABAS_RK))

# --- Upload ---
uploaded = st.file_uploader(
    "📂 Selecione o arquivo Excel (.xlsx / .xls)",
    type=["xlsx", "xls"],
)

if uploaded:
    nome_base = Path(uploaded.name).stem
    arquivo_bytes = uploaded.read()

    if st.button("▶️ Processar planilha", type="primary"):
        with st.spinner("Processando…"):
            try:
                df_h, df_s, problemas, correcoes_lit, abas_encontradas = processar_excel(
                    arquivo_bytes, uploaded.name, tipo
                )
            except KeyError as e:
                st.error(f"❌ {e}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")
                st.stop()

        # --- Métricas resumo ---
        tipo_label = "ROCHA" if tipo == "RK" else "SOLO"
        n_erros = sum(len(v) for v in problemas.values() if v != ['COLUNA AUSENTE NA PLANILHA'])
        status_ok = not problemas

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Registros HEADERS", len(df_h))
        col2.metric("Registros SAMPLE",  len(df_s))
        col3.metric("Campos c/ problema", len(problemas),
                    delta=None if not problemas else f"{len(problemas)} ⚠️")
        col4.metric("Células vazias", n_erros)
        col5.metric("Status", "✅ APROVADO" if status_ok else "❌ REPROVADO")

        st.markdown("---")

        # --- Correções de Litologia (apenas RK) ---
        if tipo == "RK" and correcoes_lit['total_alteracoes'] > 0:
            with st.expander(f"🔧 Correções LITOLOGIA_MT ({correcoes_lit['total_alteracoes']} alteração(ões))", expanded=True):
                st.info(f"O valor **'gran'** foi corrigido para **'GRAN'** em {correcoes_lit['total_alteracoes']} linha(s).")
                rows = [{"Linha (Excel)": l, "Valor original": correcoes_lit['valores_originais'][l], "Corrigido": "GRAN"}
                        for l in correcoes_lit['linhas_alteradas'][:50]]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # --- Validação de campos obrigatórios ---
        st.subheader("📋 Validação de Campos Obrigatórios")
        colunas_obrig = COLUNAS_OBRIGATORIAS_RK if tipo == "RK" else COLUNAS_OBRIGATORIAS_SO
        rows_val = []
        for col in colunas_obrig:
            if col in problemas:
                v = problemas[col]
                if v == ['COLUNA AUSENTE NA PLANILHA']:
                    rows_val.append({"Campo": col, "Status": "❌ AUSENTE", "Qtd. Vazios": "-", "Linhas": "Coluna não encontrada"})
                else:
                    ls = ", ".join(str(x) for x in v[:20])
                    if len(v) > 20:
                        ls += f" … (+{len(v)-20} mais)"
                    rows_val.append({"Campo": col, "Status": "⚠️ ERRO", "Qtd. Vazios": len(v), "Linhas": ls})
            else:
                rows_val.append({"Campo": col, "Status": "✅ OK", "Qtd. Vazios": 0, "Linhas": "Todos preenchidos"})
        st.dataframe(pd.DataFrame(rows_val), use_container_width=True, hide_index=True)

        # --- Preview dos DataFrames ---
        st.markdown("---")
        tab1, tab2 = st.tabs(["📄 HEADERS (primeiras 50 linhas)", "📄 SAMPLE (primeiras 50 linhas)"])
        with tab1:
            st.dataframe(df_h.head(50), use_container_width=True)
        with tab2:
            st.dataframe(df_s.head(50), use_container_width=True)

        # --- Download ZIP ---
        st.markdown("---")
        st.subheader("⬇️ Download dos Resultados")
        zip_buf = gerar_zip(df_h, df_s, problemas, correcoes_lit, nome_base, tipo)
        st.download_button(
            label="📦 Baixar ZIP (CSVs + Relatório TXT)",
            data=zip_buf,
            file_name=f"{nome_base}_resultados_{tipo_label}.zip",
            mime="application/zip",
        )

        # Download individual dos CSVs
        col_a, col_b = st.columns(2)
        with col_a:
            csv_h_bytes = df_h.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                "📥 CSV — HEADERS",
                data=csv_h_bytes,
                file_name=f"{nome_base}_header.csv",
                mime="text/csv",
            )
        with col_b:
            csv_s_bytes = df_s.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                "📥 CSV — SAMPLE",
                data=csv_s_bytes,
                file_name=f"{nome_base}_DEPOSITY_SAMPLE_{tipo_label}.csv",
                mime="text/csv",
            )
else:
    st.info("👆 Faça o upload de um arquivo Excel para começar.")
