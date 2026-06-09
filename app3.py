import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os

# ============================================================
# Basic configuration
# ============================================================

st.set_page_config(
    page_title="Bias Reflection Activity",
    page_icon="🧠",
    layout="centered"
)

DATA_FILE = "responses_app3.csv"

# ============================================================
# Scenario data
# ============================================================

scenarios = [
    {
        "id": "gender_bias",
        "title": "Gender Bias",
        "image": "images/gender_bias.png",
        "question": (
            "During interviews for a caregiving role in a hospital, the interviewer mentions "
            "that the team works well because “people here tend to have a natural sense of "
            "empathy and care.”\n\n"
            "How might this statement influence the evaluation of candidates?"
        ),
        "options": {
            "A": {
                "text": "It might lead the interviewer to unconsciously favour some candidates over others.",
                "bias": "Gender Bias"
            },
            "B": {
                "text": "It simply reflects the importance of interpersonal skills in the role.",
                "bias": "Potentially Unrecognised Bias"
            },
            "C": {
                "text": "It does not affect how candidates are evaluated.",
                "bias": "Bias Blind Spot"
            }
        }
    },
    {
        "id": "confirmation_bias",
        "title": "Confirmation Bias",
        "image": "images/confirmation_bias.png",
        "question": (
            "You come across a preprint strongly supporting your hypothesis about the role "
            "of microglia in Alzheimer’s disease and share it with your lab. Later, a colleague "
            "sends you another preprint presenting contradictory findings.\n\n"
            "How do you react?"
        ),
        "options": {
            "A": {
                "text": "You focus mainly on the first preprint since it aligns with your hypothesis.",
                "bias": "Confirmation Bias"
            },
            "B": {
                "text": "You critically compare both preprints and evaluate the evidence.",
                "bias": "Balanced Scientific Reasoning"
            },
            "C": {
                "text": "You decide not to look into the second preprint for now.",
                "bias": "Confirmation Bias"
            }
        }
    },
    {
        "id": "attribution_bias",
        "title": "Attribution Bias",
        "image": "images/attribution_bias.png",
        "question": (
            "A PI, Dr. P, has often described his postdoc Dr. E as highly innovative. "
            "When Dr. E’s novel optogenetics protocol yields groundbreaking results, "
            "Dr. P reflects on why it worked.\n\n"
            "What is most likely to come to his mind?"
        ),
        "options": {
            "A": {
                "text": "The success is linked to Dr. E’s innate creativity.",
                "bias": "Attribution Bias"
            },
            "B": {
                "text": "The protocol succeeded because of meticulous planning and collaboration.",
                "bias": "Context-Aware Reasoning"
            },
            "C": {
                "text": "Dr. P does not think much about why it worked.",
                "bias": "Low Reflection"
            }
        }
    },
    {
        "id": "stereotype_threat",
        "title": "Stereotype Threat",
        "image": "images/stereotype_threat.png",
        "question": (
            "K., a PhD student, is about to present his research on neurogenesis at a major "
            "conference. He is aware of the stereotype that students from his background are "
            "often perceived as less confident in high-stakes academic settings.\n\n"
            "How might this awareness affect him?"
        ),
        "options": {
            "A": {
                "text": "It could increase his anxiety about confirming the stereotype.",
                "bias": "Stereotype Threat"
            },
            "B": {
                "text": "His preparation and mastery of the data will determine his confidence.",
                "bias": "Individual-Merit Framing"
            },
            "C": {
                "text": "The stereotype probably does not cross his mind during the presentation.",
                "bias": "Bias Minimisation"
            }
        }
    },
    {
        "id": "prestige_bias",
        "title": "Regional / Prestige Bias",
        "image": "images/prestige_bias.png",
        "question": (
            "Two applicants for a neuroimaging specialist role have similar CVs. "
            "Dr. X has worked at Harvard Medical School, while Dr. Y has experience "
            "in San Giovanni Hospital in Italy.\n\n"
            "Who seems more likely to bring innovative ideas?"
        ),
        "options": {
            "A": {
                "text": "Dr. X, with experience in a high-profile institution.",
                "bias": "Prestige Bias"
            },
            "B": {
                "text": "Both candidates are equally likely to be innovative.",
                "bias": "Balanced Reasoning"
            },
            "C": {
                "text": "There is not enough information to tell.",
                "bias": "Evidence-Based Caution"
            }
        }
    },
    {
        "id": "affinity_bias",
        "title": "Affinity Bias",
        "image": "images/affinity_bias.png",
        "question": (
            "While reviewing applications for a PhD position, you notice that Élodie Laurent "
            "shares your passion for neuroethics and has cited your work in her proposal.\n\n"
            "How might this affect your impression?"
        ),
        "options": {
            "A": {
                "text": "You may feel a stronger connection to Élodie.",
                "bias": "Affinity Bias"
            },
            "B": {
                "text": "You focus primarily on the scientific merit of all applicants.",
                "bias": "Structured Evaluation"
            },
            "C": {
                "text": "It does not influence your impression.",
                "bias": "Bias Blind Spot"
            }
        }
    }
]

# ============================================================
# Feedback explanations
# ============================================================

feedback = {
    "Gender Bias": (
        "Gender bias can shape assumptions about who is naturally suited to particular roles, "
        "skills, or behaviours. Even positive-sounding assumptions can influence evaluation."
    ),
    "Potentially Unrecognised Bias": (
        "Some biases are subtle because they appear inside apparently neutral or positive statements. "
        "A statement about empathy or care may still influence how candidates are perceived."
    ),
    "Bias Blind Spot": (
        "Bias blind spot refers to the tendency to recognise bias in others more easily than in ourselves. "
        "In real settings, bias often operates even when people believe they are being neutral."
    ),
    "Confirmation Bias": (
        "Confirmation bias occurs when we give more weight to evidence that supports what we already believe. "
        "In science, it can affect literature interpretation, hypothesis testing, and peer discussion."
    ),
    "Balanced Scientific Reasoning": (
        "Balanced scientific reasoning involves critically comparing evidence, including evidence that challenges "
        "our assumptions. This is central to robust scientific thinking."
    ),
    "Attribution Bias": (
        "Attribution bias occurs when we explain outcomes mainly through personal traits while underestimating "
        "planning, context, teamwork, resources, or circumstances."
    ),
    "Context-Aware Reasoning": (
        "Context-aware reasoning considers both individual contribution and the wider conditions that made an "
        "outcome possible, such as collaboration, preparation, and methodological design."
    ),
    "Low Reflection": (
        "Low reflection can allow assumptions to pass unnoticed. In fast academic or clinical environments, "
        "taking time to examine why something happened can reduce biased interpretation."
    ),
    "Stereotype Threat": (
        "Stereotype threat occurs when awareness of a stereotype creates additional pressure or anxiety in a "
        "performance situation. This can influence confidence, attention, and behaviour."
    ),
    "Individual-Merit Framing": (
        "A purely individual-merit framing may overlook how social expectations, stereotypes, or environmental "
        "pressures affect performance and confidence."
    ),
    "Bias Minimisation": (
        "Bias minimisation occurs when we assume that stereotypes or expectations have little or no influence. "
        "In practice, such pressures may affect people even when they are not openly discussed."
    ),
    "Prestige Bias": (
        "Prestige bias occurs when reputation, institutional status, or perceived excellence influences judgement "
        "more than the direct evidence available."
    ),
    "Balanced Reasoning": (
        "Balanced reasoning avoids over-interpreting reputation, status, or institutional background when the "
        "available evidence does not justify a strong conclusion."
    ),
    "Evidence-Based Caution": (
        "Evidence-based caution means recognising when there is not enough information to make a confident judgement. "
        "This can protect against overconfidence and bias."
    ),
    "Affinity Bias": (
        "Affinity bias occurs when shared interests, values, background, or professional connections make us feel "
        "more positively toward someone."
    ),
    "Structured Evaluation": (
        "Structured evaluation helps reduce bias by applying the same criteria to all people, ideas, applications, "
        "or pieces of evidence."
    )
}

# ============================================================
# Session-state initialisation
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "activity"

if "clear_counter" not in st.session_state:
    st.session_state.clear_counter = 0

if "last_submission" not in st.session_state:
    st.session_state.last_submission = None


# ============================================================
# Helper functions
# ============================================================

def save_responses(rows, data_file):
    """Save new responses to CSV, appending to existing responses if available."""
    new_data = pd.DataFrame(rows)

    if os.path.exists(data_file):
        existing_data = pd.read_csv(data_file)
        all_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        all_data = new_data

    all_data.to_csv(data_file, index=False, encoding="utf-8-sig")
    return new_data


def show_scenario_image(image_path, title):
    """Display scenario image if it exists; otherwise show a gentle placeholder message."""
    if os.path.exists(image_path):
        st.image(
            image_path,
            caption=f"Scenario illustration: {title}",
            use_container_width=True
        )
    else:
        st.info(
            f"Image placeholder for: {title}. "
            f"Add an image at `{image_path}` to display it here."
        )


def clear_current_user_inputs():
    """
    Reset form fields for the next participant.

    Streamlit widgets persist through session_state.
    Increasing clear_counter changes widget keys, creating a fresh form.
    """
    st.session_state.clear_counter += 1
    st.session_state.last_submission = None
    st.session_state.page = "activity"


def show_analytics_dashboard():
    """Read historical data and show aggregate analytics."""
    st.title("📊 Bias Reflection Analytics Dashboard")

    st.markdown(
        """
        This dashboard summarises the anonymised historical responses collected by the app.
        It is intended for organisers and post-event reporting.
        """
    )

    if not os.path.exists(DATA_FILE):
        st.warning("No response file found yet. Complete at least one participant response first.")
        return

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        st.warning("The response file exists, but it does not contain any responses yet.")
        return

    # ------------------------------------------------------------
    # Core metrics
    # ------------------------------------------------------------

    total_participants = df["participant_id"].nunique()
    total_answers = len(df)
    total_free_text = df["free_text_response"].fillna("").str.strip().astype(bool).sum()
    total_scenarios = df["scenario_id"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Participants", total_participants)
    col2.metric("Scenario answers", total_answers)
    col3.metric("Free-text responses", total_free_text)
    col4.metric("Scenarios", total_scenarios)

    st.divider()

    # ------------------------------------------------------------
    # Bias frequency
    # ------------------------------------------------------------

    st.subheader("Most common mapped bias / reasoning types")

    bias_counts = (
        df["mapped_bias"]
        .value_counts()
        .reset_index()
    )
    bias_counts.columns = ["Mapped bias / reasoning type", "Count"]

    st.dataframe(bias_counts, use_container_width=True)

    st.bar_chart(
        bias_counts.set_index("Mapped bias / reasoning type")
    )

    st.divider()

    # ------------------------------------------------------------
    # Scenario distribution
    # ------------------------------------------------------------

    st.subheader("Responses by scenario")

    scenario_counts = (
        df["scenario_title"]
        .value_counts()
        .reset_index()
    )
    scenario_counts.columns = ["Scenario", "Number of responses"]

    st.dataframe(scenario_counts, use_container_width=True)

    st.bar_chart(
        scenario_counts.set_index("Scenario")
    )

    st.divider()

    # ------------------------------------------------------------
    # Mapped bias by scenario
    # ------------------------------------------------------------

    st.subheader("Mapped bias / reasoning type by scenario")

    scenario_bias_counts = (
        df.groupby(["scenario_title", "mapped_bias"])
        .size()
        .reset_index(name="Count")
        .sort_values(["scenario_title", "Count"], ascending=[True, False])
    )

    st.dataframe(scenario_bias_counts, use_container_width=True)

    st.divider()

    # ------------------------------------------------------------
    # Option distribution by scenario
    # ------------------------------------------------------------

    st.subheader("Option distribution by scenario")

    option_counts = (
        df.groupby(["scenario_title", "selected_option", "mapped_bias"])
        .size()
        .reset_index(name="Count")
        .sort_values(["scenario_title", "selected_option"])
    )

    st.dataframe(option_counts, use_container_width=True)

    st.divider()

    # ------------------------------------------------------------
    # Free-text responses
    # ------------------------------------------------------------

    st.subheader("Anonymised free-text responses")

    free_text_df = df[
        df["free_text_response"].fillna("").str.strip() != ""
    ][
        [
            "timestamp",
            "scenario_title",
            "selected_option",
            "mapped_bias",
            "free_text_response"
        ]
    ]

    if free_text_df.empty:
        st.info("No free-text responses have been entered yet.")
    else:
        st.dataframe(free_text_df, use_container_width=True)

    st.divider()

    # ------------------------------------------------------------
    # Raw data and download
    # ------------------------------------------------------------

    st.subheader("Raw anonymised historical data")

    st.dataframe(df, use_container_width=True)

    csv_data = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Download full anonymised CSV",
        data=csv_data,
        file_name="bias_reflection_historical_data.csv",
        mime="text/csv"
    )


# ============================================================
# Top navigation buttons
# ============================================================

top_col1, top_col2, top_col3 = st.columns([1, 1, 1])

with top_col1:
    if st.button("🧹 Clear for next user"):
        clear_current_user_inputs()
        st.rerun()

with top_col2:
    if st.button("📊 Show Analytics"):
        st.session_state.page = "analytics"
        st.rerun()

with top_col3:
    if st.button("🧠 Show Activity"):
        st.session_state.page = "activity"
        st.rerun()


# ============================================================
# Analytics page
# ============================================================

if st.session_state.page == "analytics":
    show_analytics_dashboard()
    st.stop()


# ============================================================
# Activity page
# ============================================================

st.title("🧠 Bias Reflection Activity")

st.markdown(
    """
    This short activity explores how bias can influence scientific thinking,
    academic judgement, and everyday decision-making.

    You will see a series of short scenarios. For each one:

    1. Look at the scenario image.
    2. Read the scenario.
    3. Choose the answer that feels most natural to you.
    4. Optionally write one or two sentences explaining your choice.

    This activity is **anonymous**, **educational**, and **not diagnostic**.
    """
)

st.warning(
    "Please do not include names, contact details, or identifiable personal information "
    "in your written responses."
)

st.divider()

# ============================================================
# Main form
# ============================================================

responses = []

form_key = f"bias_reflection_form_{st.session_state.clear_counter}"

with st.form(form_key):

    for number, scenario in enumerate(scenarios, start=1):

        st.subheader(f"{number}. {scenario['title']}")

        show_scenario_image(scenario["image"], scenario["title"])

        st.markdown(scenario["question"])

        option_labels = []
        for option_key, option_data in scenario["options"].items():
            option_labels.append(f"{option_key}) {option_data['text']}")

        selected_label = st.radio(
            "Choose one response:",
            option_labels,
            key=f"radio_{scenario['id']}_{st.session_state.clear_counter}"
        )

        free_text = st.text_area(
            "Optional: briefly explain your choice",
            key=f"text_{scenario['id']}_{st.session_state.clear_counter}",
            height=90,
            placeholder="Write one or two sentences about why you selected this answer..."
        )

        selected_option_key = selected_label[0]
        selected_option_data = scenario["options"][selected_option_key]

        responses.append({
            "scenario_id": scenario["id"],
            "scenario_title": scenario["title"],
            "selected_option": selected_option_key,
            "selected_text": selected_option_data["text"],
            "mapped_bias": selected_option_data["bias"],
            "free_text_response": free_text
        })

        st.divider()

    submitted = st.form_submit_button("Submit and see my reflection")


# ============================================================
# Submission and feedback
# ============================================================

if submitted:

    participant_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat(timespec="seconds")

    rows = []

    for response in responses:
        rows.append({
            "participant_id": participant_id,
            "timestamp": timestamp,
            "scenario_id": response["scenario_id"],
            "scenario_title": response["scenario_title"],
            "selected_option": response["selected_option"],
            "selected_text": response["selected_text"],
            "mapped_bias": response["mapped_bias"],
            "free_text_response": response["free_text_response"]
        })

    new_data = save_responses(rows, DATA_FILE)
    st.session_state.last_submission = new_data

    st.success("Thank you. Your reflection summary is ready.")

    st.header("Your reflection summary")

    st.markdown(
        """
        The points below show the thinking patterns linked to your selected responses.
        This does **not** mean that you “have” these biases. It simply shows how different
        choices in these scenarios may connect to known patterns in human judgement.
        """
    )

    selected_biases = new_data["mapped_bias"].value_counts()

    for bias_name, count in selected_biases.items():
        st.subheader(bias_name)
        st.write(
            feedback.get(
                bias_name,
                "This response reflects an interesting judgement pattern."
            )
        )

    st.info(
        "This is not a psychological assessment. It is a short educational reflection "
        "on how judgement can be shaped by context, expectations, familiarity, reputation, "
        "and prior beliefs."
    )

    st.subheader("Your anonymous response summary")

    st.dataframe(
        new_data[
            [
                "scenario_title",
                "selected_option",
                "mapped_bias",
                "free_text_response"
            ]
        ],
        use_container_width=True
    )

    st.download_button(
        label="Download your anonymous response summary",
        data=new_data.to_csv(index=False).encode("utf-8-sig"),
        file_name="my_bias_reflection_summary.csv",
        mime="text/csv"
    )

    st.divider()

    st.markdown(
        """
        When the next visitor is ready, press **Clear for next user** at the top of the page.
        """
    )