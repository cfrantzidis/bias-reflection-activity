import base64
import os
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pycountry
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import STOPWORDS, WordCloud


# ============================================================
# Configuration
# ============================================================

st.set_page_config(
    page_title="Bias in Scientific Thinking",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path("responses_bias_score_v2.csv")
IMAGE_DIR = Path("images")

ALBA_COLORS = {
    "purple": "#3e3d81",
    "blue": "#27a6de",
    "green": "#a1bf37",
    "yellow": "#ffec00",
    "pink": "#ca498f",
    "white": "#ffffff",
    "light": "#f6f7fb",
    "text": "#222222",
}

COUNTRIES = ["Prefer not to say"] + sorted(
    [country.name for country in pycountry.countries]
)

CAREER_STAGES = [
    "Undergraduate / Master's",
    "PhD student",
    "Postdoc",
    "PI / Faculty / Professor or equivalent",
    "Clinician",
    "Industry / Biotech",
    "Science communication / publishing / policy",
    "Research support / administration",
    "Other",
    "Prefer not to say",
]

GENDER_OPTIONS = [
    "Prefer not to say",
    "Man",
    "Woman",
    "Non-binary",
    "Prefer to self-describe",
]

AGE_GROUPS = [
    "Under 30",
    "31–45",
    "46–60",
    "61+",
    "Prefer not to say",
]

ALBA_OPTIONS = ["Yes", "No", "Unsure"]


# Appearance preference
if "appearance_mode" not in st.session_state:
    st.session_state.appearance_mode = "Standard"

IS_DARK = st.session_state.appearance_mode == "Dark"

THEME = {
    "page_bg": "#11131a" if IS_DARK else "#f6f7fb",
    "page_bg_2": "#191c26" if IS_DARK else "#ffffff",
    "card_bg": "#202431" if IS_DARK else "#ffffff",
    "field_bg": "#2a2f3d" if IS_DARK else "#ffffff",
    "text": "#f4f5f7" if IS_DARK else "#222222",
    "muted": "#c7cad1" if IS_DARK else "#626262",
    "border": "#41475a" if IS_DARK else "#dde1ec",
    "shadow": "rgba(0, 0, 0, 0.35)" if IS_DARK else "rgba(62, 61, 129, 0.10)",
}


# ============================================================
# Styling
# ============================================================

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Asap:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

        html, body, [class*="css"] {{
            font-family: "Asap", Arial, sans-serif;
        }}

        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(39,166,222,0.13), transparent 28%),
                linear-gradient(180deg, {THEME["page_bg_2"]} 0%, {THEME["page_bg"]} 100%);
            color: {THEME["text"]} !important;
        }}

        h1, h2, h3 {{
            color: {ALBA_COLORS["blue"] if IS_DARK else ALBA_COLORS["purple"]} !important;
        }}

        .stApp p,
        .stApp li,
        .stApp label {{
            color: {THEME["text"]} !important;
            font-size: 1.08rem !important;
            line-height: 1.58 !important;
        }}

        /* Main page headings */
        h1 {{
            font-size: 2.35rem !important;
            line-height: 1.18 !important;
            font-weight: 700 !important;
        }}

        h2 {{
            font-size: 1.85rem !important;
            line-height: 1.25 !important;
            font-weight: 700 !important;
        }}

        h3 {{
            font-size: 1.42rem !important;
            line-height: 1.3 !important;
            font-weight: 700 !important;
        }}

        .alba-card {{
            background: {THEME["card_bg"]} !important;
            color: {THEME["text"]} !important;
            padding: 1.3rem 1.4rem;
            border-radius: 18px;
            border-left: 7px solid {ALBA_COLORS["blue"]};
            border-top: 1px solid {THEME["border"]};
            border-right: 1px solid {THEME["border"]};
            border-bottom: 1px solid {THEME["border"]};
            box-shadow: 0 8px 24px {THEME["shadow"]};
            margin-bottom: 1rem;
        }}

        .alba-card,
        .alba-card p,
        .alba-card strong,
        .alba-card span,
        .alba-card div {{
            color: {THEME["text"]} !important;
            font-size: 1.20rem !important;
            line-height: 1.64 !important;
        }}

        .education-card {{
            background: {THEME["card_bg"]} !important;
            color: {THEME["text"]} !important;
            padding: 1.25rem 1.4rem;
            border-radius: 18px;
            border: 2px solid {ALBA_COLORS["green"]};
            box-shadow: 0 8px 24px {THEME["shadow"]};
            margin-top: 1rem;
        }}

        .education-card,
        .education-card p,
        .education-card strong,
        .education-card span,
        .education-card div {{
            color: {THEME["text"]} !important;
            font-size: 1.10rem !important;
            line-height: 1.60 !important;
        }}

        .education-card h3 {{
            color: {ALBA_COLORS["blue"] if IS_DARK else ALBA_COLORS["purple"]} !important;
        }}

        .small-muted {{
            color: {THEME["muted"]} !important;
            font-size: 0.92rem;
        }}

        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] label p,
        div[data-testid="stTextArea"] label,
        div[data-testid="stTextArea"] label p,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stSelectbox"] label p {{
            color: {THEME["text"]} !important;
            font-size: 1.07rem !important;
            line-height: 1.48 !important;
        }}

        div[data-testid="stTextArea"] label p,
        div[data-testid="stSelectbox"] label p {{
            font-weight: 650 !important;
        }}

        textarea,
        input {{
            background-color: {THEME["field_bg"]} !important;
            color: {THEME["text"]} !important;
            -webkit-text-fill-color: {THEME["text"]} !important;
        }}

        div[data-baseweb="select"] > div {{
            background-color: {THEME["field_bg"]} !important;
            color: {THEME["text"]} !important;
            border-color: {THEME["border"]} !important;
        }}

        div[data-baseweb="select"] span {{
            color: {THEME["text"]} !important;
        }}

        div[data-testid="stExpander"] details,
        div[data-testid="stExpander"] summary {{
            background-color: {THEME["card_bg"]} !important;
            color: {THEME["text"]} !important;
            border-color: {THEME["border"]} !important;
        }}

        div[data-testid="stCaptionContainer"],
        div[data-testid="stCaptionContainer"] p {{
            color: {THEME["muted"]} !important;
        }}

        .stButton > button {{
            border-radius: 12px !important;
            border: 2px solid {"#ffffff" if IS_DARK else ALBA_COLORS["purple"]} !important;
            background: {ALBA_COLORS["blue"] if IS_DARK else ALBA_COLORS["purple"]} !important;
            color: #ffffff !important;
            font-weight: 750 !important;
            font-size: 1.05rem !important;
            line-height: 1.25 !important;
            min-height: 3.15rem !important;
            padding: 0.62rem 1.05rem !important;
            box-shadow: 0 6px 16px rgba(39, 166, 222, 0.30) !important;
        }}

        .stButton > button p,
        .stButton > button span,
        .stButton > button div {{
            color: #ffffff !important;
            font-weight: 750 !important;
            font-size: 1.05rem !important;
        }}

        .stButton > button:hover {{
            background: {ALBA_COLORS["pink"] if IS_DARK else ALBA_COLORS["blue"]} !important;
            border-color: #ffffff !important;
            color: #ffffff !important;
            box-shadow: 0 8px 20px rgba(202, 73, 143, 0.34) !important;
            transform: translateY(-1px);
        }}

        .stButton > button:focus {{
            outline: 3px solid {ALBA_COLORS["yellow"]} !important;
            outline-offset: 2px !important;
        }}

        div[data-testid="stMetric"] {{
            background: {THEME["card_bg"]};
            color: {THEME["text"]};
            border-radius: 16px;
            padding: 0.9rem;
            border: 1px solid {THEME["border"]};
            border-top: 5px solid {ALBA_COLORS["pink"]};
            box-shadow: 0 7px 20px {THEME["shadow"]};
        }}

        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] div {{
            color: {THEME["text"]} !important;
        }}

        div[data-testid="stDataFrame"] {{
            border: 1px solid {THEME["border"]};
            border-radius: 12px;
            overflow: hidden;
        }}

        hr {{
            border-color: {THEME["border"]} !important;
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.90rem !important;
            }}

            h2 {{
                font-size: 1.55rem !important;
            }}

            h3 {{
                font-size: 1.30rem !important;
            }}

            .stApp p,
            .stApp li,
            .stApp label {{
                font-size: 1.00rem !important;
                line-height: 1.52 !important;
            }}

            .alba-card,
            .alba-card p,
            .alba-card div {{
                font-size: 1.08rem !important;
                line-height: 1.58 !important;
            }}

            .education-card,
            .education-card p,
            .education-card div {{
                font-size: 1.02rem !important;
                line-height: 1.55 !important;
            }}

            .stButton > button,
            .stButton > button p,
            .stButton > button span {{
                font-size: 0.98rem !important;
            }}
        }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Updated scenarios and transparent mapping
# ============================================================

SCENARIOS = [
    {
        "id": "scenario_1",
        "neutral_title": "Scenario 1",
        "bias_family": "Gender bias",
        "image": IMAGE_DIR / "scenario_1.png",
        "question": (
            'During a team debrief after a round of interviews for a clinical research '
            'coordinator role, a colleague says: "I think we need someone who can really '
            'hold the team together — someone people feel comfortable opening up to."\n\n'
            "How might this comment shape the next round of evaluations?"
        ),
        "options": {
            "A": {
                "text": "It probably reflects what the role genuinely requires.",
                "score": 2,
                "rationale": (
                    "Takes the gendered framing at face value, with no awareness that "
                    "it may be coded language."
                ),
            },
            "B": {
                "text": (
                    "It could subtly steer the team toward certain candidates without "
                    "anyone realising."
                ),
                "score": 0,
                "rationale": (
                    "Recognises the mechanism: implicit assumptions may influence judgement."
                ),
            },
            "C": {
                "text": "It is too vague to have any real influence on decisions.",
                "score": 1,
                "rationale": (
                    "Acknowledges ambiguity but dismisses the risk rather than examining it."
                ),
            },
        },
        "explanation": (
            'The comment about someone "people feel comfortable opening up to" sounds neutral, '
            "but it subtly invokes traits more commonly associated with women—warmth, emotional "
            "availability and nurturance. Without anyone explicitly saying so, this language can "
            "steer evaluators toward candidates who fit a gendered image of care, while equally "
            "qualified candidates who do not match that image may be passed over. The bias is "
            "not necessarily in the words themselves, but in the assumptions they may activate."
        ),
    },
    {
        "id": "scenario_2",
        "neutral_title": "Scenario 2",
        "bias_family": "Confirmation bias",
        "image": IMAGE_DIR / "scenario_2.png",
        "question": (
            "Your lab has spent two years building a case for the role of microglia in "
            "Alzheimer's progression. A new preprint challenges a core assumption in your "
            "model. Around the same time, a second preprint from a less prominent group "
            "appears to support it.\n\nWhat do you do next?"
        ),
        "options": {
            "A": {
                "text": (
                    "You read both but find yourself spending more time on the one that "
                    "fits your framework."
                ),
                "score": 1,
                "rationale": "The bias is operating passively or unconsciously.",
            },
            "B": {
                "text": (
                    "You flag both preprints at the next lab meeting and discuss them equally."
                ),
                "score": 0,
                "rationale": (
                    "Uses an active countermeasure and applies structural fairness to the evidence."
                ),
            },
            "C": {
                "text": (
                    "You set aside the contradicting preprint until after your upcoming "
                    "grant submission."
                ),
                "score": 2,
                "rationale": (
                    "Deliberately avoids contradictory evidence for strategic convenience."
                ),
            },
        },
        "explanation": (
            "We tend to engage more critically with evidence that challenges us and more "
            "generously with evidence that confirms what we already believe. In research, "
            "this can appear as spending less time on contradictory evidence, reading it "
            'more sceptically, or filing it away for "later".'
        ),
    },
    {
        "id": "scenario_3",
        "neutral_title": "Scenario 3",
        "bias_family": "Attribution bias",
        "image": IMAGE_DIR / "scenario_3.png",
        "question": (
            'Dr. P has always spoken highly of his postdoc, Dr. E, describing her as someone '
            'who "just sees things differently." Her new optogenetics protocol produces results '
            "that turn heads at the next conference.\n\n"
            "When Dr. P tells the story later, how does he frame it?"
        ),
        "options": {
            "A": {
                "text": (
                    "He talks about the months of troubleshooting, failed iterations and "
                    "cross-team input that got them there."
                ),
                "score": 0,
                "rationale": (
                    "Actively corrects the bias by attributing success to visible work, "
                    "collaboration and context."
                ),
            },
            "B": {
                "text": (
                    "He says it came together because Dr. E has a kind of intuition "
                    "that is hard to teach."
                ),
                "score": 2,
                "rationale": (
                    "Classic attribution bias: success is explained mainly through an innate trait."
                ),
            },
            "C": {
                "text": (
                    "He lets Dr. E present the work and steps back from the narrative entirely."
                ),
                "score": 1,
                "rationale": (
                    "Avoids imposing a biased narrative, but does so passively rather than "
                    "actively reframing the explanation."
                ),
            },
        },
        "explanation": (
            "When we already hold a positive image of someone, we may explain their success "
            "mainly in terms of who they are—their talent, instinct or character. This can "
            "flatten the fuller story of collaboration, failed attempts and structural support. "
            "The reverse can also occur when other people's success is attributed to luck "
            "or circumstance."
        ),
    },
    {
        "id": "scenario_4",
        "neutral_title": "Scenario 4",
        "bias_family": "Stereotype threat",
        "image": IMAGE_DIR / "scenario_4.png",
        "question": (
            "K., a PhD student, is presenting his neurogenesis research at a large international "
            "conference. Before going on stage, a senior researcher from another institution "
            "makes a passing remark about how students from smaller programmes sometimes "
            "struggle to hold the room.\n\nHow might that moment affect K.?"
        ),
        "options": {
            "A": {
                "text": "It sharpens his focus—he is determined to prove it wrong.",
                "score": 1,
                "rationale": (
                    "Acknowledges an effect, but frames it as fully overcome by willpower "
                    "rather than recognising a genuine cognitive cost."
                ),
            },
            "B": {
                "text": (
                    "It stays with him, and he finds it harder to settle into his delivery."
                ),
                "score": 0,
                "rationale": (
                    "Matches the documented mechanism: stereotype threat can consume "
                    "cognitive bandwidth and disrupt performance."
                ),
            },
            "C": {
                "text": "He brushes it off and presents exactly as he prepared.",
                "score": 2,
                "rationale": (
                    "Understates the potential impact of stereotype threat by assuming "
                    "the remark has no real effect."
                ),
            },
        },
        "explanation": (
            "Stereotype threat occurs when awareness of a negative stereotype about a group "
            "becomes a source of pressure. The person does not need to believe the stereotype. "
            "Concern about being seen as confirming it can consume cognitive resources and "
            "disrupt performance. Even a passing remark can act as a trigger."
        ),
    },
    {
        "id": "scenario_5",
        "neutral_title": "Scenario 5",
        "bias_family": "Prestige bias",
        "image": IMAGE_DIR / "scenario_5.png",
        "question": (
            "Two researchers apply for a neuroimaging specialist position. Their publication "
            "records are comparable. Dr. X completed a postdoc at a well-funded US research "
            "university. Dr. Y has spent the past four years at a regional hospital in southern "
            "Italy leading a smaller, independent imaging unit.\n\n"
            "What goes through your mind as you review their files?"
        ),
        "options": {
            "A": {
                "text": (
                    "You find yourself reading Dr. X's application with more anticipation."
                ),
                "score": 2,
                "rationale": "Institutional prestige is directly shaping enthusiasm.",
            },
            "B": {
                "text": (
                    "You are curious about the constraints Dr. Y worked under and what "
                    "that required of them."
                ),
                "score": 0,
                "rationale": (
                    "Actively reframes context as something to investigate rather than penalise."
                ),
            },
            "C": {
                "text": (
                    "You treat both files the same—institutional context does not factor in."
                ),
                "score": 1,
                "rationale": (
                    "Claims neutrality without examining how prestige may already shape judgement."
                ),
            },
        },
        "explanation": (
            "Prestige bias uses institutional reputation as a shortcut for individual quality. "
            "It can conflate the visibility and resources of an institution with the ability "
            "of the person. Researchers working in smaller or under-resourced settings may "
            "have developed substantial skill and independence that a conventional CV "
            "comparison misses."
        ),
    },
    {
        "id": "scenario_6",
        "neutral_title": "Scenario 6",
        "bias_family": "Affinity bias",
        "image": IMAGE_DIR / "scenario_6.png",
        "question": (
            "You are on a selection panel for a PhD position. One applicant, Élodie Laurent, "
            "has written a proposal on neuroethics that cites your recent paper—not superficially, "
            "but in a way that shows she is genuinely engaged with your argument.\n\n"
            "How does this land as you read her file?"
        ),
        "options": {
            "A": {
                "text": (
                    "You notice you are more invested in her application than the others."
                ),
                "score": 2,
                "rationale": "The affinity bias is operating directly and remains unexamined.",
            },
            "B": {
                "text": "You treat it as one data point among many and move on.",
                "score": 0,
                "rationale": (
                    "Recognises the pull and deliberately normalises its weight within "
                    "the wider evaluation."
                ),
            },
            "C": {
                "text": (
                    "You flag it to the panel as a potential conflict and recuse yourself "
                    "from her evaluation."
                ),
                "score": 1,
                "rationale": (
                    "Shows awareness but overcorrects by treating ordinary scholarly "
                    "engagement as disqualifying."
                ),
            },
        },
        "explanation": (
            "When someone reflects our interests, references our work or shares our intellectual "
            "passions, we may naturally feel more engaged with them. This is affinity bias. "
            "It is difficult to detect because the added warmth often feels like recognition "
            "rather than preferential judgement."
        ),
    },
]

# ============================================================
# Session state
# ============================================================

DEFAULT_STATE = {
    "view": "activity",
    "stage": "landing",
    "scenario_index": 0,
    "answer_confirmed": False,
    "responses": {},
    "demographics": {},
    "submission_saved": False,
    "participant_id": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# Utilities
# ============================================================

def safe_rerun():
    st.rerun()


def reset_participant():
    for key, value in DEFAULT_STATE.items():
        st.session_state[key] = value
    safe_rerun()


def image_if_available(
    path: Path,
    caption: str | None = None,
    max_width: int = 720,
):
    """
    Display an image responsively.

    On mobile screens, the image uses the available width. On larger screens,
    its displayed width is capped by max_width so that square images do not
    dominate the page.
    """
    if not path.exists():
        return

    image_bytes = path.read_bytes()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    caption_html = ""
    if caption:
        caption_html = f"""
        <div style="
            margin-top: 0.45rem;
            color: #666666;
            font-size: 0.88rem;
            text-align: center;
        ">
            {caption}
        </div>
        """

    st.markdown(
        f"""
        <div style="
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0.5rem auto 1.25rem auto;
        ">
            <img
                src="data:image/png;base64,{encoded_image}"
                style="
                    width: 100%;
                    max-width: {max_width}px;
                    height: auto;
                    display: block;
                    border-radius: 14px;
                    object-fit: contain;
                    box-shadow: 0 5px 18px rgba(62, 61, 129, 0.10);
                "
                alt="{caption or 'Scenario illustration'}"
            >
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def interpret_score(total_score: int):
    """Return the non-diagnostic bias-score band and interpretation."""
    if total_score <= 4:
        return (
            "Lower bias score",
            "Across these scenarios, your responses more often recognised or "
            "countered the bias mechanisms. This does not imply that a person is "
            "bias-free; it reflects only the choices made in this activity.",
        )
    if total_score <= 8:
        return (
            "Moderate bias score",
            "Your responses show a mixed pattern. Some biases were recognised, while "
            "others may have been minimised, left unexamined, or addressed through "
            "an incomplete or disproportionate response.",
        )
    return (
        "Higher bias score",
        "Across these scenarios, bias-related patterns were more often accepted, "
        "minimised or left unexamined. This result is a prompt for reflection, not "
        "a diagnosis or fixed description of an individual.",
    )


def save_submission():
    if st.session_state.submission_saved:
        return

    participant_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat(timespec="seconds")
    st.session_state.participant_id = participant_id

    selected_scores = []
    for scenario in SCENARIOS:
        response = st.session_state.responses[scenario["id"]]
        option = scenario["options"][response["selected_option"]]
        selected_scores.append(option["score"])

    total_score = sum(selected_scores)
    score_level, score_interpretation = interpret_score(total_score)

    rows = []
    demographics = st.session_state.demographics

    for scenario in SCENARIOS:
        response = st.session_state.responses[scenario["id"]]
        option = scenario["options"][response["selected_option"]]

        rows.append(
            {
                "participant_id": participant_id,
                "timestamp": timestamp,
                "career_stage": demographics["career_stage"],
                "country": demographics["country"],
                "gender": demographics["gender"],
                "gender_self_describe": demographics.get("gender_self_describe", ""),
                "age_group": demographics["age_group"],
                "alba_member": demographics["alba_member"],
                "scenario_id": scenario["id"],
                "scenario_number": scenario["neutral_title"],
                "bias_family": scenario["bias_family"],
                "selected_option": response["selected_option"],
                "selected_text": option["text"],
                "option_score": option["score"],
                "score_rationale": option["rationale"],
                "total_score": total_score,
                "score_level": score_level,
                "score_interpretation": score_interpretation,
                "free_text_response": response.get("free_text_response", ""),
            }
        )

    new_df = pd.DataFrame(rows)

    if DATA_FILE.exists():
        existing_df = pd.read_csv(DATA_FILE)
        output_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        output_df = new_df

    output_df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    st.session_state.submission_saved = True


def load_data():
    if not DATA_FILE.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(DATA_FILE)
    except Exception:
        return pd.DataFrame()


def participant_summary_dataframe():
    rows = []
    for scenario in SCENARIOS:
        response = st.session_state.responses[scenario["id"]]
        option = scenario["options"][response["selected_option"]]
        rows.append(
            {
                "Scenario": scenario["neutral_title"],
                "Bias theme": scenario["bias_family"],
                "Selected option": response["selected_option"],
                "Points": option["score"],
                "Why it received this score": option["rationale"],
            }
        )
    return pd.DataFrame(rows)


def render_how_it_works():
    with st.expander("How the bias score works", expanded=False):
        st.markdown(
            """
            Each answer is assigned a **bias score**:

            - **0 points:** the response actively recognises and proportionately counters the bias;
            - **1 point:** partial awareness, an incomplete response, or an overcorrection;
            - **2 points:** the bias is operating, accepted, minimised or largely unrecognised.

            The six scores are added together, giving a total from **0 to 12**.
            A larger score indicates that more bias-related responses appeared in
            this set of scenarios:

            - **0–4: Lower bias score**
            - **5–8: Moderate bias score**
            - **9–12: Higher bias score**

            This is a transparent educational scoring rule, not a validated
            psychometric scale or diagnostic instrument.
            """
        )


def get_organiser_password():
    try:
        return st.secrets.get("analytics_password", "")
    except Exception:
        return os.getenv("ALBA_ANALYTICS_PASSWORD", "")



def classify_sentiment(compound_score: float):
    if compound_score >= 0.05:
        return "Positive"
    if compound_score <= -0.05:
        return "Negative"
    return "Neutral"


def prepare_text_analytics(dataframe: pd.DataFrame):
    """Analyse non-empty English free-text responses using VADER."""
    if "free_text_response" not in dataframe.columns:
        return pd.DataFrame()

    text_df = dataframe[
        dataframe["free_text_response"].fillna("").str.strip() != ""
    ].copy()

    if text_df.empty:
        return text_df

    analyser = SentimentIntensityAnalyzer()
    sentiment_values = text_df["free_text_response"].astype(str).apply(
        analyser.polarity_scores
    )

    text_df["sentiment_compound"] = sentiment_values.apply(
        lambda item: item["compound"]
    )
    text_df["sentiment_positive"] = sentiment_values.apply(
        lambda item: item["pos"]
    )
    text_df["sentiment_neutral"] = sentiment_values.apply(
        lambda item: item["neu"]
    )
    text_df["sentiment_negative"] = sentiment_values.apply(
        lambda item: item["neg"]
    )
    text_df["sentiment_label"] = text_df["sentiment_compound"].apply(
        classify_sentiment
    )
    return text_df


def make_word_cloud(text_series):
    combined_text = " ".join(text_series.dropna().astype(str)).strip()
    if not combined_text:
        return None

    custom_stopwords = set(STOPWORDS).union(
        {
            "scenario",
            "answer",
            "option",
            "think",
            "thought",
            "would",
            "could",
            "because",
            "selected",
            "response",
        }
    )

    cloud = WordCloud(
        width=1400,
        height=700,
        background_color=THEME["card_bg"],
        color_func=lambda *args, **kwargs: (
            ALBA_COLORS["blue"] if IS_DARK else ALBA_COLORS["purple"]
        ),
        stopwords=custom_stopwords,
        collocations=False,
        max_words=120,
        min_font_size=10,
    ).generate(combined_text)

    return cloud.to_array()


# ============================================================
# Navigation
# ============================================================

nav1, nav2, nav3, nav4 = st.columns([1.25, 1.05, 1.2, 2.5])

with nav1:
    if st.button("🧠 Participant view", use_container_width=True):
        st.session_state.view = "activity"
        safe_rerun()

with nav2:
    if st.button("📊 Analytics", use_container_width=True):
        st.session_state.view = "analytics"
        safe_rerun()

with nav3:
    selected_appearance = st.selectbox(
        "Appearance",
        ["Standard", "Dark"],
        index=0 if st.session_state.appearance_mode == "Standard" else 1,
        label_visibility="collapsed",
        key="appearance_selector",
    )
    if selected_appearance != st.session_state.appearance_mode:
        st.session_state.appearance_mode = selected_appearance
        safe_rerun()

with nav4:
    st.markdown(
        '<div class="small-muted" style="text-align:right;padding-top:0.7rem;">'
        "ALBA Network • Bias Reflection Activity</div>",
        unsafe_allow_html=True,
    )

st.divider()


# ============================================================
# Analytics dashboard
# ============================================================

def render_analytics():
    st.title("Advanced analytics dashboard")

    df = load_data()
    if df.empty:
        st.info("No historical responses have been collected yet.")
        return

    required_score_columns = {"option_score", "total_score", "score_level"}
    if not required_score_columns.issubset(df.columns):
        st.warning(
            "The available historical file uses an older scoring structure. "
            "New responses will be stored separately using the inverse bias score."
        )
        return

    dimension_map = {
        "All respondents": None,
        "Career stage / role": "career_stage",
        "Age group": "age_group",
        "Country": "country",
        "Gender": "gender",
        "ALBA membership": "alba_member",
    }

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_dimension_label = st.selectbox(
            "Filter dashboard by",
            list(dimension_map.keys()),
            key="analytics_dimension",
        )

    selected_dimension = dimension_map[selected_dimension_label]
    filtered_df = df.copy()

    with filter_col2:
        if selected_dimension:
            values = sorted(
                filtered_df[selected_dimension]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )
            selected_value = st.selectbox(
                f"Select {selected_dimension_label.lower()}",
                ["All"] + values,
                key="analytics_dimension_value",
            )
            if selected_value != "All":
                filtered_df = filtered_df[
                    filtered_df[selected_dimension].astype(str) == selected_value
                ]
        else:
            st.selectbox(
                "Population",
                ["All historical respondents"],
                disabled=True,
                key="analytics_all_population",
            )

    if filtered_df.empty:
        st.warning("No responses match the selected filter.")
        return

    participant_scores = (
        filtered_df[
            ["participant_id", "total_score", "score_level"]
        ]
        .drop_duplicates(subset=["participant_id"])
    )

    total_participants = participant_scores["participant_id"].nunique()
    mean_score = participant_scores["total_score"].mean()
    median_score = participant_scores["total_score"].median()
    text_count = (
        filtered_df["free_text_response"]
        .fillna("")
        .str.strip()
        .astype(bool)
        .sum()
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Participants", total_participants)
    m2.metric("Mean bias score", f"{mean_score:.1f} / 12")
    m3.metric("Median bias score", f"{median_score:.1f} / 12")
    m4.metric("Written reflections", int(text_count))

    overview_tab, scenario_tab, demographic_tab, text_tab = st.tabs(
        [
            "Overview",
            "Scenario analysis",
            "Demographic comparisons",
            "Text insights",
        ]
    )

    with overview_tab:
        left, right = st.columns(2)

        with left:
            st.markdown("#### Distribution of total bias scores")
            fig_hist = px.histogram(
                participant_scores,
                x="total_score",
                nbins=13,
                range_x=[0, 12],
                labels={"total_score": "Total bias score"},
                color_discrete_sequence=[ALBA_COLORS["purple"]],
            )
            fig_hist.update_layout(
                bargap=0.08,
                margin=dict(l=10, r=10, t=25, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color=THEME["text"],
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with right:
            st.markdown("#### Bias-score bands")
            level_order = [
                "Lower bias score",
                "Moderate bias score",
                "Higher bias score",
            ]
            level_counts = (
                participant_scores["score_level"]
                .value_counts()
                .reindex(level_order, fill_value=0)
                .rename_axis("Score level")
                .reset_index(name="Participants")
            )
            fig_donut = px.pie(
                level_counts,
                values="Participants",
                names="Score level",
                hole=0.58,
                color="Score level",
                color_discrete_map={
                    "Lower bias score": ALBA_COLORS["green"],
                    "Moderate bias score": ALBA_COLORS["yellow"],
                    "Higher bias score": ALBA_COLORS["pink"],
                },
            )
            fig_donut.update_layout(
                margin=dict(l=10, r=10, t=25, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=THEME["text"],
                legend_title_text="",
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown("#### Participant score timeline")
        timeline = (
            filtered_df[
                ["participant_id", "timestamp", "total_score"]
            ]
            .drop_duplicates(subset=["participant_id"])
            .sort_values("timestamp")
        )
        timeline["Participant sequence"] = range(1, len(timeline) + 1)

        fig_timeline = px.scatter(
            timeline,
            x="Participant sequence",
            y="total_score",
            size_max=12,
            trendline="lowess" if len(timeline) >= 8 else None,
            labels={"total_score": "Total bias score"},
            color_discrete_sequence=[ALBA_COLORS["blue"]],
        )
        fig_timeline.update_yaxes(range=[-0.3, 12.3])
        fig_timeline.update_layout(
            margin=dict(l=10, r=10, t=25, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=THEME["text"],
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

    with scenario_tab:
        scenario_means = (
            filtered_df.groupby(["scenario_number", "bias_family"])["option_score"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "Mean bias score", "count": "Responses"})
        )

        st.markdown("#### Mean bias score by scenario")
        fig_scenario = px.bar(
            scenario_means,
            x="scenario_number",
            y="Mean bias score",
            color="bias_family",
            text=scenario_means["Mean bias score"].round(2),
            range_y=[0, 2],
            labels={
                "scenario_number": "Scenario",
                "bias_family": "Bias theme",
            },
            color_discrete_sequence=[
                ALBA_COLORS["purple"],
                ALBA_COLORS["blue"],
                ALBA_COLORS["green"],
                ALBA_COLORS["pink"],
                ALBA_COLORS["yellow"],
            ],
        )
        fig_scenario.update_traces(textposition="outside")
        fig_scenario.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=25, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=THEME["text"],
        )
        st.plotly_chart(fig_scenario, use_container_width=True)

        option_distribution = (
            filtered_df.groupby(
                ["scenario_number", "selected_option"]
            )
            .size()
            .reset_index(name="Count")
        )
        totals = option_distribution.groupby("scenario_number")["Count"].transform("sum")
        option_distribution["Percent"] = 100 * option_distribution["Count"] / totals

        st.markdown("#### Option selection by scenario")
        fig_stack = px.bar(
            option_distribution,
            x="scenario_number",
            y="Percent",
            color="selected_option",
            barmode="stack",
            text=option_distribution["Percent"].round(1),
            labels={
                "scenario_number": "Scenario",
                "selected_option": "Option",
            },
            color_discrete_sequence=[
                ALBA_COLORS["purple"],
                ALBA_COLORS["blue"],
                ALBA_COLORS["pink"],
            ],
        )
        fig_stack.update_layout(
            yaxis_title="Percentage of responses",
            legend_title_text="Option",
            margin=dict(l=10, r=10, t=25, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=THEME["text"],
        )
        st.plotly_chart(fig_stack, use_container_width=True)

        radar_values = scenario_means["Mean bias score"].tolist()
        radar_labels = scenario_means["scenario_number"].tolist()
        if radar_values:
            radar_values_closed = radar_values + [radar_values[0]]
            radar_labels_closed = radar_labels + [radar_labels[0]]
            fig_radar = go.Figure()
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=radar_values_closed,
                    theta=radar_labels_closed,
                    fill="toself",
                    name="Mean bias score",
                    line=dict(color=ALBA_COLORS["blue"]),
                    fillcolor="rgba(39,166,222,0.25)",
                )
            )
            fig_radar.update_layout(
                title="Bias profile across scenarios",
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 2],
                        color=THEME["text"],
                    ),
                    bgcolor="rgba(0,0,0,0)",
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=THEME["text"],
                showlegend=False,
                margin=dict(l=40, r=40, t=60, b=40),
            )
            st.plotly_chart(fig_radar, use_container_width=True)

    with demographic_tab:
        demographic_dimension = st.selectbox(
            "Break down total scores by",
            [
                "career_stage",
                "age_group",
                "country",
                "gender",
                "alba_member",
            ],
            format_func=lambda value: {
                "career_stage": "Career stage / role",
                "age_group": "Age group",
                "country": "Country",
                "gender": "Gender",
                "alba_member": "ALBA membership",
            }[value],
            key="demographic_chart_dimension",
        )

        demographic_scores = (
            filtered_df[
                ["participant_id", demographic_dimension, "total_score"]
            ]
            .drop_duplicates(subset=["participant_id"])
            .dropna()
        )

        counts_by_group = demographic_scores[demographic_dimension].value_counts()
        allowed_groups = counts_by_group[counts_by_group >= 5].index
        display_scores = demographic_scores[
            demographic_scores[demographic_dimension].isin(allowed_groups)
        ]

        if display_scores.empty:
            st.info(
                "No demographic subgroup currently has at least five participants. "
                "The threshold protects privacy and avoids unstable comparisons."
            )
        else:
            fig_box = px.box(
                display_scores,
                x=demographic_dimension,
                y="total_score",
                points="all",
                labels={
                    demographic_dimension: "",
                    "total_score": "Total bias score",
                },
                color=demographic_dimension,
                color_discrete_sequence=[
                    ALBA_COLORS["purple"],
                    ALBA_COLORS["blue"],
                    ALBA_COLORS["green"],
                    ALBA_COLORS["pink"],
                    ALBA_COLORS["yellow"],
                ],
            )
            fig_box.update_yaxes(range=[-0.3, 12.3])
            fig_box.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=25, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color=THEME["text"],
            )
            st.plotly_chart(fig_box, use_container_width=True)

            group_summary = (
                display_scores.groupby(demographic_dimension)["total_score"]
                .agg(["count", "mean", "median", "std"])
                .reset_index()
                .rename(
                    columns={
                        "count": "Participants",
                        "mean": "Mean score",
                        "median": "Median score",
                        "std": "Standard deviation",
                    }
                )
            )
            group_summary["Mean score"] = group_summary["Mean score"].round(2)
            group_summary["Median score"] = group_summary["Median score"].round(2)
            group_summary["Standard deviation"] = (
                group_summary["Standard deviation"].round(2)
            )
            st.dataframe(group_summary, use_container_width=True, hide_index=True)

    with text_tab:
        st.markdown("#### English free-text reflections")
        text_df = prepare_text_analytics(filtered_df)

        if text_df.empty:
            st.info("No written reflections are currently available for text analysis.")
        else:
            st.caption(
                "Sentiment is estimated using VADER, which is designed for English text. "
                "It describes the emotional polarity of the wording, not the participant's "
                "mental state, intent or attitude toward ALBA."
            )

            sentiment_counts = (
                text_df["sentiment_label"]
                .value_counts()
                .reindex(["Positive", "Neutral", "Negative"], fill_value=0)
                .rename_axis("Sentiment")
                .reset_index(name="Responses")
            )

            average_compound = text_df["sentiment_compound"].mean()
            tm1, tm2, tm3 = st.columns(3)
            tm1.metric("Analysed reflections", len(text_df))
            tm2.metric("Mean sentiment", f"{average_compound:+.2f}")
            tm3.metric(
                "Most common sentiment",
                sentiment_counts.sort_values("Responses", ascending=False).iloc[0][
                    "Sentiment"
                ],
            )

            word_cloud_image = make_word_cloud(text_df["free_text_response"])
            if word_cloud_image is not None:
                st.markdown("##### Word cloud")
                st.image(word_cloud_image, use_container_width=True)

            text_col1, text_col2 = st.columns(2)

            with text_col1:
                fig_sentiment = px.pie(
                    sentiment_counts,
                    values="Responses",
                    names="Sentiment",
                    hole=0.55,
                    color="Sentiment",
                    color_discrete_map={
                        "Positive": ALBA_COLORS["green"],
                        "Neutral": ALBA_COLORS["blue"],
                        "Negative": ALBA_COLORS["pink"],
                    },
                )
                fig_sentiment.update_layout(
                    title="Sentiment categories",
                    margin=dict(l=10, r=10, t=50, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color=THEME["text"],
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)

            with text_col2:
                fig_compound = px.histogram(
                    text_df,
                    x="sentiment_compound",
                    nbins=15,
                    range_x=[-1, 1],
                    labels={
                        "sentiment_compound": "VADER compound sentiment"
                    },
                    color_discrete_sequence=[ALBA_COLORS["purple"]],
                )
                fig_compound.update_layout(
                    title="Sentiment-score distribution",
                    margin=dict(l=10, r=10, t=50, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color=THEME["text"],
                )
                st.plotly_chart(fig_compound, use_container_width=True)

            sentiment_scenario = (
                text_df.groupby("scenario_number")["sentiment_compound"]
                .mean()
                .reset_index()
            )
            fig_sentiment_scenario = px.bar(
                sentiment_scenario,
                x="scenario_number",
                y="sentiment_compound",
                range_y=[-1, 1],
                labels={
                    "scenario_number": "Scenario",
                    "sentiment_compound": "Mean VADER sentiment",
                },
                color="sentiment_compound",
                color_continuous_scale=[
                    [0.0, ALBA_COLORS["pink"]],
                    [0.5, ALBA_COLORS["blue"]],
                    [1.0, ALBA_COLORS["green"]],
                ],
            )
            fig_sentiment_scenario.update_layout(
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=25, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color=THEME["text"],
            )
            st.plotly_chart(fig_sentiment_scenario, use_container_width=True)

    st.caption(
        "All demographic breakdowns should be interpreted cautiously. "
        "Groups with fewer than five participants are suppressed."
    )

    with st.expander("Organiser export and data-file information"):
        st.markdown(
            f"""
            **Current runtime data file:** `{DATA_FILE.name}`

            The deployed app creates this CSV inside Streamlit Community Cloud's
            temporary runtime environment. It is not automatically added to GitHub
            or downloaded to your computer. Use the organiser download buttons below
            to obtain a local copy.

            **Important:** runtime files can be lost when the cloud app is rebuilt,
            rebooted or moved to a new environment. Persistent external storage is
            recommended before the live event.
            """
        )

        organiser_password = get_organiser_password()

        file_exists = DATA_FILE.exists()
        file_size_kb = (
            DATA_FILE.stat().st_size / 1024
            if file_exists
            else 0
        )

        status_col1, status_col2 = st.columns(2)
        status_col1.metric(
            "Runtime CSV status",
            "Available" if file_exists else "Not created yet",
        )
        status_col2.metric(
            "Runtime CSV size",
            f"{file_size_kb:.1f} KB",
        )

        if not organiser_password:
            st.info(
                "Raw-data export is disabled until an organiser password is configured "
                "in Streamlit secrets as `analytics_password`."
            )
        else:
            entered_password = st.text_input(
                "Organiser password",
                type="password",
                key="organiser_password_input",
            )
            if entered_password == organiser_password:
                st.success("Organiser access granted.")
                st.download_button(
                    "Download complete anonymised dataset",
                    data=df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="alba_bias_activity_full_export.csv",
                    mime="text/csv",
                )

                text_export = prepare_text_analytics(df)
                st.download_button(
                    "Download free-text sentiment export",
                    data=text_export.to_csv(index=False).encode("utf-8-sig"),
                    file_name="alba_bias_activity_text_sentiment.csv",
                    mime="text/csv",
                )
            elif entered_password:
                st.error("Incorrect organiser password.")


# ============================================================
# Participant experience
# ============================================================

def render_landing():
    image_if_available(
        IMAGE_DIR / "header.png",
        max_width=780,
    )
    st.title("Bias in Scientific Thinking")
    st.markdown(
        """
        <div class="alba-card">
        Explore six short scenarios about scientific and professional judgement.
        Select the response that feels most natural, then reveal the educational
        explanation before moving to the next scenario.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        - Approximate completion time: **4–6 minutes**
        - Responses are collected anonymously
        - The activity is educational and **not a psychological assessment**
        - Please do not enter names, email addresses or other identifying details
        """
    )
    render_how_it_works()

    if st.button("Start activity", type="primary", use_container_width=True):
        st.session_state.stage = "demographics"
        safe_rerun()


def render_demographics():
    st.title("About you")
    st.caption(
        "These questions help us explore aggregate response patterns. "
        "Please do not provide directly identifying information."
    )

    with st.form("demographic_form"):
        career_stage = st.selectbox(
            "Career stage / role",
            CAREER_STAGES,
            index=None,
            placeholder="Select one option",
        )

        country = st.selectbox(
            "Country where you currently work or study",
            COUNTRIES,
            index=None,
            placeholder="Select a country",
        )

        gender = st.selectbox(
            "Gender (optional)",
            GENDER_OPTIONS,
            index=0,
        )

        gender_self_describe = ""
        if gender == "Prefer to self-describe":
            gender_self_describe = st.text_input(
                "How would you like to describe your gender? (optional)",
                max_chars=80,
            )

        age_group = st.selectbox(
            "Age group",
            AGE_GROUPS,
            index=None,
            placeholder="Select one option",
        )

        alba_member = st.selectbox(
            "Are you an ALBA member?",
            ALBA_OPTIONS,
            index=None,
            placeholder="Select one option",
        )

        submitted = st.form_submit_button(
            "Continue to Scenario 1",
            use_container_width=True,
        )

    if submitted:
        missing = [
            label
            for label, value in {
                "Career stage / role": career_stage,
                "Country": country,
                "Age group": age_group,
                "ALBA membership": alba_member,
            }.items()
            if value is None
        ]

        if missing:
            st.error("Please complete: " + ", ".join(missing))
        else:
            st.session_state.demographics = {
                "career_stage": career_stage,
                "country": country,
                "gender": gender,
                "gender_self_describe": gender_self_describe,
                "age_group": age_group,
                "alba_member": alba_member,
            }
            st.session_state.stage = "scenario"
            safe_rerun()


def render_scenario():
    index = st.session_state.scenario_index
    scenario = SCENARIOS[index]

    st.progress((index + 1) / len(SCENARIOS))
    st.caption(f"{index + 1} of {len(SCENARIOS)}")

    # Neutral title prevents priming
    st.title(scenario["neutral_title"])
    image_if_available(
        scenario["image"],
        caption=f"Illustration for {scenario['neutral_title']}",
        max_width=650,
    )
    st.markdown(
        f'<div class="alba-card">{scenario["question"].replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )

    existing = st.session_state.responses.get(scenario["id"], {})
    saved_option = existing.get("selected_option")

    option_labels = {
        key: f"{key}) {value['text']}"
        for key, value in scenario["options"].items()
    }

    if not st.session_state.answer_confirmed:
        with st.form(f"scenario_form_{scenario['id']}"):
            selected_label = st.radio(
                "Choose one response",
                options=list(option_labels.values()),
                index=(
                    list(option_labels.keys()).index(saved_option)
                    if saved_option in option_labels
                    else None
                ),
            )

            free_text = st.text_area(
                "Optional: what informed your response?",
                value=existing.get("free_text_response", ""),
                max_chars=600,
                placeholder="Please avoid names or identifiable information.",
            )

            confirm = st.form_submit_button(
                "Confirm answer",
                use_container_width=True,
            )

        if confirm:
            if selected_label is None:
                st.error("Please select an answer before confirming.")
            else:
                selected_option = selected_label[0]
                st.session_state.responses[scenario["id"]] = {
                    "selected_option": selected_option,
                    "free_text_response": free_text,
                }
                st.session_state.answer_confirmed = True
                safe_rerun()

    else:
        response = st.session_state.responses[scenario["id"]]
        selected_option = response["selected_option"]
        option = scenario["options"][selected_option]

        st.success(f"You selected option {selected_option}.")
        st.markdown(
            f"""
            <div class="education-card">
            <h3>What might be at play here?</h3>
            <p><strong>{scenario["bias_family"]}</strong></p>
            <p>{scenario["explanation"]}</p>
            <p class="small-muted">
            This response receives <strong>{option["score"]} point(s)</strong>.
            {option["rationale"]}
            </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        next_label = (
            "View reflection summary"
            if index == len(SCENARIOS) - 1
            else "Next scenario"
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Change answer", use_container_width=True):
                st.session_state.answer_confirmed = False
                safe_rerun()

        with col2:
            if st.button(next_label, use_container_width=True):
                if index == len(SCENARIOS) - 1:
                    save_submission()
                    st.session_state.stage = "summary"
                else:
                    st.session_state.scenario_index += 1
                    st.session_state.answer_confirmed = False
                safe_rerun()


def render_summary():
    save_submission()

    st.title("Your reflection summary")
    st.markdown(
        """
        Your result is based on six **bias scores**. Each response contributes
        **0, 1 or 2 points**, and a larger total indicates that more bias-related
        responses appeared across these scenarios.
        """
    )
    render_how_it_works()

    summary_df = participant_summary_dataframe()
    total_score = int(summary_df["Points"].sum())
    score_level, score_interpretation = interpret_score(total_score)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total bias score", f"{total_score} / 12")
    with col2:
        st.markdown(
            f"""
            <div class="education-card">
                <h3>{score_level}</h3>
                <p>{score_interpretation}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    score_chart = summary_df[["Scenario", "Points"]].copy()
    fig = px.bar(
        score_chart,
        x="Scenario",
        y="Points",
        range_y=[0, 2],
        text="Points",
        color="Points",
        color_continuous_scale=[
            [0.0, ALBA_COLORS["pink"]],
            [0.5, ALBA_COLORS["yellow"]],
            [1.0, ALBA_COLORS["green"]],
        ],
    )
    fig.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=25, b=10),
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Review my six responses and bias scores"):
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

    historical_df = load_data()

    if not historical_df.empty and "total_score" in historical_df.columns:
        st.markdown("### Compare with other respondents")

        comparison_dimension_map = {
            "All respondents": None,
            "Career stage / role": "career_stage",
            "Age group": "age_group",
            "Country": "country",
            "Gender": "gender",
            "ALBA membership": "alba_member",
        }

        comparison_label = st.selectbox(
            "Comparison view",
            list(comparison_dimension_map.keys()),
            key="participant_comparison_dimension",
        )

        comparison_dimension = comparison_dimension_map[comparison_label]
        comparison_df = historical_df.copy()

        if comparison_dimension:
            participant_value = st.session_state.demographics[comparison_dimension]
            comparison_df = comparison_df[
                comparison_df[comparison_dimension] == participant_value
            ]
            st.caption(
                f"Showing respondents with the same {comparison_label.lower()}: "
                f"{participant_value}"
            )

        participant_scores = (
            comparison_df[
                ["participant_id", "total_score", "score_level"]
            ]
            .drop_duplicates(subset=["participant_id"])
        )
        comparison_n = participant_scores["participant_id"].nunique()

        if comparison_n < 5:
            st.info(
                "This comparison is not displayed because fewer than five participants "
                "are currently represented in this subgroup."
            )
        else:
            level_order = [
                "Low bias awareness",
                "Developing awareness",
                "Strong bias awareness",
            ]
            level_counts = (
                participant_scores["score_level"]
                .value_counts()
                .reindex(level_order, fill_value=0)
                .rename_axis("Score level")
                .reset_index(name="Participants")
            )

            comparison_fig = px.bar(
                level_counts,
                x="Score level",
                y="Participants",
                color="Score level",
                color_discrete_sequence=[
                    ALBA_COLORS["pink"],
                    ALBA_COLORS["yellow"],
                    ALBA_COLORS["green"],
                ],
            )
            comparison_fig.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=25, b=10),
            )
            st.plotly_chart(comparison_fig, use_container_width=True)

    st.info(
        "This is a reflective educational tool, not a diagnostic instrument. "
        "The result is intended to surface patterns worth noticing, not to label individuals."
    )
    st.success("Thank you for taking part.")

    if st.button("CLEAR — start a new participant", use_container_width=True):
        reset_participant()


# ============================================================
# Render selected view
# ============================================================

if st.session_state.view == "analytics":
    render_analytics()
else:
    if st.session_state.stage == "landing":
        render_landing()
    elif st.session_state.stage == "demographics":
        render_demographics()
    elif st.session_state.stage == "scenario":
        render_scenario()
    elif st.session_state.stage == "summary":
        render_summary()
