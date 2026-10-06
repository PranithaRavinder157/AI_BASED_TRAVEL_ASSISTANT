"""
AI Travel Assistant - College Project
Built with Streamlit + Google Gemini (google-genai) + Geopy + Folium.
Run with:  streamlit run app.py
"""

import json
import os
import time

import folium
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from google import genai
from google.genai import types
from streamlit_folium import st_folium


# ----------------------------------------------------------------------------
# CONFIGURATION  (change the model name here if needed)
# ----------------------------------------------------------------------------
MODEL_NAME = "gemini-3.8-flash"
CURRENCY = "₹"
DISCLAIMER = ("⚠️ All prices, timings, availability and distances are AI-generated "
              "**estimates** and may change. Please verify current details before travelling.")

INTERESTS = ["Historical places", "Nature", "Adventure", "Shopping", "Beaches",
             "Culture", "Photography", "Food", "Entertainment"]
BUDGET_KEYS = ["accommodation", "food", "local_transport", "entry_tickets", "activities", "other"]


load_dotenv()  # reads GEMINI_API_KEY from the .env file
API_KEY = os.getenv("GEMINI_API_KEY")

st.set_page_config(page_title="AI Travel Assistant", page_icon="✈️", layout="wide")


# ----------------------------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------------------------
st.markdown("""
<style>

/* =========================================================
   MAIN TRAVEL APP BACKGROUND
   ========================================================= */

.stApp {
    background:
        linear-gradient(rgba(240, 249, 255, 0.94), rgba(255, 255, 255, 0.97)),
        radial-gradient(circle at top right, #bde0fe, transparent 35%),
        radial-gradient(circle at bottom left, #caf0f8, transparent 35%);
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}


/* =========================================================
   HERO / HEADER
   ========================================================= */

.hero {
    background:
        linear-gradient(135deg, rgba(0, 119, 182, 0.97), rgba(0, 180, 216, 0.94));

    padding: 38px 42px;
    border-radius: 24px;
    margin-bottom: 28px;

    box-shadow:
        0 12px 35px rgba(0, 119, 182, 0.25),
        inset 0 1px 0 rgba(255,255,255,0.25);

    border: 1px solid rgba(255,255,255,0.35);
    position: relative;
    overflow: hidden;
}

.hero::after {
    content: "✈️   🌍   🧳   🗺️";
    position: absolute;
    right: 30px;
    bottom: 18px;
    font-size: 2rem;
    opacity: 0.25;
    letter-spacing: 10px;
}

.hero h1 {
    color: #ffffff;
    margin: 0;
    font-size: 2.7rem;
    font-weight: 800;
    letter-spacing: -1px;
}

.hero p {
    color: #e8faff;
    margin: 8px 0 0 0;
    font-size: 1.15rem;
    font-weight: 500;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #dff6ff 0%,
            #f3fbff 55%,
            #ffffff 100%
        );

    border-right: 1px solid #c8eaf5;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #006994;
    font-weight: 800;
}

section[data-testid="stSidebar"] p {
    color: #34515f;
}


/* =========================================================
   TABS
   ========================================================= */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255,255,255,0.80);
    padding: 8px;
    border-radius: 16px;

    box-shadow:
        0 5px 18px rgba(0, 119, 182, 0.08);
}

.stTabs [data-baseweb="tab"] {
    height: 48px;
    padding: 0 18px;
    border-radius: 12px;

    font-weight: 700;
    font-size: 0.95rem;
    color: #356273;
}

.stTabs [data-baseweb="tab"]:hover {
    background: #e3f7fc;
    color: #0077b6;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0077b6, #00b4d8);
    color: white !important;
}


/* =========================================================
   INPUT BOXES
   ========================================================= */

div[data-baseweb="input"],
div[data-baseweb="select"],
div[data-baseweb="textarea"] {
    border-radius: 12px;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    border-radius: 12px;
    border: 1px solid #b9dce8;
    background: rgba(255,255,255,0.96);
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: #00a6c7;
    box-shadow: 0 0 0 2px rgba(0,166,199,0.12);
}


/* =========================================================
   FORM
   ========================================================= */

div[data-testid="stForm"] {
    background: rgba(255,255,255,0.94);
    padding: 25px;

    border-radius: 20px;
    border: 1px solid #d3edf5;

    box-shadow:
        0 8px 25px rgba(0, 100, 140, 0.08);
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #0077b6, #00b4d8);

    color: white;
    border: none;
    border-radius: 14px;

    padding: 12px 22px;

    font-weight: 700;
    font-size: 1rem;

    box-shadow:
        0 6px 16px rgba(0,119,182,0.22);

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease,
        background 0.2s ease;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #005f8f, #0096b7);

    transform: translateY(-2px);

    box-shadow:
        0 10px 22px rgba(0,119,182,0.28);
}

.stButton > button:active,
.stFormSubmitButton > button:active {
    transform: translateY(0);
}


/* =========================================================
   SECTION HEADINGS
   ========================================================= */

h1,
h2,
h3 {
    color: #075985;
}

.stSubheader {
    color: #006994;
    font-weight: 800;
}


/* =========================================================
   TRAVEL CARDS
   ========================================================= */

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.95);

    border-radius: 18px;
    border: 1px solid #d5edf5;

    box-shadow:
        0 7px 20px rgba(0, 100, 140, 0.08);

    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px);

    box-shadow:
        0 12px 28px rgba(0, 100, 140, 0.13);
}


/* =========================================================
   METRIC CARDS
   ========================================================= */

div[data-testid="stMetric"] {
    background:
        linear-gradient(145deg, #ffffff, #effaff);

    border: 1px solid #c9e8f2;
    border-radius: 18px;

    padding: 18px;

    box-shadow:
        0 7px 20px rgba(0,119,182,0.09);
}

div[data-testid="stMetricLabel"] {
    color: #4b7180;
    font-weight: 600;
}

div[data-testid="stMetricValue"] {
    color: #006994;
    font-weight: 800;
}


/* =========================================================
   ALERT / INFO BOXES
   ========================================================= */

div[data-testid="stAlert"] {
    border-radius: 14px;
    border-width: 1px;
}


/* =========================================================
   CHATBOT
   ========================================================= */

div[data-testid="stChatMessage"] {
    border-radius: 16px;
    margin-bottom: 10px;
    padding: 8px;
}

div[data-testid="stChatInput"] {
    border-radius: 16px;
}


/* =========================================================
   DATAFRAME / TABLE
   ========================================================= */

div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;

    border: 1px solid #cde8f1;

    box-shadow:
        0 5px 18px rgba(0,100,140,0.07);
}


/* =========================================================
   MAP
   ========================================================= */

iframe {
    border-radius: 18px !important;
}


/* =========================================================
   MULTISELECT TAGS
   ========================================================= */

span[data-baseweb="tag"] {
    background: #dff7fc !important;
    color: #006994 !important;
    border-radius: 10px !important;
}


/* =========================================================
   CAPTIONS
   ========================================================= */

.stCaption {
    color: #607d8b;
}


/* =========================================================
   LABELS
   ========================================================= */

label {
    font-weight: 600 !important;
    color: #315b6b !important;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

hr {
    border-color: #d8edf4;
}


/* =========================================================
   SCROLLBAR
   ========================================================= */

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #eefaff;
}

::-webkit-scrollbar-thumb {
    background: #8ed8e8;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: #00a6c7;
}


/* =========================================================
   MOBILE RESPONSIVE DESIGN
   ========================================================= */

@media (max-width: 768px) {

    .hero {
        padding: 28px 22px;
        border-radius: 18px;
    }

    .hero h1 {
        font-size: 2rem;
    }

    .hero p {
        font-size: 1rem;
    }

    .hero::after {
        display: none;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0 10px;
        font-size: 0.8rem;
    }

}

</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# GEMINI HELPERS
# ----------------------------------------------------------------------------

class GeminiError(Exception):
    """Raised with a beginner-friendly message when Gemini fails."""


@st.cache_resource
def get_client(key: str):
    """Create the Gemini client once and reuse it."""
    return genai.Client(api_key=key)


def friendly_error(err: Exception) -> str:
    """Convert raw API errors into simple messages."""
    msg = str(err).lower()

    if "api key" in msg or "api_key" in msg or "permission" in msg or "401" in msg or "403" in msg:
        return "Your Gemini API key looks invalid. Please check the .env file."

    if "404" in msg or "not found" in msg:
        return f"Model '{MODEL_NAME}' was not found. Change MODEL_NAME at the top of app.py."

    if "429" in msg or "quota" in msg or "resource_exhausted" in msg:
        return "Gemini quota/rate limit reached. Wait a minute and try again."

    if "connect" in msg or "timeout" in msg or "network" in msg:
        return "Network problem while contacting Gemini. Check your internet connection."

    return f"Gemini request failed: {err}"


def ask_gemini(contents, system=None, json_mode=False) -> str:
    """Send a request to Gemini (2 attempts) and return the response text."""

    client = get_client(API_KEY)

    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=0.7,
        response_mime_type="application/json" if json_mode else None,
    )

    last_error = None

    for _ in range(2):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config
            )

            if response.text:
                return response.text

            last_error = ValueError("Gemini returned an empty response.")

        except Exception as e:
            last_error = e

        time.sleep(1.5)

    raise GeminiError(friendly_error(last_error))


def parse_json(text: str) -> dict:
    """Parse JSON from the model, tolerating markdown fences or extra text."""

    text = text.strip().replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")

        if start != -1 and end > start:
            return json.loads(text[start:end + 1])

        raise


def num(value) -> float:
    """Safely convert any value to a number."""

    try:
        return float(value)

    except (TypeError, ValueError):
        return 0.0


# ----------------------------------------------------------------------------
# TRIP GENERATION
# ----------------------------------------------------------------------------

def build_prompt(t: dict) -> str:

    return f"""
You are an expert travel planner. Plan a trip using these details:
- Destination: {t['destination']}
- Days: {t['days']}
- Total budget for the whole group: {CURRENCY}{t['budget']:,.0f} (INR)
- Travelers: {t['travelers']} ({t['travel_type']})
- Interests: {', '.join(t['interests'])}
- Preferred activities: {t['activities'] or 'No specific preference'}
- Accommodation preference: {t['accommodation']}
- Food preference: {t['food_pref']}

Return ONLY valid JSON (no markdown) in exactly this structure:

{{
  "overview": "2-3 sentence summary of the destination",

  "places": [
    {{
      "name": "Real place name",
      "description": "1-2 sentences",
      "category": "e.g. Historical"
    }}
  ],

  "itinerary": [
    {{
      "day": 1,
      "theme": "short title",
      "morning": "place + short note",
      "afternoon": "place + short note",
      "evening": "place + short note",
      "food_suggestion": "what/where to eat",
      "approx_cost": 0
    }}
  ],

  "budget": {{
    "accommodation": 0,
    "food": 0,
    "local_transport": 0,
    "entry_tickets": 0,
    "activities": 0,
    "other": 0
  }},

  "food": {{
    "dishes": [
      {{
        "name": "dish",
        "description": "short"
      }}
    ],
    "places": [
      {{
        "name": "restaurant or food area",
        "known_for": "short",
        "approx_cost_per_person": 0
      }}
    ]
  }},

  "transport": {{
    "options": [
      "local transport option with approx fare"
    ],
    "suggested_modes": "best way to move around",
    "route_info": "general route/travel info, how to reach the destination",
    "tips": [
      "short tip"
    ]
  }}
}}

Rules:
- give 6 to 8 real places
- the itinerary MUST have exactly {t['days']} entries
- all money values are numbers in INR for the WHOLE group
- respect the food preference
- keep every budget number realistic and in total close to the user's budget
""".strip()


def validate_inputs(destination, days, budget, travelers, interests) -> list:
    """Return a list of error messages (empty list = valid)."""

    errors = []

    if not destination.strip():
        errors.append("Please enter a destination.")

    elif len(destination.strip()) < 2 or not any(c.isalpha() for c in destination):
        errors.append("Destination must contain valid letters (e.g. Hyderabad).")

    if days < 1 or days > 14:
        errors.append("Number of days must be between 1 and 14.")

    if budget < 500:
        errors.append(f"Budget must be at least {CURRENCY}500.")

    if travelers < 1:
        errors.append("At least 1 traveler is required.")

    if not interests:
        errors.append("Please select at least one interest.")

    return errors


@st.cache_data(show_spinner=False, ttl=86400)
def geocode(query: str):
    """Return (lat, lon) for a place name using Geopy, or None if not found."""

    try:
        geolocator = Nominatim(
            user_agent="ai_travel_assistant_college_project"
        )

        location = geolocator.geocode(
            query,
            timeout=10
        )

        return (location.latitude, location.longitude) if location else None

    except Exception:
        return None


def locate_places(destination: str, places: list) -> list:
    """Add coordinates to each recommended place (best effort)."""

    located = []

    for p in places[:8]:

        coords = geocode(
            f"{p.get('name', '')}, {destination}"
        )

        time.sleep(1)

        if coords:
            located.append({
                **p,
                "lat": coords[0],
                "lon": coords[1]
            })

    return located


def distance_table(located: list) -> pd.DataFrame:
    """Straight-line distance between consecutive recommended places."""

    rows = []

    for a, b in zip(located, located[1:]):

        km = geodesic(
            (a["lat"], a["lon"]),
            (b["lat"], b["lon"])
        ).km

        rows.append({
            "From": a["name"],
            "To": b["name"],
            "Approx. distance (km)": round(km, 1)
        })

    return pd.DataFrame(rows)


def generate_trip(trip: dict):
    """Call Gemini, then use Geopy to locate the destination and places."""

    plan = parse_json(
        ask_gemini(
            build_prompt(trip),
            json_mode=True
        )
    )

    dest_coords = geocode(trip["destination"])

    located = (
        locate_places(
            trip["destination"],
            plan.get("places", [])
        )
        if dest_coords
        else []
    )

    return plan, dest_coords, located


# ----------------------------------------------------------------------------
# UI SECTIONS
# ----------------------------------------------------------------------------

def render_overview(plan):

    st.subheader("🗺️ Recommended Places")

    if plan.get("overview"):
        st.info(plan["overview"])

    cols = st.columns(2)

    for i, p in enumerate(plan.get("places", [])):

        with cols[i % 2].container(border=True):

            st.markdown(
                f"**📍 {p.get('name', 'Place')}**  ·  "
                f"_{p.get('category', '')}_"
            )

            st.write(
                p.get("description", "")
            )


def render_itinerary(plan):

    st.subheader("📅 Day-wise Itinerary")

    for d in plan.get("itinerary", []):

        with st.container(border=True):

            st.markdown(
                f"### Day {d.get('day', '')}: "
                f"{d.get('theme', '')}"
            )

            st.markdown(
                f"🌅 **Morning:** {d.get('morning', '-')}"
            )

            st.markdown(
                f"☀️ **Afternoon:** {d.get('afternoon', '-')}"
            )

            st.markdown(
                f"🌇 **Evening:** {d.get('evening', '-')}"
            )

            st.markdown(
                f"🍽️ **Food:** {d.get('food_suggestion', '-')}"
            )

            st.markdown(
                f"💵 **Approx. cost:** "
                f"{CURRENCY}{num(d.get('approx_cost')):,.0f}"
            )

    st.caption(DISCLAIMER)


def render_budget(plan, trip):

    st.subheader("💰 Budget Estimate")

    budget = plan.get("budget", {})

    df = pd.DataFrame({
        "Category": [
            k.replace("_", " ").title()
            for k in BUDGET_KEYS
        ],

        f"Estimated cost ({CURRENCY})": [
            num(budget.get(k))
            for k in BUDGET_KEYS
        ],
    })

    total = df.iloc[:, 1].sum()

    diff = trip["budget"] - total

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Your budget",
        f"{CURRENCY}{trip['budget']:,.0f}"
    )

    c2.metric(
        "Estimated total",
        f"{CURRENCY}{total:,.0f}"
    )

    c3.metric(
        "Difference",
        f"{CURRENCY}{abs(diff):,.0f}",
        "Under budget" if diff >= 0 else "Over budget",
        delta_color="normal" if diff >= 0 else "inverse"
    )

    if diff >= 0:

        st.success(
            "✅ The estimated cost fits within your budget."
        )

    else:

        st.warning(
            "⚠️ The estimated cost is above your budget. "
            "Consider fewer days or cheaper stays."
        )

    left, right = st.columns(2)

    left.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    right.bar_chart(
        df.set_index("Category")
    )

    st.caption(DISCLAIMER)


def render_food(plan):

    st.subheader("🍴 Food Recommendations")

    food = plan.get("food", {})

    left, right = st.columns(2)

    with left:

        st.markdown("#### 🍛 Popular Dishes")

        for dish in food.get("dishes", []):

            with st.container(border=True):

                st.markdown(
                    f"**{dish.get('name', '')}**"
                )

                st.write(
                    dish.get("description", "")
                )

    with right:

        st.markdown("#### 🏪 Restaurants / Food Areas")

        for r in food.get("places", []):

            with st.container(border=True):

                st.markdown(
                    f"**{r.get('name', '')}**"
                )

                st.write(
                    r.get("known_for", "")
                )

                st.caption(
                    f"Approx. "
                    f"{CURRENCY}"
                    f"{num(r.get('approx_cost_per_person')):,.0f}"
                    f" per person"
                )

    st.caption(DISCLAIMER)


def render_map(plan, trip, dest_coords, located):

    st.subheader("🧭 Map & Travel Information")

    if not dest_coords:

        st.warning(
            "Could not find map coordinates for this destination. "
            "The rest of the plan still works."
        )

    else:

        m = folium.Map(
            location=dest_coords,
            zoom_start=12
        )

        folium.Marker(
            dest_coords,
            tooltip=trip["destination"],
            popup=trip["destination"],
            icon=folium.Icon(
                color="red",
                icon="home"
            )
        ).add_to(m)

        for p in located:

            folium.Marker(
                (p["lat"], p["lon"]),
                tooltip=p["name"],
                popup=(
                    f"<b>{p['name']}</b><br>"
                    f"{p.get('description', '')}"
                ),
                icon=folium.Icon(
                    color="blue",
                    icon="info-sign"
                )
            ).add_to(m)

        st_folium(
            m,
            height=450,
            use_container_width=True,
            returned_objects=[]
        )

        if not located:

            st.info(
                "Exact coordinates of individual places were not found; "
                "showing the destination only."
            )

    # Travel information from Gemini

    t = plan.get("transport", {})

    st.markdown("#### 🚗 Transportation")

    st.write(
        f"**Suggested modes:** "
        f"{t.get('suggested_modes', '-')}"
    )

    st.write(
        f"**Route / travel info:** "
        f"{t.get('route_info', '-')}"
    )

    for option in t.get("options", []):

        st.markdown(
            f"- 🚌 {option}"
        )

    for tip in t.get("tips", []):

        st.markdown(
            f"- 💡 {tip}"
        )

    if len(located) > 1:

        st.markdown(
            "#### 📏 Approx. straight-line distances (Geopy)"
        )

        st.dataframe(
            distance_table(located),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Straight-line distances only; "
            "real road distance will be longer."
        )

    st.caption(DISCLAIMER)


def render_chatbot():

    st.subheader("🤖 AI Travel Chatbot")

    st.caption(
        "Ask anything: best places, food, budget, packing, "
        "family-friendliness, Day 2 plans..."
    )

    if "chat" not in st.session_state:
        st.session_state.chat = []

    trip = st.session_state.get("trip")
    plan = st.session_state.get("plan")

    context = (
        "No trip generated yet. "
        "Answer general travel questions."
    )

    if trip and plan:

        context = (
            f"The user's trip: "
            f"{json.dumps(trip, default=str)}. "
            f"Generated plan: "
            f"{json.dumps(plan)[:6000]}"
        )

    system = (
        "You are a friendly, concise AI travel assistant. "
        "Answer only travel-related questions. "
        "Mention that prices and timings are estimates. "
        "Context: " + context
    )

    for msg in st.session_state.chat:

        with st.chat_message(msg["role"]):

            st.markdown(
                msg["content"]
            )

    question = st.chat_input(
        "Type your travel question here..."
    )

    if question:

        st.session_state.chat.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):

            st.markdown(question)

        contents = [
            {
                "role": (
                    "user"
                    if m["role"] == "user"
                    else "model"
                ),
                "parts": [
                    {
                        "text": m["content"]
                    }
                ]
            }

            for m in st.session_state.chat
        ]

        with st.chat_message("assistant"):

            try:

                with st.spinner("Thinking..."):

                    answer = ask_gemini(
                        contents,
                        system=system
                    )

            except GeminiError as e:

                answer = (
                    f"⚠️ Sorry, I couldn't answer right now. "
                    f"{e}"
                )

            st.markdown(answer)

        st.session_state.chat.append({
            "role": "assistant",
            "content": answer
        })

    if st.session_state.chat and st.button("🗑️ Clear chat"):

        st.session_state.chat = []

        st.rerun()


def trip_form():
    """Render the input form and return the trip dict when submitted and valid."""

    with st.form("trip_form"):

        c1, c2 = st.columns(2)

        destination = c1.text_input(
            "📍 Destination",
            placeholder="e.g. Hyderabad"
        )

        budget = c2.number_input(
            f"💰 Total budget ({CURRENCY})",
            min_value=0,
            value=10000,
            step=500
        )

        c3, c4, c5 = st.columns(3)

        days = c3.number_input(
            "📆 Number of days",
            min_value=1,
            max_value=14,
            value=3
        )

        travelers = c4.number_input(
            "👥 Travelers",
            min_value=1,
            max_value=20,
            value=2
        )

        travel_type = c5.selectbox(
            "🧳 Travel type",
            ["Solo", "Family", "Friends", "Couple"],
            index=2
        )

        interests = st.multiselect(
            "🎯 Interests",
            INTERESTS,
            default=["Historical places", "Food"]
        )

        activities = st.text_input(
            "🏃 Preferred activities",
            placeholder="e.g. Sightseeing and local food"
        )

        c6, c7 = st.columns(2)

        accommodation = c6.selectbox(
            "🏨 Accommodation",
            [
                "Budget (hostel/guesthouse)",
                "Mid-range hotel",
                "Luxury hotel",
                "Homestay / Airbnb"
            ],
            index=1
        )

        food_pref = c7.selectbox(
            "🥗 Food preference",
            [
                "Vegetarian",
                "Non-vegetarian",
                "Vegan",
                "No preference"
            ],
            index=3
        )

        submitted = st.form_submit_button(
            "🚀 Generate My Trip",
            use_container_width=True
        )

    if not submitted:
        return None

    errors = validate_inputs(
        destination,
        int(days),
        float(budget),
        int(travelers),
        interests
    )

    if errors:

        for e in errors:
            st.error(e)

        return None

    return {
        "destination": destination.strip(),
        "days": int(days),
        "budget": float(budget),
        "travelers": int(travelers),
        "travel_type": travel_type,
        "interests": interests,
        "activities": activities.strip(),
        "accommodation": accommodation,
        "food_pref": food_pref
    }


# ----------------------------------------------------------------------------
# MAIN APP
# ----------------------------------------------------------------------------

def main():

    with st.sidebar:

        st.title("⚙️ Settings")

        st.write(
            f"**Model:** `{MODEL_NAME}`"
        )

        st.write(
            "**API key:** " +
            ("✅ Loaded" if API_KEY else "❌ Missing")
        )

        st.markdown("---")

        st.markdown(
            "### ℹ️ About\n"
            "AI Travel Assistant plans trips using "
            "Google Gemini, Geopy and Folium.\n\n"
            "*College project demo.*"
        )

        st.caption(DISCLAIMER)

    st.markdown(
        '<div class="hero">'
        '<h1>✈️ AI Travel Assistant</h1>'
        '<p>Plan your perfect trip with Artificial Intelligence 🌍</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if not API_KEY:

        st.error(
            "🔑 GEMINI_API_KEY not found. Create a `.env` file next to "
            "app.py containing `GEMINI_API_KEY=your_api_key_here`, "
            "then restart the app."
        )

        st.stop()

    tabs = st.tabs([
        "🧳 Trip Planner",
        "📅 Itinerary",
        "💰 Budget",
        "🍴 Food",
        "🗺️ Map",
        "🤖 AI Chatbot"
    ])

    with tabs[0]:

        trip = trip_form()

        if trip:

            try:

                with st.spinner(
                    "✨ Gemini is planning your trip... "
                    "(map lookup may take a few seconds)"
                ):

                    plan, dest_coords, located = generate_trip(trip)

                st.session_state.update(
                    trip=trip,
                    plan=plan,
                    dest_coords=dest_coords,
                    located=located
                )

                st.session_state.chat = []

                st.success(
                    "✅ Trip generated! "
                    "Check the other tabs for details."
                )

                if not dest_coords:

                    st.warning(
                        "Destination not found on the map, "
                        "but your plan was generated."
                    )

            except GeminiError as e:

                st.error(
                    f"❌ {e}"
                )

            except (
                json.JSONDecodeError,
                KeyError,
                TypeError
            ):

                st.error(
                    "❌ The AI response could not be understood. "
                    "Please click Generate again."
                )

            except Exception as e:

                st.error(
                    f"❌ Unexpected error: {e}"
                )

        if st.session_state.get("plan"):

            render_overview(
                st.session_state.plan
            )

    plan = st.session_state.get("plan")
    saved_trip = st.session_state.get("trip")

    renderers = [
        (
            tabs[1],
            lambda: render_itinerary(plan)
        ),
        (
            tabs[2],
            lambda: render_budget(
                plan,
                saved_trip
            )
        ),
        (
            tabs[3],
            lambda: render_food(plan)
        ),
        (
            tabs[4],
            lambda: render_map(
                plan,
                saved_trip,
                st.session_state.get("dest_coords"),
                st.session_state.get("located", [])
            )
        ),
    ]

    for tab, render in renderers:

        with tab:

            if plan:
                render()

            else:

                st.info(
                    "👈 Generate a trip in the "
                    "**Trip Planner** tab first."
                )

    with tabs[5]:

        render_chatbot()


if __name__ == "__main__":
    main()