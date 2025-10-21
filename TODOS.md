ANALYZE AGENT
1. In industry average - make sure the right period is compared and not differnet periods. Also validate all steps.
2. Output report (in streamlit) that includes diagrams plus rationales for KPI choice and company info.

SCREENER AGENT
1. Interpret (1) industry, sector and/or country, (2) KPIs
2. Screen on companies based on above
3. Return a 

PORTFOLIO AGENT
1. Make functionality that takes the current portfolio and creates outlook reminders for calendar event and invites all from my list. Downloads the latest Q-report, search on the internet and summarize it. Sources included. 

GENERAL INVESTMENT ADVICE
1. MVP Done



----------------------------------------------------
LET OTHERS TEST YOUR AGENT:
Alt 1: kör din agent som en privat, nyckelskyddad HTTP-tjänst (t.ex. FastAPI på Render/Fly/Cloud Run). Dina BD- och OpenAI-nycklar stannar på servern. Dina testare får en enkel POST /ask–endpoint och en egen “tester-nyckel”. Ingen behöver installera något eller få ett UI.
struktur:
srv/
  app.py            # FastAPI, /ask + /health
  auth.py           # enkel API-nyckelkontroll + rate limit
  models.py         # Pydantic request/response
  service.py        # adapter som kallar din befintliga agent.run()
  requirements.txt
  Dockerfile

Alt 2: E-post-gateway: en enkel mail-in till din backend (t.ex. via Mailgun webhook) och svar tillbaka—också UI-löst för testaren.

----------------------------------------------------
GENERAL PYTHON
1. Use asynch and await in the app
2. Consistency of camelCase or snake_case
3. Fix all packages and make __init__s and imports clean

----------------------------------------------------
GENERAL IN THE APP
1. Streamlit for minimal UI - get plots to work
2. Build in a RAG-system