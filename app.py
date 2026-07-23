"""
TrekMatch AI — Streamlit front-end
==================================

Presentation-layer only. recommender.py is never imported for anything
other than its public `TrekRecommender` class and is not modified.

    recommender = TrekRecommender()
    recommendations = recommender.recommend(
        budget=budget,
        days=days,
        month=month,
        experience=experience,
    )

Expected DataFrame columns:
    Trek, Image, Price, Duration, Altitude, Distance, Grade,
    Best Time, Score, Explanation, Reasons

Run with:
    streamlit run app.py
"""

import time
import streamlit as st
from backend.recommender import TrekRecommender  # your existing, unmodified module


# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TrekMatch AI",
    page_icon="🏔",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BG_IMAGE_URL = "https://images.unsplash.com/photo-1544198365-f5d60b6d8190?q=80&w=2200&auto=format&fit=crop"
RANK_EMOJI = {0: "🥇", 1: "🥈", 2: "🥉"}


# ---------------------------------------------------------------------------
# Global CSS — full-screen fixed background, glass search panel, premium cards
# ---------------------------------------------------------------------------
def inject_css() -> None:
    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Manrope:wght@700;800&display=swap');

            :root {{
                --primary: #2563eb;
                --primary-2: #1d4ed8;
                --accent: #38bdf8;
                --glow: #60a5fa;
                --card-bg: rgba(255, 255, 255, 0.97);
                --glass-bg: rgba(13, 22, 38, 0.55);
                --glass-border: rgba(255, 255, 255, 0.16);
                --text-main: #0f172a;
                --text-muted: #55627a;
                --text-on-dark: #f5f8fc;
                --text-on-dark-muted: #aebcd1;
                --radius-lg: 24px;
                --radius-md: 16px;
                --shadow-soft: 0 12px 34px rgba(0, 0, 0, 0.38);
                --shadow-hover: 0 22px 50px rgba(0, 0, 0, 0.5);
                --shadow-glow: 0 0 0 1px rgba(96,165,250,0.35), 0 12px 40px rgba(37,99,235,0.28);
            }}

            html, body, [class*="css"] {{
                font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            }}

            /* ---------- Full-screen fixed background image with overlay ---------- */
            .stApp {{
                background-image:
                    linear-gradient(180deg, rgba(4,9,18,0.72) 0%, rgba(4,9,18,0.62) 35%, rgba(4,9,18,0.88) 100%),
                    url('{BG_IMAGE_URL}');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                background-repeat: no-repeat;
                color: var(--text-on-dark);
            }}
            [data-testid="stHeader"] {{ background: transparent; }}
            #MainMenu, footer {{ visibility: hidden; }}

            .block-container {{
                padding-top: 3.2rem;
                padding-bottom: 3rem;
                max-width: 1180px;
            }}

            /* ---------- Page title block ---------- */
            .app-heading {{
                text-align: center;
                margin-bottom: 2.1rem;
                animation: fadeInUp 0.8s ease-out;
            }}
            .app-heading .eyebrow {{
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                color: var(--accent);
                background: rgba(56,189,248,0.12);
                border: 1px solid rgba(56,189,248,0.3);
                padding: 0.35rem 0.9rem;
                border-radius: 999px;
                margin-bottom: 1rem;
            }}
            .app-heading h1 {{
                font-family: 'Manrope', 'Inter', sans-serif;
                font-size: clamp(2.2rem, 4.4vw, 3.1rem);
                font-weight: 800;
                letter-spacing: -0.02em;
                margin: 0 0 0.65rem 0;
                text-shadow: 0 4px 24px rgba(0,0,0,0.45);
            }}
            .app-heading .sub {{
                font-size: clamp(1rem, 1.6vw, 1.15rem);
                font-weight: 500;
                color: var(--text-on-dark-muted);
                max-width: 620px;
                margin: 0 auto;
                line-height: 1.6;
            }}

            /* ---------- Floating glassmorphism search panel ---------- */
            .st-key-search-panel {{
                animation: fadeInUp 0.9s ease-out 0.1s both;
                margin-bottom: 0.5rem;
            }}
            .st-key-search-panel > div {{
                background: var(--glass-bg) !important;
                backdrop-filter: blur(24px) saturate(150%);
                -webkit-backdrop-filter: blur(24px) saturate(150%);
                border: 1px solid var(--glass-border) !important;
                border-radius: var(--radius-lg) !important;
                box-shadow: var(--shadow-glow);
                padding: 1.9rem 2.1rem !important;
            }}
            .st-key-search-panel label,
            .st-key-search-panel p,
            .st-key-search-panel span {{
                color: var(--text-on-dark) !important;
                font-weight: 600 !important;
            }}
            .st-key-search-panel .stSlider [data-baseweb="slider"] > div > div {{
                background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
            }}
            .st-key-search-panel div[data-baseweb="select"] > div {{
                background: rgba(255,255,255,0.07) !important;
                border-color: rgba(255,255,255,0.22) !important;
                border-radius: 12px !important;
                color: var(--text-on-dark) !important;
                transition: border-color 0.2s ease, box-shadow 0.2s ease;
            }}
            .st-key-search-panel div[data-baseweb="select"]:hover > div {{
                border-color: var(--accent) !important;
                box-shadow: 0 0 0 3px rgba(56,189,248,0.15);
            }}
            .btn-spacer {{ height: 1.75rem; }}

            div[data-baseweb="popover"] ul {{ background-color: #0d1626 !important; }}
            div[data-baseweb="popover"] li {{ color: var(--text-on-dark) !important; }}
            div[data-baseweb="popover"] li:hover {{ background-color: rgba(56,189,248,0.18) !important; }}

            /* Primary CTA button — glowing */
            .stButton > button {{
                background: linear-gradient(135deg, var(--primary), var(--primary-2));
                color: #ffffff;
                border: none;
                border-radius: 13px;
                padding: 0.72rem 1.2rem;
                font-size: 1rem;
                font-weight: 700;
                width: 100%;
                box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
                transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
            }}
            .stButton > button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 0 0 4px rgba(56,189,248,0.22), 0 12px 30px rgba(56, 189, 248, 0.45);
                color: #ffffff;
                border: none;
            }}
            .stButton > button:active {{ transform: translateY(0); }}

            /* ---------- Matches label ---------- */
            .matches-label {{
                text-align: center;
                color: var(--text-on-dark);
                font-weight: 800;
                letter-spacing: 0.02em;
                font-size: 1.5rem;
                margin: 3rem 0 0.35rem 0;
                animation: fadeInUp 0.7s ease-out;
            }}
            .matches-sub {{
                text-align: center;
                color: var(--text-on-dark-muted);
                font-size: 0.95rem;
                margin-bottom: 1.9rem;
            }}

            /* ---------- Recommendation cards (native Streamlit layout) ----------
               One single card per trek — no nested white boxes. Image bleeds
               to the card edges (rounded top corners only, via overflow:hidden
               on the card + a negative-margin image). Everything else is
               plain typography and dividers, tightly spaced, with colour used
               only as accents (never as little background panels). */

            [class*="st-key-rec-card-"] {{
                animation: fadeInUp 0.6s ease-out both;
            }}
            .st-key-rec-card-0 {{ animation-delay: 0.05s; }}
            .st-key-rec-card-1 {{ animation-delay: 0.2s; }}
            .st-key-rec-card-2 {{ animation-delay: 0.35s; }}

            [class*="st-key-rec-card-"] > div {{
                background-color: var(--card-bg) !important;
                border: 1px solid rgba(255,255,255,0.6) !important;
                border-radius: var(--radius-lg) !important;
                box-shadow: var(--shadow-soft);
                padding: 1.15rem 1.35rem 1.35rem 1.35rem !important;
                overflow: hidden;
                transition: transform 0.25s ease-in-out, box-shadow 0.25s ease-in-out;
            }}
            [class*="st-key-rec-card-"] > div:hover {{
                transform: translateY(-6px);
                box-shadow: var(--shadow-hover);
            }}

            /* Tighter, single-column rhythm so the card reads as one piece,
               not a stack of separated widgets */
            [class*="st-key-rec-card-"] [data-testid="stVerticalBlock"] {{
                gap: 0.5rem;
            }}

            /* Trek image — bled out to the card's edges (the negative margin
               exactly cancels the card's own padding), so overflow:hidden on
               the card clips it to rounded corners at the top only */
            [class*="st-key-rec-card-"] [data-testid="stImage"] {{
                margin: -1.15rem -1.35rem 0.9rem -1.35rem;
                width: calc(100% + 2.7rem);
            }}
            [class*="st-key-rec-card-"] [data-testid="stImage"] img {{
                height: 250px;
                width: 100%;
                object-fit: cover;
                display: block;
                transition: transform 0.4s ease;
            }}
            [class*="st-key-rec-card-"]:hover [data-testid="stImage"] img {{
                transform: scale(1.05);
            }}

            /* Trek name heading (rendered via st.markdown "### ...") */
            [class*="st-key-rec-card-"] h3 {{
                font-family: 'Manrope', 'Inter', sans-serif;
                font-size: 1.34rem;
                font-weight: 800;
                color: var(--text-main);
                margin: 0.1rem 0 0.1rem 0;
                padding: 0;
                line-height: 1.25;
            }}

            /* Match line — large percentage, small qualitative label, no pill/box */
            .match-pct-text {{
                font-family: 'Manrope', 'Inter', sans-serif;
                font-size: 1.15rem;
                font-weight: 800;
                background: linear-gradient(135deg, var(--primary-2), var(--accent));
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }}
            .match-label-text {{
                font-weight: 600;
                font-size: 0.88rem;
                color: var(--text-muted);
                margin-left: 0.35rem;
            }}

            /* Statistics — plain two-column typography, no chip/box backgrounds */
            .stat-line {{
                font-size: 0.98rem;
                font-weight: 700;
                color: var(--text-main);
            }}
            .stat-line-muted {{
                font-size: 0.92rem;
                font-weight: 600;
                color: var(--text-muted);
            }}

            /* Divider lines between sections */
            [class*="st-key-rec-card-"] hr {{
                margin: 0.6rem 0;
                border-color: #e7ebf1;
            }}

            /* AI preview — darker, clearly readable text (not the muted grey) */
            [class*="st-key-rec-card-"] [data-testid="stCaptionContainer"] p {{
                color: #3d4a63;
                font-size: 0.93rem;
                font-weight: 500;
                line-height: 1.5;
            }}

            [class*="st-key-rec-card-"] [data-testid="stExpander"] {{
                border: none !important;
                border-radius: 10px !important;
                background: transparent !important;
            }}
            [class*="st-key-rec-card-"] [data-testid="stExpander"] summary {{
                font-weight: 700;
                color: var(--primary);
                font-size: 0.8rem;
                background: #eff6ff;
                border: 1px solid #dbeafe;
                border-radius: 10px;
                padding: 0.58rem 0.95rem;
                transition: background 0.2s ease, box-shadow 0.2s ease;
            }}
            [class*="st-key-rec-card-"] [data-testid="stExpander"] summary:hover {{
                background: #dbeafe;
                box-shadow: 0 0 0 3px rgba(37,99,235,0.12);
            }}
            [class*="st-key-rec-card-"] [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
                padding: 0.9rem 0.1rem 0.2rem 0.1rem;
            }}

            /* ---------- Footer ---------- */
            .app-footer {{
                text-align: center;
                color: var(--text-on-dark-muted);
                font-size: 0.85rem;
                margin-top: 3.5rem;
                padding-bottom: 1.5rem;
                letter-spacing: 0.02em;
            }}

            /* ---------- Animations ---------- */
            @keyframes fadeInUp {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}

            /* ---------- Responsiveness ---------- */
            @media (max-width: 768px) {{
                .st-key-search-panel > div {{ padding: 1.3rem !important; }}
                [class*="st-key-rec-card-"] [data-testid="stImage"] img {{ height: 200px; }}
                [class*="st-key-rec-card-"] h3 {{ font-size: 1.15rem; }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Heading — replaces the old hero banner. Background now lives on .stApp.
# ---------------------------------------------------------------------------
def render_heading() -> None:
    st.markdown(
        """
        <div class="app-heading">
            <div class="eyebrow">✨ AI-Powered Trek Discovery</div>
            <h1>🏔 TrekMatch AI</h1>
            <div class="sub">
                Discover your perfect Himalayan adventure using AI-powered recommendations
                tailored to your experience, budget and schedule.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Floating glassmorphism search panel — one row on desktop
# ---------------------------------------------------------------------------
def render_search_panel():
    """Renders the floating glass search bar and returns the collected form values."""
    with st.container(border=True, key="search-panel"):
        cols = st.columns([1.3, 1.6, 1.0, 1.3, 1.1], gap="medium")

        with cols[0]:
            experience = st.selectbox(
                "Experience",
                options=["First Trek", "Beginner", "Intermediate", "Experienced"],
            )
        with cols[1]:
            budget = st.slider(
                "Budget (₹)", min_value=5000, max_value=25000,
                value=12000, step=500, format="₹%d",
            )
        with cols[2]:
            days = st.slider("Days", min_value=3, max_value=15, value=6)
        with cols[3]:
            month = st.selectbox(
                "Month",
                options=[
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December",
                ],
                index=10,  # November default
            )
        with cols[4]:
            st.markdown('<div class="btn-spacer"></div>', unsafe_allow_html=True)
            submitted = st.button("✨ Find My Trek", use_container_width=True)

    return submitted, budget, days, month, experience


# ---------------------------------------------------------------------------
# Helper: robust match-percentage calculation
# ---------------------------------------------------------------------------
def compute_match_percent(raw_score) -> int:
    """
    Normalize a recommender Score into a 0-100 integer match percentage.

    Handles three common conventions without guessing based on the *output*
    of a prior calculation:
      - 0.0–1.0 fractional score      -> multiply by 100
      - 0–100 score already a percent -> use as-is
      - anything else                 -> clamp into [0, 100]
    """
    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        return 0

    if score < 0:
        return 0
    if score <= 1.0:
        pct = score * 100
    elif score <= 100.0:
        pct = score
    else:
        pct = 100.0

    return int(round(max(0.0, min(100.0, pct))))


# ---------------------------------------------------------------------------
# Helper: short, travel-style AI preview (NOT the raw explanation text)
# ---------------------------------------------------------------------------
def generate_ai_preview(trek) -> str:
    """
    Builds a short (<=2 line, ~80 char) travel-style teaser based on the
    trek's difficulty grade -- distinct from the full AI explanation, which
    stays inside the "View Full AI Analysis" expander.
    """
    grade = str(trek.get("Grade", "")).strip().lower()

    if "difficult" in grade and "moderate" in grade:
        return "A rewarding step up for trekkers ready to push past moderate terrain."
    if "difficult" in grade:
        return "One of the best high-altitude expeditions for experienced trekkers."
    if "moderate" in grade:
        return "Excellent choice if you're looking for snow without extreme difficulty."
    if "easy" in grade:
        return "Perfect for first-time Himalayan trekkers."
    return "A well-matched Himalayan adventure for your travel plans."


# ---------------------------------------------------------------------------
# Helper: colour-coded difficulty badge
# ---------------------------------------------------------------------------
def get_difficulty_badge(grade) -> tuple:
    """Returns (emoji, label, css_class) for a Grade value."""
    g = str(grade).strip().lower()

    if "difficult" in g and "moderate" in g:
        return "🟠", "Moderate–Difficult", "diff-modhard"
    if "difficult" in g:
        return "🔴", "Difficult", "diff-hard"
    if "moderate" in g:
        return "🟡", "Moderate", "diff-moderate"
    if "easy" in g:
        return "🟢", "Easy", "diff-easy"
    return "⚪", str(grade), "diff-unknown"


# ---------------------------------------------------------------------------
# Helper: qualitative label shown under the match percentage
# ---------------------------------------------------------------------------
def get_match_label(match_pct: int) -> str:
    if match_pct >= 90:
        return "Excellent Match"
    if match_pct >= 75:
        return "Highly Recommended"
    if match_pct >= 60:
        return "Good Match"
    return "Fair Match"


# ---------------------------------------------------------------------------
# Recommendation card — rebuilt as one premium travel card. Native Streamlit
# widgets only (container, columns, image, markdown, caption, expander) —
# no st.metric (its boxed KPI look was the "dashboard" feel), no empty
# placeholder elements, and no per-section wrapper panels. CSS above only
# adds colour/typography/spacing to these native elements.
# ---------------------------------------------------------------------------
def render_recommendation_card(trek, rank: int) -> None:
    """Renders a single trek recommendation as one unified travel card."""
    medal = RANK_EMOJI.get(rank, "🏅")
    match_pct = compute_match_percent(trek["Score"])
    match_label = get_match_label(match_pct)
    diff_emoji, diff_label, _ = get_difficulty_badge(trek["Grade"])
    preview = generate_ai_preview(trek)

    with st.container(border=True, key=f"rec-card-{rank}"):
        # Large trek image — bleeds to the card edges via CSS
        st.image(trek["Image"], use_container_width=True)

        # Trek name
        st.markdown(f"### {medal} {trek['Trek']}")

        # Match percentage + qualitative label, plain typography (no pill/box)
        st.markdown(
            f'<span class="match-pct-text">⭐ {match_pct}% Match</span>'
            f'<span class="match-label-text">{match_label}</span>',
            unsafe_allow_html=True,
        )

        st.divider()

        # Statistics — clean two-column plain text, then best season on its
        # own line, exactly like a destination card, not a KPI dashboard
        left, right = st.columns(2)
        with left:
            st.markdown(f'<span class="stat-line">💰 ₹{int(trek["Price"]):,}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="stat-line">⛰️ {int(trek["Altitude"]):,} ft</span>', unsafe_allow_html=True)
        with right:
            st.markdown(f'<span class="stat-line">📅 {trek["Duration"]} Days</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="stat-line">{diff_emoji} {diff_label}</span>', unsafe_allow_html=True)
        st.markdown(f'<span class="stat-line-muted">🗓 {trek["Best Time"]}</span>', unsafe_allow_html=True)

        st.divider()

        # Short travel-style AI preview — darker, readable text
        st.caption(preview)

        # Full AI analysis, at the natural end of the card
        with st.expander("▼ View Full AI Analysis"):
            st.markdown("**🤖 Why we recommended this trek**")
            # Rendered via st.markdown (not raw HTML) so bold text, bullet
            # lists, and spacing in the explanation render correctly.
            st.markdown(trek["Explanation"])

            st.markdown("**Why it matches you**")
            reasons = trek.get("Reasons", [])
            if isinstance(reasons, str):
                reasons = [r.strip() for r in reasons.split(",") if r.strip()]
            for reason in reasons:
                st.markdown(f"✔ {reason}")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
def render_footer() -> None:
    st.markdown('<div class="app-footer">🏔 Powered by TrekMatch AI &nbsp;·&nbsp; AI-crafted Himalayan itineraries</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main app flow
# ---------------------------------------------------------------------------
def main() -> None:
    inject_css()
    render_heading()

    submitted, budget, days, month, experience = render_search_panel()

    if submitted:
        with st.spinner("🧭 Analyzing routes, weather windows and altitude profiles..."):
            time.sleep(1)
            recommender = TrekRecommender()
            recommendations = recommender.recommend(
                budget=budget,
                days=days,
                month=month,
                experience=experience,
            )

        if recommendations is None or len(recommendations) == 0:
            st.warning("No matching treks found. Try adjusting your preferences.")
        else:
            st.markdown('<div class="matches-label">🎯 Your Top Matches</div>', unsafe_allow_html=True)
            st.markdown('<div class="matches-sub">Ranked by AI based on your budget, timing and experience level</div>', unsafe_allow_html=True)

            top_matches = recommendations.head(3).reset_index(drop=True)

            # Side-by-side, equal-width columns — the cards themselves ARE
            # the comparison, so no separate dataframe/table is rendered.
            cols = st.columns(3, gap="large")
            for rank in range(len(top_matches)):
                with cols[rank]:
                    render_recommendation_card(top_matches.iloc[rank], rank)

    render_footer()


if __name__ == "__main__":
    main()
    