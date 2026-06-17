import base64
import os
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import pycountry
import streamlit as st


# ============================================================
# Configuration
# ============================================================

st.set_page_config(
    page_title="Bias in Scientific Thinking",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path("responses_app4.csv")
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
            background: linear-gradient(180deg, #ffffff 0%, {ALBA_COLORS["light"]} 100%);
        }}

        h1, h2, h3 {{
            color: {ALBA_COLORS["purple"]};
        }}

        .alba-card {{
            background: white;
            padding: 1.25rem 1.35rem;
            border-radius: 16px;
            border-left: 6px solid {ALBA_COLORS["blue"]};
            box-shadow: 0 5px 18px rgba(62, 61, 129, 0.10);
            margin-bottom: 1rem;
        }}

        .education-card {{
            background: #ffffff;
            padding: 1.2rem 1.35rem;
            border-radius: 16px;
            border: 2px solid {ALBA_COLORS["green"]};
            margin-top: 1rem;
        }}

        .small-muted {{
            color: #626262;
            font-size: 0.92rem;
        }}

        .stButton > button {{
            border-radius: 10px;
            border: 0;
            background: {ALBA_COLORS["purple"]};
            color: white;
            font-weight: 600;
            min-height: 2.8rem;
        }}

        .stButton > button:hover {{
            background: {ALBA_COLORS["blue"]};
            color: white;
        }}

        div[data-testid="stMetric"] {{
            background: white;
            border-radius: 14px;
            padding: 0.8rem;
            border-top: 5px solid {ALBA_COLORS["pink"]};
            box-shadow: 0 4px 14px rgba(62, 61, 129, 0.08);
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
                "orientation": "Minimising / blind-spot",
                "detail": "Potentially unrecognised bias",
            },
            "B": {
                "text": "It could subtly steer the team toward certain candidates without anyone realising.",
                "orientation": "Bias-aware",
                "detail": "Recognition of gendered assumptions",
            },
            "C": {
                "text": "It is too vague to have any real influence on decisions.",
                "orientation": "Minimising / blind-spot",
                "detail": "Bias minimisation",
            },
        },
        "explanation": (
            'The comment about someone "people feel comfortable opening up to" sounds neutral, '
            "but it subtly invokes traits more commonly associated with women—warmth, emotional "
            "availability and nurturance. Without anyone explicitly saying so, this language can "
            "steer evaluators toward candidates who fit a gendered image of care. The bias is not "
            "necessarily in the words themselves, but in the assumptions they may activate."
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
                "text": "You read both but find yourself spending more time on the one that fits your framework.",
                "orientation": "Bias-leaning",
                "detail": "Confirmation bias",
            },
            "B": {
                "text": "You flag both preprints at the next lab meeting and discuss them equally.",
                "orientation": "Reflective / balanced",
                "detail": "Balanced scientific reasoning",
            },
            "C": {
                "text": "You set aside the contradicting preprint until after your upcoming grant submission.",
                "orientation": "Bias-leaning",
                "detail": "Confirmation bias",
            },
        },
        "explanation": (
            "We tend to engage more critically with evidence that challenges us and more "
            "generously with evidence that confirms what we already believe. In research, "
            "this can appear as spending less time on contradictory evidence, reading it more "
            'sceptically, or filing it away for "later".'
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
                "text": "He talks about the months of troubleshooting, failed iterations and cross-team input that got them there.",
                "orientation": "Context-aware",
                "detail": "Context-aware reasoning",
            },
            "B": {
                "text": "He says it came together because Dr. E has a kind of intuition that is hard to teach.",
                "orientation": "Bias-leaning",
                "detail": "Attribution bias",
            },
            "C": {
                "text": "He lets Dr. E present the work and steps back from the narrative entirely.",
                "orientation": "Protective / corrective",
                "detail": "Corrective attribution practice",
            },
        },
        "explanation": (
            "When we already hold a positive image of someone, we may explain their success "
            "mainly in terms of who they are—their talent, instinct or character. This can "
            "flatten the fuller story of collaboration, failed attempts and structural support. "
            "The reverse can also occur when other people's success is attributed to luck or circumstance."
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
                "orientation": "Mixed / context-sensitive",
                "detail": "Performance pressure response",
            },
            "B": {
                "text": "It stays with him, and he finds it harder to settle into his delivery.",
                "orientation": "Bias-aware",
                "detail": "Recognition of stereotype threat",
            },
            "C": {
                "text": "He brushes it off and presents exactly as he prepared.",
                "orientation": "Minimising / blind-spot",
                "detail": "Bias minimisation",
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
                "text": "You find yourself reading Dr. X's application with more anticipation.",
                "orientation": "Bias-leaning",
                "detail": "Prestige bias",
            },
            "B": {
                "text": "You are curious about the constraints Dr. Y worked under and what that required of them.",
                "orientation": "Context-aware",
                "detail": "Context-aware reasoning",
            },
            "C": {
                "text": "You treat both files the same—institutional context does not factor in.",
                "orientation": "Reflective / balanced",
                "detail": "Procedural neutrality",
            },
        },
        "explanation": (
            "Prestige bias uses institutional reputation as a shortcut for individual quality. "
            "It can conflate the visibility and resources of an institution with the ability "
            "of the person. Researchers working in smaller or under-resourced settings may "
            "have developed substantial skill and independence that a conventional CV comparison misses."
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
                "text": "You notice you are more invested in her application than the others.",
                "orientation": "Bias-leaning",
                "detail": "Affinity bias",
            },
            "B": {
                "text": "You treat it as one data point among many and move on.",
                "orientation": "Reflective / balanced",
                "detail": "Structured evaluation",
            },
            "C": {
                "text": "You flag it to the panel as a potential conflict and recuse yourself from her evaluation.",
                "orientation": "Protective / corrective",
                "detail": "Conflict-management response",
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


def save_submission():
    if st.session_state.submission_saved:
        return

    participant_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat(timespec="seconds")
    st.session_state.participant_id = participant_id

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
                "reasoning_orientation": option["orientation"],
                "detailed_label": option["detail"],
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
                "Selected option": response["selected_option"],
                "Reasoning category": option["orientation"],
                "Detailed label": option["detail"],
            }
        )
    return pd.DataFrame(rows)


def render_how_it_works():
    with st.expander("How this works", expanded=False):
        st.markdown(
            """
            Each answer option is manually pre-tagged with two non-diagnostic descriptors:

            **1. A broad reasoning orientation**, such as *Bias-leaning*, 
            *Reflective / balanced*, *Context-aware*, *Bias-aware*, 
            *Protective / corrective* or *Minimising / blind-spot*.

            **2. A more specific descriptive label**, such as *Confirmation bias*,
            *Structured evaluation* or *Context-aware reasoning*.

            The Reflection Summary is a simple frequency count of the broad reasoning
            orientations selected across the six scenarios. It is not weighted, probabilistic
            or diagnostic. The activity is designed for education and reflection.
            """
        )


def get_organiser_password():
    try:
        return st.secrets.get("analytics_password", "")
    except Exception:
        return os.getenv("ALBA_ANALYTICS_PASSWORD", "")


# ============================================================
# Navigation
# ============================================================

nav1, nav2, nav3 = st.columns([1.2, 1.2, 3.6])

with nav1:
    if st.button("🧠 Participant view", use_container_width=True):
        st.session_state.view = "activity"
        safe_rerun()

with nav2:
    if st.button("📊 Analytics", use_container_width=True):
        st.session_state.view = "analytics"
        safe_rerun()

with nav3:
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
    st.title("Analytics dashboard")

    df = load_data()
    if df.empty:
        st.info("No historical responses have been collected yet.")
        return

    total_participants = df["participant_id"].nunique()
    total_answers = len(df)
    total_completed = int(total_answers / len(SCENARIOS))
    alba_yes = df.loc[df["alba_member"] == "Yes", "participant_id"].nunique()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Participants", total_participants)
    m2.metric("Completed activities", total_completed)
    m3.metric("Scenario responses", total_answers)
    m4.metric("ALBA members", alba_yes)

    st.markdown("### Explore responses")

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
            "Compare or filter by",
            list(dimension_map.keys()),
        )

    selected_dimension = dimension_map[selected_dimension_label]
    filtered_df = df.copy()

    with filter_col2:
        if selected_dimension:
            values = sorted(
                filtered_df[selected_dimension].dropna().astype(str).unique().tolist()
            )
            selected_value = st.selectbox(
                f"Select {selected_dimension_label.lower()}",
                ["All"] + values,
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
            )

    subgroup_n = filtered_df["participant_id"].nunique()
    st.caption(f"Current view: {subgroup_n} participant(s)")

    if filtered_df.empty:
        st.warning("No responses match the selected filter.")
        return

    # Consolidated table: scenario × options, with category labels
    consolidated = (
        filtered_df.groupby(
            [
                "scenario_number",
                "bias_family",
                "selected_option",
                "reasoning_orientation",
            ]
        )
        .size()
        .reset_index(name="Count")
    )

    scenario_totals = (
        filtered_df.groupby("scenario_number")
        .size()
        .rename("Scenario total")
        .reset_index()
    )
    consolidated = consolidated.merge(scenario_totals, on="scenario_number")
    consolidated["Percent"] = (
        100 * consolidated["Count"] / consolidated["Scenario total"]
    ).round(1)

    st.markdown("#### Consolidated response dashboard")
    st.dataframe(
        consolidated[
            [
                "scenario_number",
                "bias_family",
                "selected_option",
                "reasoning_orientation",
                "Count",
                "Percent",
            ]
        ].rename(
            columns={
                "scenario_number": "Scenario",
                "bias_family": "Educational bias theme",
                "selected_option": "Option",
                "reasoning_orientation": "Reasoning category",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    chart_data = (
        filtered_df.groupby(
            ["scenario_number", "selected_option"]
        )
        .size()
        .reset_index(name="Count")
    )

    fig_options = px.bar(
        chart_data,
        x="scenario_number",
        y="Count",
        color="selected_option",
        barmode="group",
        labels={
            "scenario_number": "Scenario",
            "selected_option": "Selected option",
        },
        color_discrete_sequence=[
            ALBA_COLORS["purple"],
            ALBA_COLORS["blue"],
            ALBA_COLORS["pink"],
        ],
    )
    fig_options.update_layout(
        legend_title_text="Option",
        margin=dict(l=10, r=10, t=25, b=10),
    )
    st.plotly_chart(fig_options, use_container_width=True)

    orientation_data = (
        filtered_df["reasoning_orientation"]
        .value_counts()
        .rename_axis("Reasoning category")
        .reset_index(name="Count")
    )

    fig_orientation = px.bar(
        orientation_data,
        x="Reasoning category",
        y="Count",
        color="Reasoning category",
        color_discrete_sequence=[
            ALBA_COLORS["purple"],
            ALBA_COLORS["blue"],
            ALBA_COLORS["green"],
            ALBA_COLORS["pink"],
            ALBA_COLORS["yellow"],
        ],
    )
    fig_orientation.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=25, b=10),
    )
    st.plotly_chart(fig_orientation, use_container_width=True)

    st.caption(
        "Small subgroups should be interpreted cautiously. For public display, "
        "consider suppressing demographic comparisons where fewer than five participants are represented."
    )

    # Backend-only export: no raw or free-text tables displayed
    with st.expander("Organiser export"):
        organiser_password = get_organiser_password()

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

                free_text_df = df[
                    df["free_text_response"].fillna("").str.strip() != ""
                ]
                st.download_button(
                    "Download anonymised free-text responses",
                    data=free_text_df.to_csv(index=False).encode("utf-8-sig"),
                    file_name="alba_bias_activity_free_text_export.csv",
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
            Your selected response was pre-tagged as:
            <strong>{option["orientation"]}</strong>
            ({option["detail"]}).
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
        This summary shows the reasoning categories linked to your selected responses.
        It does not measure personality, ability or unconscious bias, and it should not
        be interpreted diagnostically.
        """
    )
    render_how_it_works()

    summary_df = participant_summary_dataframe()
    counts = (
        summary_df["Reasoning category"]
        .value_counts()
        .rename_axis("Reasoning category")
        .reset_index(name="Count")
    )

    fig = px.bar(
        counts,
        x="Reasoning category",
        y="Count",
        color="Reasoning category",
        color_discrete_sequence=[
            ALBA_COLORS["purple"],
            ALBA_COLORS["blue"],
            ALBA_COLORS["green"],
            ALBA_COLORS["pink"],
            ALBA_COLORS["yellow"],
        ],
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=10, r=10, t=25, b=10),
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Review my six responses"):
        st.dataframe(summary_df, hide_index=True, use_container_width=True)

    # Dynamic comparison with historical data
    historical_df = load_data()

    if not historical_df.empty:
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
            participant_value = st.session_state.demographics[
                comparison_dimension
            ]
            comparison_df = comparison_df[
                comparison_df[comparison_dimension] == participant_value
            ]
            st.caption(
                f"Showing respondents with the same {comparison_label.lower()}: "
                f"{participant_value}"
            )

        comparison_n = comparison_df["participant_id"].nunique()

        if comparison_n < 5:
            st.info(
                "This comparison is not displayed because fewer than five participants "
                "are currently represented in this subgroup."
            )
        else:
            comparison_data = (
                comparison_df.groupby(
                    ["scenario_number", "selected_option"]
                )
                .size()
                .reset_index(name="Count")
            )

            comparison_fig = px.bar(
                comparison_data,
                x="scenario_number",
                y="Count",
                color="selected_option",
                barmode="group",
                labels={
                    "scenario_number": "Scenario",
                    "selected_option": "Selected option",
                },
                color_discrete_sequence=[
                    ALBA_COLORS["purple"],
                    ALBA_COLORS["blue"],
                    ALBA_COLORS["pink"],
                ],
            )
            comparison_fig.update_layout(
                margin=dict(l=10, r=10, t=25, b=10),
            )
            st.plotly_chart(comparison_fig, use_container_width=True)

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
