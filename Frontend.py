
import streamlit as st
import requests
import html
import json
import csv
import io
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="FallacyLens | AI Argument Analyzer",
    page_icon="🔎",
    layout="wide"
)

API_URL = "https://stretch-sequence-clammy.ngrok-free.dev/predict"

# --------------------------------------------------
# EXAMPLE ARGUMENTS
# --------------------------------------------------
EXAMPLES = {
    "Ad Populum": (
        "Everyone believes this product is the best, "
        "so it must be the best product."
    ),
    "False Dilemma": (
        "Either you agree with my proposal, "
        "or you don't care about the future."
    ),
    "False Causality": (
        "I wore my lucky shirt and passed the exam, "
        "so the shirt caused me to pass."
    ),
    "Ad Hominem": (
        "You are wrong about climate change because "
        "you are an ignorant person."
    ),
    "Circular Reasoning": (
        "This rule is correct because it is the right rule to follow."
    ),
    "Faulty Generalization": (
        "Two students from this college were late, "
        "so all students from this college are irresponsible."
    ),
}

FALLACY_INFO = {
    "ad hominem": (
        "Attacking a person instead of addressing their argument.",
        "Check whether the argument criticizes someone's character "
        "rather than responding to their evidence."
    ),
    "ad populum": (
        "Treating a claim as true because many people believe it.",
        "Check whether popularity is being used instead of relevant evidence."
    ),
    "appeal to emotion": (
        "Using emotions as persuasion instead of sufficient evidence.",
        "Check whether fear, pity, anger, or excitement replaces reasoning."
    ),
    "circular reasoning": (
        "Using the conclusion itself as support for that conclusion.",
        "Check whether the argument provides an independent reason."
    ),
    "equivocation": (
        "Using a word with different meanings during an argument.",
        "Check whether an important word changes meaning between claims."
    ),
    "fallacy of credibility": (
        "Relying on credibility or authority without adequate support.",
        "Check whether the source's expertise is relevant to the claim."
    ),
    "fallacy of extension": (
        "Distorting or exaggerating another person's argument.",
        "Compare the position described with the position actually stated."
    ),
    "fallacy of logic": (
        "Reasoning that may contain a logical error or unsupported inference.",
        "Check whether the conclusion follows from the premises."
    ),
    "fallacy of relevance": (
        "Using reasons that do not adequately support the conclusion.",
        "Check whether the evidence is relevant to the claim."
    ),
    "false causality": (
        "Assuming one event caused another without sufficient evidence.",
        "Check whether causation is established rather than merely assumed."
    ),
    "false dilemma": (
        "Presenting limited choices when other possibilities may exist.",
        "Check whether reasonable alternatives have been excluded."
    ),
    "faulty generalization": (
        "Drawing a broad conclusion from limited or unrepresentative examples.",
        "Check whether the examples are sufficient and representative."
    ),
    "intentional": (
        "A dataset-specific category related to intentional fallacious reasoning.",
        "The label alone cannot establish a person's intent."
    ),
}


def get_explanation(name):
    key = name.strip().lower()
    return FALLACY_INFO.get(
        key,
        (
            "The model ranked this as a possible fallacy category.",
            "Review the argument and supporting evidence before drawing a conclusion."
        )
    )


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "argument_input" not in st.session_state:
    st.session_state.argument_input = ""

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "selected_history" not in st.session_state:
    st.session_state.selected_history = 0


# --------------------------------------------------
# STYLING
# --------------------------------------------------
st.markdown("""
<style>
.stApp {
    background: radial-gradient(
        circle at 10% 0%, #172554 0%, #0b1120 45%, #080d19 100%
    );
    color: #f1f5f9;
}
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3, p, label {
    color: #f1f5f9;
}
.hero {
    padding: 30px;
    border: 1px solid #334155;
    border-radius: 20px;
    background: linear-gradient(135deg, #1e2d60, #111827);
    margin-bottom: 26px;
}
.hero h1 {
    font-size: 2.5rem;
    font-weight: 800;
}
.hero p {
    color: #cbd5e1;
    line-height: 1.7;
}
.section-title {
    font-size: 1.4rem;
    font-weight: 750;
    margin-top: 20px;
}
div[data-testid="stTextArea"] textarea {
    background: #111827;
    color: #f8fafc;
    border: 1px solid #475569;
    border-radius: 12px;
    font-size: 1rem;
}
div.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    font-weight: 700;
}
.result-card {
    background: #111b30;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 18px;
    margin: 12px 0;
}
.top-card {
    border-color: #818cf8;
    background: linear-gradient(135deg, #242454, #111827);
}
.muted {
    color: #94a3b8;
    line-height: 1.6;
}
.footer {
    border-top: 1px solid #334155;
    margin-top: 35px;
    padding-top: 18px;
    color: #94a3b8;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <p>AI · CRITICAL THINKING · RESEARCH</p>
    <h1>🔎 FallacyLens</h1>
    <p>
        Analyze arguments, explore possible logical fallacies,
        and understand reasoning patterns with AI-assisted analysis.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# EXAMPLE ARGUMENTS
# --------------------------------------------------
st.markdown(
    '<div class="section-title">Try an example</div>',
    unsafe_allow_html=True
)

example_name = st.selectbox(
    "Choose a sample argument",
    list(EXAMPLES.keys()),
    key="example_choice"
)

if st.button("Load Example Argument", use_container_width=True):
    # Set the value before the text-area widget is created below.
    st.session_state.argument_input = EXAMPLES[example_name]
    st.rerun()


# --------------------------------------------------
# ARGUMENT INPUT
# --------------------------------------------------
st.markdown(
    '<div class="section-title">Analyze an argument</div>',
    unsafe_allow_html=True
)

argument = st.text_area(
    "Enter an argument",
    key="argument_input",
    height=140,
    placeholder="Enter a claim or argument to analyze..."
)

if st.button("🔍 Analyze Argument", use_container_width=True):
    if not argument.strip():
        st.warning("Please enter an argument first.")
    else:
        try:
            with st.spinner("Analyzing with the FallacyLens model..."):
                response = requests.post(
                    API_URL,
                    json={"argument": argument.strip()},
                    headers={"ngrok-skip-browser-warning": "true"},
                    timeout=180
                )
                response.raise_for_status()
                data = response.json()

            predictions = data.get("predictions", [])

            if not predictions:
                st.warning("The model returned no predictions.")
            else:
                record = {
                    "timestamp": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "argument": argument.strip(),
                    "predictions": predictions
                }

                # Avoid adding the same result twice if Streamlit reruns.
                st.session_state.analysis_history.insert(0, record)
                st.session_state.selected_history = 0

                st.success("Analysis completed!")

        except requests.exceptions.Timeout:
            st.error("The model took too long to respond. Please try again.")

        except requests.exceptions.RequestException as error:
            st.error(
                "Could not reach the model. Check that Colab and ngrok "
                "are still running and that the API URL is current."
            )
            st.caption(str(error))

        except (ValueError, TypeError) as error:
            st.error("The API returned an unexpected response.")
            st.caption(str(error))


# --------------------------------------------------
# HISTORY SELECTOR
# --------------------------------------------------
history = st.session_state.analysis_history

st.markdown("---")
st.markdown(
    '<div class="section-title">📚 Analysis History</div>',
    unsafe_allow_html=True
)

if not history:
    st.info(
        "Your analyses will appear here after your first successful prediction."
    )
else:
    history_labels = [
        f"{i + 1}. {item['timestamp']} — "
        f"{item['argument'][:65]}"
        for i, item in enumerate(history)
    ]

    selected_label = st.selectbox(
        "Choose an analysis to view or download",
        history_labels,
        key="history_selector"
    )

    selected_index = history_labels.index(selected_label)
    selected_record = history[selected_index]

    st.caption(f"Analyzed on: {selected_record['timestamp']}")
    st.markdown("**Argument**")
    st.write(selected_record["argument"])

    predictions = selected_record["predictions"]

    if predictions:
        top = predictions[0]
        top_name = top.get("fallacy", "Unknown")
        meaning, check = get_explanation(top_name)

        st.markdown(
            f'<div class="result-card top-card">'
            f'<b>★ Top-ranked candidate: '
            f'{html.escape(top_name.replace("_", " ").title())}</b>'
            f'<p>{html.escape(meaning)}</p>'
            f'<p><b>What to examine:</b> {html.escape(check)}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("### Ranked predictions")

        for rank, item in enumerate(predictions, start=1):
            name = item.get("fallacy", "Unknown")
            score = float(item.get("entailment_score", 0))
            meaning, check = get_explanation(name)

            with st.expander(
                f"{rank}. {name.replace('_', ' ').title()} — {score:.4f}"
            ):
                st.write("**Meaning:**", meaning)
                st.write("**What to examine:**", check)
                st.progress(max(0.0, min(1.0, score)))
                st.caption(f"Entailment score: {score:.4f}")


# --------------------------------------------------
# DOWNLOAD RESULTS
# --------------------------------------------------
if history:
    st.markdown("---")
    st.markdown(
        '<div class="section-title">⬇️ Download Results</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="muted">Export the selected analysis or your full '
        'session history.</p>',
        unsafe_allow_html=True
    )

    # Selected analysis as JSON
    selected_json = json.dumps(
        selected_record,
        indent=2,
        ensure_ascii=False
    )

    # Selected analysis as CSV
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow([
        "timestamp",
        "argument",
        "rank",
        "fallacy",
        "entailment_score",
        "contradiction_score",
        "neutral_score"
    ])

    for rank, item in enumerate(
        selected_record["predictions"], start=1
    ):
        writer.writerow([
            selected_record["timestamp"],
            selected_record["argument"],
            rank,
            item.get("fallacy", ""),
            item.get("entailment_score", ""),
            item.get("contradiction_score", ""),
            item.get("neutral_score", "")
        ])

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "Download selected analysis (JSON)",
            data=selected_json,
            file_name="fallacylens_analysis.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        st.download_button(
            "Download selected analysis (CSV)",
            data=csv_buffer.getvalue(),
            file_name="fallacylens_analysis.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Export all session analyses
    all_json = json.dumps(history, indent=2, ensure_ascii=False)

    all_csv_buffer = io.StringIO()
    all_writer = csv.writer(all_csv_buffer)
    all_writer.writerow([
        "timestamp",
        "argument",
        "rank",
        "fallacy",
        "entailment_score",
        "contradiction_score",
        "neutral_score"
    ])

    for record in history:
        for rank, item in enumerate(record["predictions"], start=1):
            all_writer.writerow([
                record["timestamp"],
                record["argument"],
                rank,
                item.get("fallacy", ""),
                item.get("entailment_score", ""),
                item.get("contradiction_score", ""),
                item.get("neutral_score", "")
            ])

    st.download_button(
        "Download all session history (JSON)",
        data=all_json,
        file_name="fallacylens_history.json",
        mime="application/json",
        use_container_width=True
    )

    st.download_button(
        "Download all session history (CSV)",
        data=all_csv_buffer.getvalue(),
        file_name="fallacylens_history.csv",
        mime="text/csv",
        use_container_width=True
    )

    if st.button("Clear Analysis History", use_container_width=True):
        st.session_state.analysis_history = []
        st.rerun()


# --------------------------------------------------
# DISCLAIMER AND FOOTER
# --------------------------------------------------
st.markdown("""
<div class="result-card">
    <b>How to interpret predictions</b>
    <p class="muted">
        Scores rank candidate fallacy hypotheses; they are not calibrated
        probabilities or proof that a fallacy is present. The explanations
        are general guidance, not independent verification of the argument.
    </p>
</div>

<div class="footer">
    <b>FallacyLens</b> · Research-based prototype<br>
    Analysis history is stored in the current Streamlit session.
    It is not permanently saved to a database.
</div>
""", unsafe_allow_html=True)
