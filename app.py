import streamlit as st
import pandas as pd

# Set page layout to wide
st.set_page_config(layout="wide")

# App Title
st.title("Financial Metrics Dashboard")

@st.cache_data
def load_data():
    """Loads, cleans, and standardizes the CSV data and headers."""
    try:
        # Assumes Stocks.csv is in the same GitHub repository folder
        df = pd.read_csv("Stocks.csv")
        
        # 1. Clean headers: strip spaces and convert everything to lowercase
        df.columns = df.columns.str.strip().str.lower()
        
        # 2. Check for missing critical columns to display a friendly message
        required_columns = ['ticker', 'company', 'metric', '2023', '2024', '2025']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Error: Your CSV is missing the following required column headers: {', '.join(missing_columns)}")
            st.write("Current columns found in your file:", list(df.columns))
            return None
        
        # 3. Ensure correct datatypes
        df['ticker'] = df['ticker'].astype(str).str.strip()
        df['company'] = df['company'].astype(str).str.strip()
        df['metric'] = df['metric'].astype(str).str.strip()
        
        # Handle cases where manual entry might have commas or blank spaces in numbers
        df['2023'] = pd.to_numeric(df['2023'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
        df['2024'] = pd.to_numeric(df['2024'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
        df['2025'] = pd.to_numeric(df['2025'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
        
        return df
    except FileNotFoundError:
        st.error("Error: 'Stocks.csv' not found. Please upload it to your GitHub repository.")
        return None

# Load dataset
df = load_data()

if df is not None:
    # --- Top Layout with Right-Aligned Dropdown ---
    # col1, col2 = st.columns()
    col1, col2 = st.columns([4, 1])
    
    with col1:
        unique_tickers = sorted(df['ticker'].unique())
        
    with col2:
        # Top-right dropdown selector
        selected_ticker = st.selectbox("Select Ticker", options=unique_tickers)
    
    # Filter data based on selected ticker
    filtered_df = df[df['ticker'] == selected_ticker].copy()
    
    # Extract company name safely for the header
    company_name = filtered_df['company'].iloc[0]
    st.subheader(f"{company_name} ({selected_ticker})")
    
    # Isolate display columns
    display_df = filtered_df[['metric', '2023', '2024', '2025']].reset_index(drop=True)
    
    # --- Conditional Coloring Logic ---
    def style_dataframe(row):
        """Applies conditional formatting based on year-over-year growth."""
        styles = [''] * len(row)
        
        val_2023 = row['2023']
        val_2024 = row['2024']
        val_2025 = row['2025']
        
        # Style 2024 column (Index 2 in DataFrame structure)
        if val_2024 > val_2023:
            styles[2] = 'background-color: green; color: white;'
        else:
            styles[2] = 'background-color: red; color: white;'
            
        # Style 2025 column (Index 3 in DataFrame structure)
        if val_2025 > val_2024:
            styles[3] = 'background-color: green; color: white;'
        else:
            styles[3] = 'background-color: red; color: white;'
            
        return styles

    # Apply styles to the table dataframe
    styled_df = display_df.style.apply(style_dataframe, axis=1).format({
        '2023': '{:,.2f}',
        '2024': '{:,.2f}',
        '2025': '{:,.2f}'
    })
    
    # Display the styled interactive table
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
