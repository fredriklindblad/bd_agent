# BD Agent  
![Python](https://img.shields.io/badge/Python-3.11+-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

**AI-powered stock analysis and screening tool** built with **Börsdata API**, **OpenAI**, and **PydanticAI**.

BD Agent combines financial data with large language models to:
- Screen stocks by country, sector, industry, and KPI filters (In progress)  
- Analyze individual companies with relevant KPI rationales (MVP)
- Generate portfolio summaries and comparisons (In progress)
- Display results in a modern **Streamlit interface** (MVP)

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
```bash
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
"Analyze Atlas Copco" -> analyze_agent
"Screen Swedish banks" -> screener_agent
"Show portfolio overview" -> portfolio_agent
"Advise on how to balance between cash holdings and stock investments" -> advisor_agent
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
