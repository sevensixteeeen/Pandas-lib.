"""House Price Explorer — a Streamlit app built on housing.csv.

Run it from this folder with:
    python -m streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "housing.csv"

st.set_page_config(page_title="House Price Explorer", layout="wide")


# ---------------------------------------------------------------------------
# STEP 1 — Load and clean the data (same cleaning as housing.ipynb)
# @st.cache_data runs this once and reuses the result on every rerun,
# so the 2.6 MB CSV isn't re-read each time you move a slider.
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE, index_col=0, dtype={"zipcode": str})
    df = df.drop_duplicates()
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%dT%H%M%S")
    df.loc[df["bedrooms"] == 33, "bedrooms"] = 3
    df = df[(df["bedrooms"] > 0) & (df["bathrooms"] > 0)].copy()
    return df


df = load_data()

st.title("🏠 House Price Explorer")
st.caption(f"{len(df):,} house sales from King County, WA (2014–2015)")


# ---------------------------------------------------------------------------
# STEP 2 — Sidebar filters, applied with boolean masks
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

min_price, max_price = int(df["price"].min()), int(df["price"].max())
price_range = st.sidebar.slider(
    "Price ($)", min_price, max_price, (min_price, 2_000_000), step=10_000
)

min_bed, max_bed = int(df["bedrooms"].min()), int(df["bedrooms"].max())
bed_range = st.sidebar.slider("Bedrooms", min_bed, max_bed, (min_bed, max_bed))

mask = (
    df["price"].between(*price_range)
    & df["bedrooms"].between(*bed_range)
)
filtered = df[mask]

if filtered.empty:
    st.warning("No houses match these filters. Try widening them.")
    st.stop()


# ---------------------------------------------------------------------------
# STEP 3 — Headline numbers
# ---------------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Houses", f"{len(filtered):,}")
c2.metric("Average price", f"${filtered['price'].mean():,.0f}")
c3.metric("Median price", f"${filtered['price'].median():,.0f}")
c4.metric("Avg living area", f"{filtered['sqft_living'].mean():,.0f} sqft")


# ---------------------------------------------------------------------------
# STEP 4 — Charts
# ---------------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("How many houses at each price?")
    # Round each price down to its $100k band, then count houses per band.
    band = (filtered["price"] // 100_000 * 100).rename("price band ($k)")
    st.bar_chart(band.value_counts().sort_index())

with right:
    st.subheader("Bigger house → higher price?")
    # Plotting ~20k dots is slow; a random sample shows the same pattern.
    sample = filtered.sample(min(len(filtered), 3000), random_state=0)
    st.scatter_chart(sample, x="sqft_living", y="price")

st.subheader("Most expensive zipcodes")
by_zip = (
    filtered.groupby("zipcode")
    .agg(avg_price=("price", "mean"), houses=("price", "size"))
    .sort_values("avg_price", ascending=False)
    .head(10)
)
st.dataframe(
    by_zip,
    column_config={"avg_price": st.column_config.NumberColumn("Avg price", format="$%d")},
)


# ---------------------------------------------------------------------------
# STEP 5 — Map (our longitude column is called "long", so we name it)
# ---------------------------------------------------------------------------
st.subheader("Where are they?")
st.map(filtered, latitude="lat", longitude="long", size=20)
