# streamlit_app.py
from __future__ import annotations

import json
from typing import Any, Iterable

import streamlit as st
from dotenv import load_dotenv, find_dotenv

# Ladda .env (BD/OpenAI keys etc.)
load_dotenv(find_dotenv())

# --- Först: försök använda ren router-funktion om du har den ---
try:
    from bd_agent.router import run_agent  # recommended

    _HAS_ROUTE_AGENT = True
except Exception:
    _HAS_ROUTE_AGENT = False

# Fallback: bygg en enkel router lokalt om route_agent saknas
if not _HAS_ROUTE_AGENT:
    from bd_agent.intents import intent_classifier
    import bd_agent.agents as agents

    def _route_agent(user_prompt: str) -> Any:
        """Fallback routing if bd_agent.router.route_agent is missing."""
        intent = intent_classifier(user_prompt).intent
        if intent == "screening":
            return agents.run_screener(user_prompt)
        elif intent == "single_stock_analysis":
            return agents.run_analyzer(user_prompt)
        elif intent == "portfolio_analysis":
            return "Portfolio analysis is not implemented yet."
        elif intent == "general_investment_advice":
            return agents.run_advisor(user_prompt)
        else:
            return "Could not assess intent. Please retry."


# Intent-klassi (för visning i UI)
from bd_agent.intents import intent_classifier

st.set_page_config(page_title="BD Agent", page_icon="📈", layout="wide")

st.title("📈 BD Agent – Minimal UI")
st.caption("Skriv vad du vill ha hjälp med, så klassas intent och rätt agent körs.")

# --- Inputs ---
prompt = st.text_area(
    "Din fråga / uppgift",
    value="Analysera Evolution eller screena spelbolag i Sverige med hög ROIC.",
    height=140,
    placeholder="Ex: 'Analysera EVO', 'Screena svenska industri-bolag med hög ROIC och låg skuld'…",
)

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    run_btn = st.button("Kör", type="primary", use_container_width=True)
with col2:
    show_raw = st.toggle("Visa rå-output (JSON)")
with col3:
    keep_history = st.toggle("Spara historik", value=True)

detected_intent_slot = st.empty()
result_slot = st.container()
history_slot = st.expander("Historik", expanded=False)

if "history" not in st.session_state:
    st.session_state.history = []


# --- Render helpers ---
def _is_matplotlib_figure(obj: Any) -> bool:
    try:
        from matplotlib.figure import Figure  # type: ignore

        return isinstance(obj, Figure)
    except Exception:
        return False


def _iterable(obj: Any) -> bool:
    return isinstance(obj, (list, tuple))


def _render_one(obj: Any) -> None:
    """Rendera ett enda objekt (figur, df, pydantic, dict/list, text)."""
    # Matplotlib Figure
    if _is_matplotlib_figure(obj):
        # Viktigt: använd st.pyplot
        st.pyplot(obj)
        return

    # Pandas DataFrame
    try:
        import pandas as pd  # noqa

        if isinstance(obj, pd.DataFrame):
            st.dataframe(obj, use_container_width=True)
            return
    except Exception:
        pass

    # Pydantic BaseModel (v2)
    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        data = obj.model_dump()
        if show_raw:
            st.json(data, expanded=False)
        else:
            st.write(data)
        return

    # Dict/list
    if isinstance(obj, (dict, list)):
        if show_raw:
            st.json(obj, expanded=False)
        else:
            # list[dict] -> tabell
            if isinstance(obj, list) and obj and isinstance(obj[0], dict):
                try:
                    import pandas as pd  # noqa

                    st.dataframe(pd.DataFrame(obj), use_container_width=True)
                except Exception:
                    st.write(obj)
            else:
                st.write(obj)
        return

    # Fallback: text
    st.write(obj)


def _render_result(obj: Any) -> None:
    """Rendera resultat; stöder list/tuple av blandade typer."""
    if _iterable(obj) and obj:
        # Särskilt fall: lista av figurer → numrera
        if all(_is_matplotlib_figure(x) for x in obj):  # type: ignore[arg-type]
            for i, fig in enumerate(obj, start=1):
                st.subheader(f"Diagram {i}")
                st.pyplot(fig)
            return
        # Annars: rendera varje element
        for part in obj:
            _render_one(part)
        return
    _render_one(obj)


# --- Körning ---
if run_btn:
    if not prompt.strip():
        st.warning("Skriv något i rutan först.")
    else:
        with st.spinner("Klassificerar intent och kör agent..."):
            # 1) Intent (för visning)
            try:
                intent_res = intent_classifier(prompt).intent
                detected_intent_slot.info(f"Upptäckt intent: **{intent_res}**")
            except Exception as e:
                detected_intent_slot.error(f"Kunde inte klassificera intent: {e}")
                intent_res = None

            # 2) Kör router/agent
            try:
                result = run_agent(prompt)
            except Exception as e:
                result_slot.error(f"Något gick fel i agenten: {e}")
                result = None

            # 3) Rendera
            if result is not None:
                with result_slot:
                    _render_result(result)

                if keep_history:
                    st.session_state.history.append(
                        {
                            "prompt": prompt,
                            "intent": intent_res,
                            # För historik: undvik tunga objekt (figurer); spara bara typinfo
                            "result_type": type(result).__name__,
                            "preview": (
                                result.head(3).to_dict()  # DataFrame
                                if hasattr(result, "head")
                                else result.model_dump()  # Pydantic
                                if hasattr(result, "model_dump")
                                else result[:1]  # list/tuple: första elementet
                                if _iterable(result)
                                else str(result)[:500]  # text/dict
                            ),
                        }
                    )

# --- Historikvisning ---
if st.session_state.history:
    with history_slot:
        for i, item in enumerate(reversed(st.session_state.history), start=1):
            st.markdown(
                f"**#{i}** – intent: `{item['intent']}` – typ: `{item['result_type']}`"
            )
            if isinstance(item["preview"], (dict, list)):
                st.json(item["preview"], expanded=False)
            else:
                st.write(item["preview"])
            st.markdown("---")
