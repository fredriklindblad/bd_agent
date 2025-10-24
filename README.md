# BD Agent

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
Analyze Evolution
Screen Swedish banks with high ROE
Show portfolio overview for EVO, SAGA B, and BOKUS
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

## License
MIT © [Your Name or Company]

---

## Contact
For questions or feedback: [your.email@example.com]  
GitHub: [https://github.com/yourprofile](https://github.com/yourprofile)
