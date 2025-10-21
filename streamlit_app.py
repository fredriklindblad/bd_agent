"""Streamlit application for minimal UI"""

# load dotenv to get access to openai api key
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import json
from typing import Any

import streamlit as st
from bd_agent.router import run_agent
from bd_agent.intents import intent_classifier
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


# Page setup
st.set_page_config(page_title="BD Agent", page_icon="📈", layout="centered")
st.title("📈 BD Agent – Minimal UI")
st.caption("What can I help you with today?.")

# Set input area
prompt = st.text_area(
    "User inquiry",
    height=50,
    placeholder="Ex: 'Analyze Evolution', 'Screen swedish banks'…",
)

# Set columns for run, show raw output and save chat history
col1, col2 = st.columns([1, 3])
with col1:
    run_btn = st.button("Run", type="primary", use_container_width=True)
with col2:
    keep_history = st.toggle("Save chat history", value=True)

# Set history state for the session
if "history" not in st.session_state:
    st.session_state.history = []

# Set containers for result and history
detected_intent_slot = st.empty()
result_slot = st.container()
history_slot = st.expander("History", expanded=False)

# update the intent when writing and exit the input window
try:
    intent_res = intent_classifier(prompt).intent
    st.info(f"Detected intent: **{intent_res}**")
except Exception as e:
    st.error(f"Could not classify intent: {e}.")


# --- Render helpers ---
def _is_matplotlib_figure(obj: Any) -> bool:
    """Checks if matplotlib figure and return boolean"""
    try:
        return isinstance(obj, Figure)
    except Exception:
        return False


def _iterable(obj: Any) -> bool:
    """Checks if list/tuple and return bool"""
    return isinstance(obj, (list, tuple))


def _render_one(obj: Any) -> None:
    """Renders one based on what type it is, e.g. plot, dataframe etc."""
    if _is_matplotlib_figure(obj):
        print("is a plt Figure")
        st.pyplot(obj)
        return

    # Fallback: text
    st.write(obj)


def _render_result(obj: Any) -> None:
    """Renders result by calling on _render_one if more than one item"""
    if _iterable(obj) and obj:
        # List of figures
        if all(_is_matplotlib_figure(x) for x in obj):
            for i, fig in enumerate(obj, start=1):
                st.subheader(f"Chart {i}")
                st.pyplot(fig)
                return
    # Else render object
    print("Will render one now..")
    _render_one(obj)


# --------- RUN AGENT ---------
if run_btn:
    if not prompt.strip():
        st.warning("Please write something first.")
    else:
        with st.spinner("Running agent"):
            try:
                result = run_agent(prompt)
            except Exception as e:
                result = None
                result_slot.error(f"Agent error: {e}.")

        if result is not None:
            with result_slot:
                _render_result(result)

        st.session_state.last_result = result

# Always render if we have earlier result
if "last_result" in st.session_state and st.session_state.last_result is not None:
    res = st.session_state.last_result
    print(type(res))

    # Render now
    if isinstance(res, Figure):
        with result_slot:
            st.pyplot(res)
    elif (
        isinstance(res, (list, tuple))
        and res
        and all(isinstance(x, Figure) for x in res)
    ):
        with result_slot:
            for i, fig in enumerate(res, 1):
                st.subheader(f"Chart {i}")
                st.pyplot(fig)

    else:
        with result_slot:
            _render_result(res)

# def _iterable(obj: Any) -> bool:
#     return isinstance(obj, (list, tuple))


# def _render_one(obj: Any) -> None:
#     """Rendera ett enda objekt (figur, df, pydantic, dict/list, text)."""
#     # Matplotlib Figure
#     if _is_matplotlib_figure(obj):
#         # Viktigt: använd st.pyplot
#         st.pyplot(obj)
#         return

#     # Pandas DataFrame
#     try:
#         import pandas as pd  # noqa

#         if isinstance(obj, pd.DataFrame):
#             st.dataframe(obj, use_container_width=True)
#             return
#     except Exception:
#         pass

#     # Pydantic BaseModel (v2)
#     if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
#         data = obj.model_dump()
#         if show_raw:
#             st.json(data, expanded=False)
#         else:
#             st.write(data)
#         return

#     # Dict/list
#     if isinstance(obj, (dict, list)):
#         if show_raw:
#             st.json(obj, expanded=False)
#         else:
#             # list[dict] -> tabell
#             if isinstance(obj, list) and obj and isinstance(obj[0], dict):
#                 try:
#                     import pandas as pd  # noqa

#                     st.dataframe(pd.DataFrame(obj), use_container_width=True)
#                 except Exception:
#                     st.write(obj)
#             else:
#                 st.write(obj)
#         return

#     # Fallback: text
#     st.write(obj)


# def _render_result(obj: Any) -> None:
#     """Rendera resultat; stöder list/tuple av blandade typer."""
#     if _iterable(obj) and obj:
#         # Särskilt fall: lista av figurer → numrera
#         if all(_is_matplotlib_figure(x) for x in obj):  # type: ignore[arg-type]
#             for i, fig in enumerate(obj, start=1):
#                 st.subheader(f"Diagram {i}")
#                 st.pyplot(fig)
#             return
#         # Annars: rendera varje element
#         for part in obj:
#             _render_one(part)
#         return
#     _render_one(obj)


# # --- Körning ---
# if run_btn:
#     if not prompt.strip():
#         st.warning("Skriv något i rutan först.")
#     else:
#         with st.spinner("Klassificerar intent och kör agent..."):
#             # 1) Intent (för visning)
#             try:
#                 intent_res = intent_classifier(prompt).intent
#                 detected_intent_slot.info(f"Upptäckt intent: **{intent_res}**")
#             except Exception as e:
#                 detected_intent_slot.error(f"Kunde inte klassificera intent: {e}")
#                 intent_res = None

#             # 2) Kör router/agent
#             try:
#                 result = run_agent(prompt)
#             except Exception as e:
#                 result_slot.error(f"Något gick fel i agenten: {e}")
#                 result = None

#             # 3) Rendera
#             if result is not None:
#                 with result_slot:
#                     _render_result(result)

#                 if keep_history:
#                     st.session_state.history.append(
#                         {
#                             "prompt": prompt,
#                             "intent": intent_res,
#                             # För historik: undvik tunga objekt (figurer); spara bara typinfo
#                             "result_type": type(result).__name__,
#                             "preview": (
#                                 result.head(3).to_dict()  # DataFrame
#                                 if hasattr(result, "head")
#                                 else result.model_dump()  # Pydantic
#                                 if hasattr(result, "model_dump")
#                                 else result[:1]  # list/tuple: första elementet
#                                 if _iterable(result)
#                                 else str(result)[:500]  # text/dict
#                             ),
#                         }
#                     )

# # --- Historikvisning ---
# if st.session_state.history:
#     with history_slot:
#         for i, item in enumerate(reversed(st.session_state.history), start=1):
#             st.markdown(
#                 f"**#{i}** – intent: `{item['intent']}` – typ: `{item['result_type']}`"
#             )
#             if isinstance(item["preview"], (dict, list)):
#                 st.json(item["preview"], expanded=False)
#             else:
#                 st.write(item["preview"])
#             st.markdown("---")
