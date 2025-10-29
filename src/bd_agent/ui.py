"""Streamlit application for minimal UI"""

import sys, json
from pathlib import Path
from typing import Any, Iterable, List

# Add parent directory to sys before any bd_agent imports
project_root = Path(__file__).parent.parent
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pandas as pd
import streamlit as st
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from bd_agent.router import run_agent
from bd_agent.intents import intent_classifier
from bd_agent.eval import plot_coverage_accuracy_curve


# Page setup
st.set_page_config(page_title="BD Agent", page_icon="📈", layout="centered")
st.title("📈 BD Agent – Minimal UI")
st.caption(
    "BD Agent is a private investment bot. It can help you with instrument analysis, screening and give general investment advice."
)

# Set input area
prompt = st.text_area(
    "What can I help you with today?",
    height=50,
    placeholder="Ex: 'Analyze Evolution', 'Screen swedish banks'…",
)

# Set columns for run, show raw output and save chat history
col1, col2 = st.columns([1, 3])
with col1:
    run_btn = st.button("Run", type="primary", width="stretch")
with col2:
    keep_history = st.toggle("Save chat history", value=True)

# Set initial session states
st.session_state.setdefault("history", [])
st.session_state.setdefault("last_result", None)
st.session_state.setdefault("last_prompt", "")

# Set containers for result and history
intent_slot = st.empty()
result_slot = st.container()
history_slot = st.expander("History", expanded=False)

# update the intent when writing and exit the input window
if prompt and prompt.strip():
    try:
        intent_res = intent_classifier(prompt)
        with intent_slot:
            st.info(f"""
                    **Detected intent:** {intent_res.intent}     
                    **Confidence:** {intent_res.confidence}
                    """)
    except Exception as e:
        with intent_slot:
            st.error(f"Could not classify intent: {e}.")
else:
    intent_slot.empty()

# --- EVAL RESULTS SECTION ---
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
st.header("Evaluation Results")
st.subheader("Confusion Matrix - Intent Classification")
eval_container = st.container()

with eval_container:
    show_eval = st.button("Show Evaluation Intents Results", type="secondary")

    if show_eval:
        # load latest intent report
        report_path = (
            project_root
            / "bd_agent"
            / "eval"
            / "artifacts"
            / "intents-eval-latest"
            / "intent_report.json"
        )

        st.caption(f"Loading report from {report_path}")

        with report_path.open("r", encoding="utf-8") as f:
            report = json.load(f)

        cm = report["overall"]["confusion_matrix"]

        # convert to df and show
        df = pd.DataFrame(cm)
        st.markdown("### Confusion Matrix")
        st.dataframe(df, use_container_width=True)

        # other metrics
        metrics = {
            "Accuracy": report["overall"]["accuracy"],
            "Precision": report["overall"]["precision"],
            "Recall": report["overall"]["recall"],
            "F1 Score": report["overall"]["f1_score"],
            "Weighted F1 Score": report["overall"]["weighted_f1_score"],
        }

        st.markdown("### Overall Metrics")
        for metric, value in metrics.items():
            st.markdown(f"**{metric}:** {value:.2%}")

        if "coverage_accuracy_curve" in report["overall"]:
            st.markdown("### Coverage-Accuracy Curve")
            curve_df = pd.DataFrame(report["overall"]["coverage_accuracy_curve"])
            fig = plot_coverage_accuracy_curve(curve_df)
            st.pyplot(fig, width="content")


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


def _ensure_figsize(fig: Figure, size=(10, 6), dpi=120) -> Figure:
    """Help function to ensure figure size"""
    fig.set_size_inches(*size, forward=True)
    fig.set_dpi(dpi)
    fig.tight_layout()
    return fig


def _render_one(obj: Any) -> None:
    """Renders one based on what type it is, e.g. plot, dataframe etc."""
    if _is_matplotlib_figure(obj):
        # obj = _ensure_figsize(obj)
        st.pyplot(obj, width="content")
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
                st.pyplot(fig, width="content")
            return
    # Else render object
    _render_one(obj)


# --------- RUN AGENT ---------
just_ran = False

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
        just_ran = True

# Always render if we have earlier result
if (
    not just_ran
    and "last_result" in st.session_state
    and st.session_state.last_result is not None
):
    with result_slot:
        _render_result(st.session_state.last_result)
