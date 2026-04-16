"""
Project:  Expense Analytics Dashboard
Author: [DALIM KUMAR ]
License: MIT
Description: A professional Streamlit application for tracking and visualizing personal finances.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from datetime import datetime

# ==========================================
# 1. GLOBAL SETTINGS & DIRECTORY SETUP
# ==========================================
st.set_page_config(
    page_title="expense tracker  | Data Insights",
    page_icon="💰",
    layout="wide"
)

# Create directory structure for scalability
PROJECT_DIRS = ['data', 'outputs', 'reports']
for folder in PROJECT_DIRS:
    os.makedirs(folder, exist_ok=True)

DATA_PATH = "data/transactions.csv"

# ==========================================
# 2. DATA ENGINE
# ==========================================
def load_data():
    """Loads transaction data from CSV or returns an empty DataFrame."""
    if os.path.exists(DATA_PATH):
        try:
            df = pd.read_csv(DATA_PATH)
            df['Date'] = pd.to_datetime(df['Date'])
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()
    return pd.DataFrame(columns=["Date", "Category", "Amount", "Currency", "Description"])

def save_data(dataframe):
    """Saves the current DataFrame to a CSV file."""
    dataframe.to_csv(DATA_PATH, index=False)

# ==========================================
# 3. SIDEBAR - GLOBAL INPUTS
# ==========================================
st.sidebar.header("🕹️ Control Panel")
st.title("Expense Tracker Dashboard")
# Currency Selection (Makes it Global)
currency = st.sidebar.selectbox("Select Base Currency", ["USD ($)", "EUR (€)", "INR (₹)", "GBP (£)", "JPY (¥)", "BDT (৳)"])
currency_symbol = currency.split(" ")[1].replace("(", "").replace(")", "")

with st.sidebar.expander("➕ Add Transaction", expanded=True):
    with st.form("input_form", clear_on_submit=True):
        date = st.date_input("Transaction Date", datetime.now())
        cat = st.selectbox("Category", ["Housing", "Food", "Transport", "Utilities", "Health", "Leisure", "Education", "Income", "Investments"])
        amt = st.number_input(f"Amount ({currency_symbol})", min_value=0.0, format="%.2f")
        desc = st.text_input("Short Description")
        
        if st.form_submit_button("Record Transaction"):
            if amt > 0:
                df = load_data()
                new_row = pd.DataFrame([[pd.to_datetime(date), cat, amt, currency_symbol, desc]], 
                                       columns=df.columns)
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.toast("Transaction recorded successfully!", icon="✅")
                st.rerun()
            else:
                st.warning("Please enter an amount greater than zero.")

# ==========================================
# 4. MAIN DASHBOARD
# ==========================================

st.write(f"Monitoring financial flow in **{currency.split(' ')[0]}**")

df = load_data()

if not df.empty:
    # --- KPI Calculations ---
    # Separating Income vs Expenses
    total_income = df[df['Category'] == 'Income']['Amount'].sum()
    total_expenses = df[df['Category'] != 'Income']['Amount'].sum()
    savings_rate = ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Income", f"{currency_symbol}{total_income:,.2f}")
    m2.metric("Total Expenses", f"{currency_symbol}{total_expenses:,.2f}")
    m3.metric("Net Balance", f"{currency_symbol}{(total_income - total_expenses):,.2f}")
    m4.metric("Savings Rate", f"{savings_rate:.1f}%")

    st.markdown("---")

    # --- Analytics Charts ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Spending Breakdown by Category")
        expense_only = df[df['Category'] != 'Income']
        if not expense_only.empty:
            fig_pie = px.pie(expense_only, values='Amount', names='Category', hole=0.4,
                             template="plotly_dark", color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data available for visualization.")

    with c2:
        st.subheader("Daily Cashflow Trend")
        df_trend = df.groupby('Date')['Amount'].sum().reset_index()
        fig_line = px.area(df_trend, x='Date', y='Amount', 
                           line_shape="spline", template="plotly_white")
        st.plotly_chart(fig_line, use_container_width=True)

    # --- Data Table & Export ---
    st.subheader("📜 Transaction Ledger")
    st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
    
    # Global Download Feature
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Data to CSV", data=csv, file_name='fintrack_report.csv', mime='text/csv')

else:
    st.info("👋 Welcome! Use the sidebar to add your first transaction or upload a file.")
    # Professional Placeholder
    st.image("https://raw.githubusercontent.com/streamlit/fluent-ui-components/master/images/hero.png")

# ==========================================
# 5. FOOTER
# ==========================================
st.sidebar.markdown("---")
st.sidebar.caption("v1.0.0 Global Edition | Built with ❤️ by [DALIM KUMAR ]")