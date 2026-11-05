# ============================================================
# MATCH POINT ANALYTICS
# Professional Tennis Analytics Dashboard
# Python + Streamlit + MySQL + Plotly + SportRadar
# ============================================================

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# 1. CONFIGURATION
# ------------------------------------------------------------

st.set_page_config(
    page_title="Match Point | Tennis Intelligence",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#0B1220"
PANEL = "#121E30"
GREEN = "#C5F36B"
MUTED = "#93A4B8"
BORDER = "#26374D"


# ------------------------------------------------------------
# 2. CUSTOM PROFESSIONAL DESIGN
# ------------------------------------------------------------

st.markdown(
    f"""
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap'
    );

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
    }}

    .stApp {{
        background: {NAVY};
        color: #F4F7FB;
    }}

    [data-testid="stSidebar"] {{
        background: #0E1929;
        border-right: 1px solid {BORDER};
    }}

    [data-testid="stSidebar"] * {{
        color: #E6EDF5;
    }}

    .block-container {{
        max-width: 1550px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3 {{
        color: #F4F7FB !important;
        letter-spacing: -0.5px;
    }}

    p, label {{
        color: #D5DFEA;
    }}

    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, #17263A, #111B2B);
        border: 1px solid {BORDER};
        border-radius: 15px;
        padding: 20px 18px;
        min-height: 120px;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {MUTED};
        font-size: 0.9rem;
    }}

    div[data-testid="stMetricValue"] {{
        color: {GREEN};
        font-size: 1.8rem;
        font-weight: 700;
    }}

    .hero {{
        padding: 30px;
        border: 1px solid #354B5F;
        border-radius: 20px;
        background:
            radial-gradient(
                circle at 90% 10%,
                #30472D 0,
                transparent 30%
            ),
            linear-gradient(120deg, #15283D, #101A29);
        margin-bottom: 24px;
    }}

    .eyebrow {{
        color: {GREEN};
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}

    .hero h1 {{
        font-size: clamp(2rem, 4vw, 3.2rem);
        margin: 12px 0 8px 0;
    }}

    .hero p {{
        color: #B5C5D6;
        max-width: 700px;
        line-height: 1.7;
    }}

    .section-label {{
        color: {GREEN};
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }}

    .info-panel {{
        background: {PANEL};
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 12px;
        overflow: hidden;
    }}

    div.stButton > button {{
        border-radius: 9px;
        font-weight: 600;
    }}

    hr {{
        border-color: {BORDER};
    }}

    footer {{
        visibility: hidden;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------
# 3. DATABASE CONNECTION
# ------------------------------------------------------------

def get_connection():
    """Connect to the SQLite database stored with this project."""
    db_path = Path(__file__).resolve().parent / "data" / "tennis_analytics.db"

    if not db_path.exists():
        raise FileNotFoundError(
            f"SQLite database file not found: {db_path}. "
            "Make sure data/tennis_analytics.db is included in the GitHub repository."
        )

    return sqlite3.connect(
        str(db_path),
        timeout=10,
        check_same_thread=False,
    )


@st.cache_data(ttl=60, show_spinner=False)
def read_query(query, params=()):
    """Run a read-only SQL query and return a DataFrame."""
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [item[0] for item in cursor.description]
        return pd.DataFrame(rows, columns=columns)
    finally:
        cursor.close()
        connection.close()


def safe_number(value):
    """Format a metric without showing NaN."""
    if pd.isna(value):
        return "N/A"

    return f"{int(value):,}"


def clean_numeric(df, columns):
    """Convert selected columns to numeric where possible."""
    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column], errors="coerce"
            )

    return df


def style_chart(fig, height=360):
    """Apply the shared dashboard chart theme."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="DM Sans, sans-serif",
            color="#DCE5EF",
            size=12,
        ),
        title_font=dict(size=17, color="#F4F7FB"),
        height=height,
        margin=dict(l=15, r=15, t=55, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    fig.update_xaxes(
        gridcolor="#26374D",
        zerolinecolor="#26374D",
    )
    fig.update_yaxes(
        gridcolor="#26374D",
        zerolinecolor="#26374D",
    )

    return fig


def show_download(df, filename, label="Download CSV"):
    """Add a CSV download button."""
    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=f"download_{filename}",
    )


# ------------------------------------------------------------
# 4. LOAD THE DATA
# ------------------------------------------------------------

try:
    with st.spinner("Connecting to the tennis analytics database..."):

        competitions = read_query("""
            SELECT
                c.competition_id,
                c.competition_name,
                c.competition_type,
                c.gender,
                c.category_id,
                cat.category_name
            FROM competitions c
            LEFT JOIN categories cat
                ON c.category_id = cat.category_id
        """)

        venues = read_query("""
            SELECT
                v.venue_id,
                v.venue_name,
                v.city_name,
                v.city_id,
                v.country_name,
                v.country_code,
                v.timezone,
                v.complex_id,
                c.complex_name
            FROM venues v
            LEFT JOIN complexes c
                ON v.complex_id = c.complex_id
        """)

        rankings = read_query("""
            SELECT
                cr.ranking_id,
                cr.rank_position,
                cr.movement,
                cr.points,
                cr.competitions_played,
                cr.ranking_type_id,
                cr.ranking_type_name,
                cr.ranking_year,
                cr.ranking_week,
                cr.gender,
                cr.competitor_id,
                c.competitor_name,
                c.country,
                c.country_code,
                c.abbreviation
            FROM competitor_rankings cr
            LEFT JOIN competitors c
                ON cr.competitor_id = c.competitor_id
        """)

        categories = read_query("""
            SELECT category_id, category_name
            FROM categories
        """)

        complexes = read_query("""
            SELECT complex_id, complex_name
            FROM complexes
        """)

        competitors = read_query("""
            SELECT
                competitor_id,
                competitor_name,
                country,
                country_code,
                abbreviation
            FROM competitors
        """)

except Exception as error:
    st.error("Unable to connect to the tennis analytics database.")
    st.markdown(
        "Check that data/tennis_analytics.db exists in the project and "
        "contains all six tables."
    )
    st.code(str(error))
    st.stop()


# Convert ranking fields to numeric values
rankings = clean_numeric(
    rankings,
    [
        "rank_position",
        "movement",
        "points",
        "competitions_played",
        "ranking_year",
        "ranking_week",
    ],
)


# ------------------------------------------------------------
# 5. SIDEBAR NAVIGATION
# ------------------------------------------------------------

st.sidebar.markdown(
    f"""
    <div style="padding:10px 0 22px 0;">
        <div style="font-size:30px;">🎾</div>
        <div style="font-size:21px;font-weight:800;">
            MATCH POINT
        </div>
        <div style="font-size:11px;letter-spacing:2px;color:{GREEN};">
            TENNIS INTELLIGENCE
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Rankings Lab",
        "Competitor Explorer",
        "Competition Intelligence",
        "Venue Intelligence",
        "Data Quality",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Global Filters")

gender_options = sorted(
    rankings["gender"].dropna().astype(str).unique().tolist()
)

country_options = sorted(
    rankings["country"].dropna().astype(str).unique().tolist()
)

selected_gender = st.sidebar.selectbox(
    "Ranking gender",
    ["All"] + gender_options,
)

selected_country = st.sidebar.selectbox(
    "Competitor country",
    ["All"] + country_options,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div style="font-size:12px;color:{MUTED};line-height:1.8;">
        <b style="color:{GREEN};">● DATABASE CONNECTED</b><br>
        SQLite · tennis_analytics.db<br>
        Source · SportRadar API<br>
        Cache · 60 seconds
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("↻ Refresh dashboard", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# Apply global ranking filters
filtered_rankings = rankings.copy()

if selected_gender != "All":
    filtered_rankings = filtered_rankings[
        filtered_rankings["gender"].astype(str) == selected_gender
    ]

if selected_country != "All":
    filtered_rankings = filtered_rankings[
        filtered_rankings["country"].astype(str) == selected_country
    ]


# ------------------------------------------------------------
# 6. COMMON HEADER
# ------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">SPORTS DATA · PERFORMANCE · DISCOVERY</div>
        <h1>Every ranking tells a story.</h1>
        <p>
            Your interactive tennis intelligence hub. Explore competitor
            rankings, tournament categories, venue networks and the data
            behind the sport — all powered by your SportRadar dataset.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PAGE 1 — OVERVIEW
# ============================================================

if page == "Overview":

    st.markdown(
        '<div class="section-label">YOUR TENNIS UNIVERSE</div>',
        unsafe_allow_html=True,
    )
    st.header("Analytics Overview")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Competitions", safe_number(len(competitions)))
    k2.metric("Venues", safe_number(len(venues)))
    k3.metric("Complexes", safe_number(len(complexes)))
    k4.metric(
        "Competitors",
        safe_number(competitors["competitor_id"].nunique()),
    )

    st.markdown("### The big picture")

    left, right = st.columns(2)

    with left:
        gender_data = (
            competitions["gender"]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("Gender")
            .reset_index(name="Competitions")
        )

        fig = px.pie(
            gender_data,
            names="Gender",
            values="Competitions",
            hole=0.65,
            title="Competition Distribution",
            color_discrete_sequence=[
                GREEN, "#38C8C8", "#6387D9", "#D6A7F5"
            ],
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )

    with right:
        type_data = (
            competitions["competition_type"]
            .fillna("Unknown")
            .value_counts()
            .head(12)
            .rename_axis("Competition Type")
            .reset_index(name="Count")
        )

        fig = px.bar(
            type_data.sort_values("Count"),
            x="Count",
            y="Competition Type",
            orientation="h",
            title="Competition Types",
            color="Count",
            color_continuous_scale=["#3B5940", GREEN],
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )

    st.markdown("### Ranking leaders")

    leaders = filtered_rankings.dropna(
        subset=["rank_position", "competitor_name"]
    ).sort_values("rank_position").head(10)

    if not leaders.empty:
        leader_view = leaders[
            [
                "rank_position",
                "competitor_name",
                "country",
                "points",
                "movement",
            ]
        ].copy()

        st.dataframe(
            leader_view,
            use_container_width=True,
            hide_index=True,
        )

        show_download(
            leader_view,
            "ranking_leaders.csv",
            "⬇ Download ranking leaders",
        )
    else:
        st.info("No ranking records match your selected filters.")

    st.markdown("### Venue footprint")

    venue_country = (
        venues["country_name"]
        .dropna()
        .value_counts()
        .head(10)
        .rename_axis("Country")
        .reset_index(name="Venue Count")
    )

    if not venue_country.empty:
        fig = px.bar(
            venue_country.sort_values("Venue Count"),
            x="Venue Count",
            y="Country",
            orientation="h",
            title="Countries with the Most Listed Venues",
            color="Venue Count",
            color_continuous_scale=["#3B5940", GREEN],
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )


# ============================================================
# PAGE 2 — RANKINGS LAB
# ============================================================

elif page == "Rankings Lab":

    st.markdown(
        '<div class="section-label">LEADERBOARD ANALYTICS</div>',
        unsafe_allow_html=True,
    )
    st.header("Rankings Lab")
    st.caption(
        "Search, sort, filter and export the ranking records in your database."
    )

    search = st.text_input(
        "🔎 Search competitor",
        placeholder="Start typing a competitor name...",
    )

    sort_choice = st.selectbox(
        "Sort leaderboard by",
        [
            "Best rank",
            "Most ranking points",
            "Most competitions played",
            "Largest movement value",
        ],
    )

    page_size = st.selectbox(
        "Rows per page",
        [10, 25, 50, 100],
        index=1,
    )

    data = filtered_rankings.copy()

    if search.strip():
        data = data[
            data["competitor_name"].astype(str).str.contains(
                search.strip(),
                case=False,
                na=False,
            )
        ]

    if sort_choice == "Best rank":
        data = data.sort_values("rank_position", na_position="last")
    elif sort_choice == "Most ranking points":
        data = data.sort_values("points", ascending=False, na_position="last")
    elif sort_choice == "Most competitions played":
        data = data.sort_values(
            "competitions_played", ascending=False, na_position="last"
        )
    else:
        data = data.assign(
            _movement_abs=data["movement"].abs()
        ).sort_values("_movement_abs", ascending=False, na_position="last")

    total_rows = len(data)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)

    selected_page = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
    )

    start = (selected_page - 1) * page_size
    visible = data.iloc[start:start + page_size].copy()

    st.caption(
        f"Showing {len(visible):,} of {total_rows:,} matching records · "
        f"Page {selected_page} of {total_pages}"
    )

    display_columns = [
        "rank_position",
        "competitor_name",
        "country",
        "points",
        "movement",
        "competitions_played",
        "gender",
        "ranking_type_name",
    ]

    st.dataframe(
        visible[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    show_download(
        data[display_columns],
        "tennis_rankings.csv",
        "⬇ Export all filtered rankings",
    )

    st.markdown("### Ranking points comparison")

    chart_data = data.dropna(
        subset=["competitor_name", "points"]
    ).nlargest(15, "points")

    if not chart_data.empty:
        fig = px.bar(
            chart_data.sort_values("points"),
            x="points",
            y="competitor_name",
            orientation="h",
            title="Top 15 by Ranking Points",
            color="points",
            color_continuous_scale=["#3B5940", GREEN],
            hover_data=["rank_position", "country"],
        )

        st.plotly_chart(
            style_chart(fig, height=480),
            use_container_width=True,
        )


# ============================================================
# PAGE 3 — COMPETITOR EXPLORER
# ============================================================

elif page == "Competitor Explorer":

    st.markdown(
        '<div class="section-label">COMPETITOR PROFILE</div>',
        unsafe_allow_html=True,
    )
    st.header("Competitor Explorer")
    st.caption(
        "Explore the ranking information available for an individual competitor."
    )

    player_options = sorted(
        filtered_rankings["competitor_name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not player_options:
        st.info("No competitors match the global filters.")
    else:
        selected_player = st.selectbox(
            "Choose competitor",
            player_options,
        )

        player_rows = filtered_rankings[
            filtered_rankings["competitor_name"] == selected_player
        ].copy()

        if not player_rows.empty:
            player_rows = player_rows.sort_values(
                "rank_position", na_position="last"
            )

            player = player_rows.iloc[0]

            st.markdown(
                f"""
                <div class="info-panel">
                    <div class="section-label">COMPETITOR PROFILE</div>
                    <h2 style="margin-bottom:4px;">
                        {player["competitor_name"]}
                    </h2>
                    <div style="color:{MUTED};">
                        Country: {player["country"] if pd.notna(player["country"]) else "Not available"}
                        &nbsp; · &nbsp;
                        Ranking group: {player["ranking_type_name"] if pd.notna(player["ranking_type_name"]) else "Not available"}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")

            p1, p2, p3, p4 = st.columns(4)

            p1.metric(
                "Rank position",
                safe_number(player["rank_position"]),
            )
            p2.metric(
                "Ranking points",
                safe_number(player["points"]),
            )
            p3.metric(
                "Movement value",
                safe_number(player["movement"]),
            )
            p4.metric(
                "Competitions played",
                safe_number(player["competitions_played"]),
            )

            st.markdown("### Available ranking records")

            player_columns = [
                "ranking_type_name",
                "gender",
                "ranking_year",
                "ranking_week",
                "rank_position",
                "points",
                "movement",
                "competitions_played",
            ]

            st.dataframe(
                player_rows[player_columns],
                use_container_width=True,
                hide_index=True,
            )

            show_download(
                player_rows[player_columns],
                "competitor_profile.csv",
                "⬇ Export competitor records",
            )

            st.info(
                "The profile displays fields available in your dataset. "
                "Historical ranking changes are not inferred when only "
                "a single ranking snapshot is available."
            )


# ============================================================
# PAGE 4 — COMPETITION INTELLIGENCE
# ============================================================

elif page == "Competition Intelligence":

    st.markdown(
        '<div class="section-label">TOURNAMENT DISCOVERY</div>',
        unsafe_allow_html=True,
    )
    st.header("Competition Intelligence")

    comp_data = competitions.copy()

    gender_list = sorted(
        comp_data["gender"].dropna().astype(str).unique().tolist()
    )
    type_list = sorted(
        comp_data["competition_type"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    category_list = sorted(
        comp_data["category_name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    f1, f2, f3 = st.columns(3)

    with f1:
        comp_gender = st.selectbox(
            "Filter gender",
            ["All"] + gender_list,
            key="comp_gender",
        )

    with f2:
        comp_type = st.selectbox(
            "Filter competition type",
            ["All"] + type_list,
            key="comp_type",
        )

    with f3:
        comp_category = st.selectbox(
            "Filter category",
            ["All"] + category_list,
            key="comp_category",
        )

    comp_search = st.text_input(
        "Search competition name",
        placeholder="Search a tournament or competition...",
    )

    if comp_gender != "All":
        comp_data = comp_data[
            comp_data["gender"].astype(str) == comp_gender
        ]

    if comp_type != "All":
        comp_data = comp_data[
            comp_data["competition_type"].astype(str) == comp_type
        ]

    if comp_category != "All":
        comp_data = comp_data[
            comp_data["category_name"].astype(str) == comp_category
        ]

    if comp_search.strip():
        comp_data = comp_data[
            comp_data["competition_name"].astype(str).str.contains(
                comp_search.strip(), case=False, na=False
            )
        ]

    a, b = st.columns(2)
    a.metric("Matching competitions", f"{len(comp_data):,}")
    b.metric(
        "Categories represented",
        f"{comp_data['category_name'].nunique():,}",
    )

    comp_chart = (
        comp_data["category_name"]
        .fillna("Unknown")
        .value_counts()
        .head(15)
        .rename_axis("Category")
        .reset_index(name="Competitions")
    )

    if not comp_chart.empty:
        fig = px.bar(
            comp_chart.sort_values("Competitions"),
            x="Competitions",
            y="Category",
            orientation="h",
            title="Competitions by Category",
            color="Competitions",
            color_continuous_scale=["#3B5940", GREEN],
        )

        st.plotly_chart(
            style_chart(fig, height=430),
            use_container_width=True,
        )

    st.markdown("### Competition catalogue")

    st.dataframe(
        comp_data[
            [
                "competition_name",
                "competition_type",
                "gender",
                "category_name",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    show_download(
        comp_data,
        "filtered_competitions.csv",
        "⬇ Export competitions",
    )


# ============================================================
# PAGE 5 — VENUE INTELLIGENCE
# ============================================================

elif page == "Venue Intelligence":

    st.markdown(
        '<div class="section-label">GLOBAL TENNIS VENUES</div>',
        unsafe_allow_html=True,
    )
    st.header("Venue Intelligence")

    venue_data = venues.copy()

    country_list = sorted(
        venue_data["country_name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    venue_country = st.selectbox(
        "Select venue country",
        ["All"] + country_list,
    )

    venue_search = st.text_input(
        "Search venue, city or complex",
        placeholder="Enter a venue, city or complex name...",
    )

    if venue_country != "All":
        venue_data = venue_data[
            venue_data["country_name"].astype(str) == venue_country
        ]

    if venue_search.strip():
        mask = (
            venue_data["venue_name"].astype(str).str.contains(
                venue_search, case=False, na=False
            )
            | venue_data["city_name"].astype(str).str.contains(
                venue_search, case=False, na=False
            )
            | venue_data["complex_name"].astype(str).str.contains(
                venue_search, case=False, na=False
            )
        )
        venue_data = venue_data[mask]

    v1, v2, v3 = st.columns(3)

    v1.metric("Matching venues", f"{len(venue_data):,}")
    v2.metric(
        "Countries",
        f"{venue_data['country_name'].nunique():,}",
    )
    v3.metric(
        "Complexes",
        f"{venue_data['complex_id'].nunique():,}",
    )

    country_counts = (
        venue_data["country_name"]
        .dropna()
        .value_counts()
        .head(15)
        .rename_axis("Country")
        .reset_index(name="Venues")
    )

    if not country_counts.empty:
        fig = px.bar(
            country_counts.sort_values("Venues"),
            x="Venues",
            y="Country",
            orientation="h",
            title="Venue Distribution by Country",
            color="Venues",
            color_continuous_scale=["#3B5940", GREEN],
        )

        st.plotly_chart(
            style_chart(fig, height=430),
            use_container_width=True,
        )

    st.markdown("### Venue directory")

    venue_columns = [
        "venue_name",
        "city_name",
        "country_name",
        "complex_name",
        "timezone",
    ]

    st.dataframe(
        venue_data[venue_columns],
        use_container_width=True,
        hide_index=True,
    )

    show_download(
        venue_data[venue_columns],
        "venue_directory.csv",
        "⬇ Export venue directory",
    )


# ============================================================
# PAGE 6 — DATA QUALITY
# ============================================================

elif page == "Data Quality":

    st.markdown(
        '<div class="section-label">PIPELINE MONITORING</div>',
        unsafe_allow_html=True,
    )
    st.header("Data Quality & Database Audit")

    st.caption(
        "A quick audit of loaded records and missing values. "
        "These checks describe the current database snapshot."
    )

    table_frames = {
        "categories": categories,
        "competitions": competitions,
        "complexes": complexes,
        "venues": venues,
        "competitors": competitors,
        "competitor_rankings": rankings,
    }

    summary_rows = []

    for table_name, frame in table_frames.items():
        summary_rows.append({
            "Table": table_name,
            "Records": len(frame),
            "Columns": len(frame.columns),
            "Missing cells": int(frame.isna().sum().sum()),
            "Duplicate rows": int(frame.duplicated().sum()),
        })

    quality_summary = pd.DataFrame(summary_rows)

    total_records = int(quality_summary["Records"].sum())
    missing_cells = int(quality_summary["Missing cells"].sum())
    duplicate_rows = int(quality_summary["Duplicate rows"].sum())

    q1, q2, q3 = st.columns(3)

    q1.metric("Total table records", f"{total_records:,}")
    q2.metric("Missing cells", f"{missing_cells:,}")
    q3.metric("Duplicate rows", f"{duplicate_rows:,}")

    st.markdown("### Table-level quality summary")

    st.dataframe(
        quality_summary,
        use_container_width=True,
        hide_index=True,
    )

    show_download(
        quality_summary,
        "data_quality_summary.csv",
        "⬇ Download quality report",
    )

    st.markdown("### Missing values by column")

    selected_table = st.selectbox(
        "Choose table",
        list(table_frames.keys()),
    )

    selected_frame = table_frames[selected_table]

    null_report = pd.DataFrame({
        "Column": selected_frame.columns,
        "Missing Values": [
            int(selected_frame[column].isna().sum())
            for column in selected_frame.columns
        ],
    })

    null_report["Missing %"] = (
        null_report["Missing Values"]
        / max(len(selected_frame), 1)
        * 100
    ).round(2)

    st.dataframe(
        null_report,
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Duplicate-row checks identify identical rows in the loaded "
        "DataFrames. They do not replace primary-key, foreign-key, "
        "or source-data validation."
    )


# ------------------------------------------------------------
# 7. FOOTER
# ------------------------------------------------------------

st.markdown("---")

st.markdown(
    f"""
    <div style="text-align:center;padding:12px;color:{MUTED};">
        <b style="color:{GREEN};">MATCH POINT</b>
        &nbsp;·&nbsp; Tennis Intelligence Platform<br>
        <span style="font-size:12px;">
            Built with Python, Streamlit, Plotly, SQLite and SportRadar API
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

