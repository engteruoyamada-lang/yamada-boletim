"""Configuração de Identidade Visual Yamada Engenharia"""

# Cores oficiais
COLORS = {
    "verde_escuro": "#1B4D2E",      # Principal
    "verde_medio": "#3DA63A",        # Destaques, CTAs
    "preto": "#1A1A1A",             # Textos, fundos
    "branco": "#FFFFFF",            # Backgrounds claros
}

# Mapeamento para Matplotlib/Plotly
MATPLOTLIB_COLORS = {
    "primary": COLORS["verde_escuro"],
    "accent": COLORS["verde_medio"],
    "text": COLORS["preto"],
    "background": COLORS["branco"],
}

# Temas Streamlit
STREAMLIT_THEME = {
    "primaryColor": COLORS["verde_escuro"],
    "backgroundColor": COLORS["branco"],
    "secondaryBackgroundColor": "#f0f0f0",
    "textColor": COLORS["preto"],
}

# Ícones e símbolos meteorológicos
ICONS = {
    "temperatura": "🌡️",
    "chuva": "🌧️",
    "umidade": "💧",
    "vento": "💨",
    "sol": "☀️",
    "nuvem": "☁️",
    "raio": "⚡",
    "geada": "❄️",
    "queimada": "🔥",
    "alerta": "⚠️",
}

# Fontes (adicionar em assets/fonts/)
FONTS = {
    "titulo": "sans-serif",
    "corpo": "sans-serif",
    "mono": "monospace",
}
