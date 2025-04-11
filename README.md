
# 📊 Buscador de Acciones del Mercado

Una aplicación web interactiva desarrollada con **Streamlit** que permite buscar información financiera detallada sobre empresas que cotizan en bolsa. Integra visualizaciones interactivas, estadísticas clave y traducción automática al español de descripciones técnicas usando la API de **Gemini AI**.

---

## 🚀 Características principales

- 🔎 **Búsqueda por símbolo bursátil** (ej. AAPL, MSFT, TSLA)
- 🌍 Traducción profesional de la descripción de la empresa al español (Gemini API)
- 📈 Visualización del precio histórico con:
  - Gráfico de velas (candlestick)
  - Comparación contra el índice S&P 500 (SPY)
  - Bandas de Bollinger y medias móviles
- 💹 Cálculo automático de:
  - Rendimientos históricos por período (1m, 3m, YTD, etc.)
  - **CAGR** (Tasa de Crecimiento Anual Compuesto)
  - **Volatilidad anualizada**

---

## 🧩 Tecnologías utilizadas

- `streamlit`
- `yfinance`
- `altair`
- `plotly`
- `pandas`
- `numpy`
- `google.generativeai` (Gemini API)

---

## ⚙️ Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu_usuario/nombre-del-repo.git
   cd nombre-del-repo
   ```

2. Crea un entorno virtual y actívalo:
   ```bash
   python -m venv env
   source env/bin/activate   # En Windows: env\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Ejecución

Lanza la aplicación con Streamlit:

```bash
streamlit run app.py
```

Una vez ejecutado, abre tu navegador en la dirección que te indique Streamlit, normalmente:

```
http://localhost:8501
```

---

## 🔐 Configuración de API Key

Este proyecto usa Gemini para traducir descripciones técnicas de empresas al español.

- Regístrate en [Google AI Studio](https://ai.google.dev)
- Genera una API Key
- Reemplaza la clave directamente en el código o usa variables de entorno.

```python
genai.configure(api_key="TU_API_KEY")
```

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.

---

## 👨‍💻 Autor

Desarrollado por [Tu Nombre] - [Tu perfil de GitHub o LinkedIn]
