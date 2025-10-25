# BD Agent  
![Python](https://img.shields.io/badge/Python-3.11+-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

*A portfolio project that uses AI to analyze and screen Nordic stocks using Börsdata data and OpenAI models.*

**AI-powered stock analysis and screening tool** built with **Börsdata API**, **OpenAI**, and **PydanticAI**.

BD Agent combines financial data with large language models to:
- Screen stocks by country, sector, industry, and KPI filters  
- Analyze individual companies with relevant KPI rationales  
- Generate portfolio summaries and comparisons  
- Display results in a modern **Streamlit interface**

---

## Getting Started

### 1. Clone the repository
```bash
git clone <repo-url>
cd bd_agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API keys
Create a `.env` file in the project root and add:
```
OPENAI_API_KEY=sk-...
BORSDATA_API_KEY=...
```

### 4. Run the Streamlit app
```bash
streamlit run bd_agent/ui.py
```

---

## Example prompts
```
"Analyze Atlas Copco"
"Screen Swedish banks"
"Show portfolio overview"
```

---

## Tech stack
- Python 3.11+
- OpenAI SDK
- PydanticAI
- Börsdata API
- Pandas / NumPy / Matplotlib
- Streamlit

---

## Changelog
See the full [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

---

## License
MIT © Fredrik Lindblad

---

## Contact
For questions or feedback: [fredrik-lindblad@hotmail.com]  
GitHub: [https://github.com/fredriklindblad](https://github.com/fredriklindblad)
