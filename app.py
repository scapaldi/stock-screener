import streamlit as pd
import pandas as pd

# Set page layout to wide
st.set_page_config(layout="wide")

# App Title
st.title("Financial Metrics Dashboard")


@st.cache_data
def load_data():
    """Loads and cleans the CSV data."""
    try:
        # Assumes data.csv is in the same GitHub repository folder
        df = pd.read_csv("data.csv")

        # Clean column names to remove any accidental whitespace
        df.columns = df.columns.str.strip()

        # Ensure correct datatypes
        df["ticker"] = df["ticker"].astype(str).str.strip()
        df["company"] = df["company"].astype(str).str.strip()
        df["metric"] = df["metric"].astype(str).str.strip()
        df["2023"] = df["2023"].astype(float)
        df["2024"] = df["2024"].astype(float)
        df["2025"] = df["2025"].astype(float)

        return df
    except FileNotFoundError:
        st.error(
            "Error: 'data.csv' not found. Please upload it to your GitHub repository."
        )
        return None


# Load dataset
df = load_data()

if df is not None:
    # --- Top Layout with Right-Aligned Dropdown ---
    col1, col2 = st.columns([3, 1])

    with col1:
        # Dynamically display the selected company name
        unique_tickers = sorted(df["ticker"].unique())

    with col2:
        # Top-right dropdown selector
        selected_ticker = st.selectbox("Select Ticker", options=unique_tickers)

    # Filter data based on selected ticker
    filtered_df = df[df["ticker"] == selected_ticker].copy()

    # Extract company name for the header
    company_name = filtered_df["company"].iloc[0]
    st.subheader(f"{company_name} ({selected_ticker})")

    # Isolate display columns
    display_df = filtered_df[["metric", "2023", "2024", "2025"]].reset_index(
        drop=True
    )

    # --- Conditional Coloring Logic ---
    def style_dataframe(row):
        """Applies conditional formatting based on year-over-year growth."""
        # Initialize default styles (no background)
        styles = [""] * len(row)

        # 2024 Comparison (Index 1 in display_df columns: metric=0, 2023=1, 2024=2, 2025=3)
        val_2023 = row["2023"]
        val_2024 = row["2024"]
        val_2025 = row["2025"]

        # Style 2024 column
        if val_2024 > val_2023:
            styles[2] = "background-color: green; color: white;"
        else:
            styles[2] = "background-color: red; color: white;"

        # Style 2025 column
        if val_2025 > val_2024:
            styles[3] = "background-color: green; color: white;"
        else:
            styles[3] = "background-color: red; color: white;"

        return styles

    # Apply styles to the table dataframe
    styled_df = display_df.style.apply(style_dataframe, axis=1).format(
        {"2023": "{:,.2f}", "2024": "{:,.2f}", "2025": "{:,.2f}"}
    )

    # Display the styled interactive table
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
