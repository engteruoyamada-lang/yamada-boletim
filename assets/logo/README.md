# Assets - Logo e Recursos Visuais

Esta pasta contém todos os recursos visuais para o sistema Yamada Engenharia.

## Estrutura

```
assets/
├── logo/           # Logo e variantes
├── fonts/          # Fontes customizadas
└── icons/          # Ícones meteorológicos
```

## Logo

### Como Adicionar Seu Logo

1. **Formatos aceitos**:
   - PNG (recomendado, com transparência)
   - SVG (vetorial, escalável)
   - JPEG (fallback)

2. **Dimensões recomendadas**:
   - **Logo principal**: 400x200 px (aspecto 2:1)
   - **Logo quadrado**: 200x200 px
   - **Logo branca**: Variante em branco para fundos escuros

3. **Localização**:
   ```
   assets/logo/
   ├── yamada_logo.png           # Versão padrão (fundo branco)
   ├── yamada_logo_white.png     # Versão branca (fundo verde/escuro)
   ├── yamada_logo.svg           # Vetorial (opcional)
   └── yamada_logo_icon.png      # Ícone pequeno (favicon)
   ```

4. **Uso no código**:

   **Streamlit**:
   ```python
   from PIL import Image
   logo = Image.open("assets/logo/yamada_logo.png")
   st.image(logo, width=300)
   ```

   **PDF (ReportLab)**:
   ```python
   from reportlab.platypus import Image
   logo = Image("assets/logo/yamada_logo.png", width=400, height=200)
   ```

## Identidade Visual

- **Verde escuro**: #1B4D2E (principal)
- **Verde médio**: #3DA63A (destaque)
- **Preto**: #1A1A1A (texto)
- **Branco**: #FFFFFF (fundo)

---

**Adicione seu logo aqui antes de gerar os primeiros boletins.**
