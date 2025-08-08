import pandas as pd
import requests
import random
from scipy.stats import poisson
import numpy as np

MAPA_TIMES = {
    # 2025
    'ATM': 'Atlético Mineiro', 'BAH': 'Bahia', 'BOT': 'Botafogo', 'CEA': 'Ceará',
    'COR': 'Corinthians', 'CRU': 'Cruzeiro', 'FLA': 'Flamengo', 'FLU': 'Fluminense',
    'FOR': 'Fortaleza', 'GRE': 'Grêmio', 'INT': 'Internacional', 'JUV': 'Juventude',
    'MIR': 'Mirassol', 'PAL': 'Palmeiras', 'RBB': 'Red Bull Bragantino',
    'SAN': 'Santos', 'SPA': 'São Paulo', 'SPT': 'Sport', 'VAS': 'Vasco da Gama',
    'VIT': 'Vitória',
    # 2024
    'ATP': 'Athletico Paranaense', 'ATG': 'Atlético Goianiense', 'CRI': 'Criciúma',
    'CUI': 'Cuiabá'
}


def limpar_tabela_classificacao(df):
    df_clean = df.drop(columns=df.columns[0])
    df_clean = df_clean.rename(columns={'Equipevde': 'Time', 'Pts': 'Pontos'})
    df_clean = df_clean.head(20)
    df_clean['Time'] = df_clean['Time'].str.replace(r'\[.*?\]', '', regex=True).str.strip()
    df_clean['Pontos'] = pd.to_numeric(df_clean['Pontos'])
    return df_clean[['Time', 'Pontos']]


def limpar_tabela_jogos(df):
    
    df = df.rename(columns={df.columns[0]: 'Time da Casa'})

    df_melted = df.melt(id_vars='Time da Casa', var_name='Time de Fora_sigla', value_name='Placar')

    df_melted['Time de Fora'] = df_melted['Time de Fora_sigla'].map(MAPA_TIMES)

    df_melted = df_melted.dropna(subset=['Placar'])
    df_melted = df_melted[df_melted['Placar'].str.contains('–', na=False)]
    
    gols = df_melted['Placar'].str.extract(r'(\d+)\s*–\s*(\d+)')
    df_melted['Gols Casa'] = pd.to_numeric(gols[0])
    df_melted['Gols Fora'] = pd.to_numeric(gols[1])

    return df_melted[['Time da Casa', 'Time de Fora', 'Gols Casa', 'Gols Fora']]


def buscar_dados_ano(ano):

    print(f"Buscando dados para o ano de {ano}...")
    url = f'https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_{ano}_-_S%C3%A9rie_A'
    try:
        response = requests.get(url)
        response.raise_for_status()
        all_tables = pd.read_html(response.content, encoding='utf-8')
    except Exception as e:
        print(f"Não foi possível buscar os dados para {ano}. Erro: {e}")
        return None, None

    if ano == 2025:
        idx_classificacao = 7
        idx_jogos = 8
    elif ano == 2024:
        idx_classificacao = 5
        idx_jogos = 6
    else:
        print(f"Ano {ano} não suportado.")
        return None, None

    tabela_classificacao_bruta = all_tables[idx_classificacao]
    tabela_jogos_bruta = all_tables[idx_jogos]

    tabela_classificacao = limpar_tabela_classificacao(tabela_classificacao_bruta)
    tabela_jogos = limpar_tabela_jogos(tabela_jogos_bruta)
    tabela_jogos['ano'] = ano
    
    return tabela_classificacao, tabela_jogos

def calcular_estatisticas_ponderadas(df_jogos, pesos):
    df_jogos['peso'] = df_jogos['ano'].map(pesos)
    def weighted_mean(df, value_col, weight_col):
        return (df[value_col] * df[weight_col]).sum() / df[weight_col].sum()
    gols_feitos_casa = df_jogos.groupby('Time da Casa').apply(weighted_mean, 'Gols Casa', 'peso', include_groups=False)
    gols_sofridos_casa = df_jogos.groupby('Time da Casa').apply(weighted_mean, 'Gols Fora', 'peso', include_groups=False)
    gols_feitos_fora = df_jogos.groupby('Time de Fora').apply(weighted_mean, 'Gols Fora', 'peso', include_groups=False)
    gols_sofridos_fora = df_jogos.groupby('Time de Fora').apply(weighted_mean, 'Gols Casa', 'peso', include_groups=False)
    stats = pd.DataFrame({
        'Gols Feitos Casa': gols_feitos_casa,
        'Gols Sofridos Casa': gols_sofridos_casa,
        'Gols Feitos Fora': gols_feitos_fora,
        'Gols Sofridos Fora': gols_sofridos_fora
    }).fillna(0)
    return stats


def simular_resultado_jogo(time_casa, time_fora, stats_df):
    if time_casa not in stats_df.index or time_fora not in stats_df.index:
        return random.choice(['vitoria_casa', 'empate', 'vitoria_fora'])
    lambda_casa = (stats_df.loc[time_casa]['Gols Feitos Casa'] * stats_df.loc[time_fora]['Gols Sofridos Fora'])
    lambda_fora = (stats_df.loc[time_fora]['Gols Feitos Fora'] * stats_df.loc[time_casa]['Gols Sofridos Casa'])
    prob_vitoria_casa, prob_empate, prob_vitoria_fora = 0, 0, 0
    for i in range(11):
        for j in range(11):
            prob_placar = poisson.pmf(i, lambda_casa) * poisson.pmf(j, lambda_fora)
            if i > j: prob_vitoria_casa += prob_placar
            elif i == j: prob_empate += prob_placar
            else: prob_vitoria_fora += prob_placar
    soma_probs = prob_vitoria_casa + prob_empate + prob_vitoria_fora
    if soma_probs == 0: return 'empate'
    resultado = random.choices(
        population=['vitoria_casa', 'empate', 'vitoria_fora'],
        weights=[prob_vitoria_casa / soma_probs, prob_empate / soma_probs, prob_vitoria_fora / soma_probs],
        k=1
    )[0]
    return resultado


def simular_campeonato_final():
    classificacao_2025, jogos_2025 = buscar_dados_ano(2025)
    classificacao_2024, jogos_2024 = buscar_dados_ano(2024)
    
    if jogos_2024 is None or classificacao_2025 is None: 
        print("\nNão foi possível obter todos os dados necessários. Encerrando a simulação.")
        return

    jogos_realizados_2024 = jogos_2024.dropna(subset=['Gols Casa', 'Gols Fora'])
    jogos_realizados_2025 = jogos_2025.dropna(subset=['Gols Casa', 'Gols Fora'])
    
    todos_os_times = classificacao_2025['Time'].tolist()
    jogos_possiveis = []
    for casa in todos_os_times:
        for fora in todos_os_times:
            if casa != fora:
                jogos_possiveis.append((casa, fora))
    
    jogos_realizados_tuplas = set(tuple(x) for x in jogos_realizados_2025[['Time da Casa', 'Time de Fora']].to_numpy())
    
    jogos_faltantes_df = pd.DataFrame(
        [jogo for jogo in jogos_possiveis if jogo not in jogos_realizados_tuplas],
        columns=['Time da Casa', 'Time de Fora']
    )

    base_de_jogos_combinada = pd.concat([jogos_realizados_2024, jogos_realizados_2025], ignore_index=True)
    pesos = {2024: 0.7, 2025: 1.3} 
    stats = calcular_estatisticas_ponderadas(base_de_jogos_combinada, pesos)
    print("\nEstatísticas de força dos times calculadas com sucesso (ponderadas).\n")

    pontos_futuros = {time: 0 for time in classificacao_2025['Time']}
    
    for _, row in jogos_faltantes_df.iterrows():
        time_casa, time_fora = row['Time da Casa'], row['Time de Fora']
        resultado_sorteado = simular_resultado_jogo(time_casa, time_fora, stats)
        
        if resultado_sorteado == 'vitoria_casa':
            pontos_futuros[time_casa] += 3
        elif resultado_sorteado == 'empate':
            pontos_futuros[time_casa] += 1
            pontos_futuros[time_fora] += 1
        else:
            pontos_futuros[time_fora] += 3

    pontos_futuros_df = pd.DataFrame(list(pontos_futuros.items()), columns=['Time', 'Pontos Futuros'])
    classificacao_final = pd.merge(classificacao_2025, pontos_futuros_df, on='Time', how='left').fillna(0)
    
    classificacao_final['Pontos Finais'] = (classificacao_final['Pontos'] + classificacao_final['Pontos Futuros']).astype(int)
    classificacao_final = classificacao_final.sort_values(by=['Pontos Finais', 'Pontos'], ascending=[False, False]).reset_index(drop=True)
    classificacao_final.index = classificacao_final.index + 1

    print("\n--- TABELA FINAL SIMULADA (2025) ---")
    print("(Baseado em dados de 2024 e 2025, com pesos e sorteio de resultados)")
    print(classificacao_final[['Time', 'Pontos', 'Pontos Futuros', 'Pontos Finais']])

simular_campeonato_final()