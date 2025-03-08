import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from func import DataAnalyzer, BrazilMapPlotter
from babel.numbers import format_currency

sns.set(style='dark')

# Dataset
datetime_cols = [
    "order_approved_at", "order_delivered_carrier_date",
    "order_delivered_customer_date", "order_estimated_delivery_date",
    "order_purchase_timestamp", "shipping_limit_date"
]

try:
    all_df = pd.read_csv("../data/all_data.xls")  # Pastikan file ini CSV, bukan Excel
except:
    all_df = pd.read_excel("../data/all_data.xls")

all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Geolocation Dataset
try:
    geolocation = pd.read_csv('../data/geolocation.xls')
except:
    geolocation = pd.read_excel('../data/geolocation.xls')

data = geolocation.drop_duplicates(subset='customer_unique_id')

# Konversi Kolom Tanggal
for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col], errors='coerce')

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    st.title("Fazlu Rachman :sparkles:")
    # st.image("gcl.png")

        # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter Data
main_df = all_df[
    (all_df["order_approved_at"] >= str(start_date)) & 
    (all_df["order_approved_at"] <= str(end_date))
]

# Data Analyzer
function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()
# rfm_df = function.create_rfm_df(main_df)

# Dashboard
st.header("Dashboard Brazilian E-Commerce :convenience_store:")

# **Daily Orders**
st.subheader("Daily Orders")
col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Order: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Revenue: **{total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(daily_orders_df["order_approved_at"], daily_orders_df["order_count"], marker="o", linewidth=2, color="#90CAF9")
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)
plt.close(fig)

# **Customer Spend Money**
st.subheader("Customer Spend Money")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Spend: **{total_spend}**")

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "IDR", locale="id_ID")
    st.markdown(f"Average Spend: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(sum_spend_df["order_approved_at"], sum_spend_df["total_spend"], marker="o", linewidth=2, color="#90CAF9")
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)
plt.close(fig)

# **Review Score**
st.subheader("Review Score")
col1, col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Average Review Score: **{avg_review_score:.2f}**")

with col2:
    most_common_review_score = review_score.value_counts().idxmax()
    st.markdown(f"Most Common Review Score: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index, y=review_score.values, order=review_score.index,
            palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index])
plt.title("Rating by customers for service", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Count")
plt.xticks(fontsize=12)
st.pyplot(fig)
plt.close(fig)

# **Customer Demographic**
st.subheader("Customer Demographic")
tab1, tab2, tab3 = st.tabs(["State", "Order Status", "Geolocation"])

with tab1:
    st.markdown(f"Most Common State: **{most_common_state}**")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=state.customer_state.value_counts().index,
                y=state.customer_count.values, data=state,
                palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index])
    plt.title("Number customers from State", fontsize=15)
    plt.xlabel("State")
    plt.ylabel("Number of Customers")
    plt.xticks(fontsize=12)
    st.pyplot(fig)
    plt.close(fig)

with tab2:
    st.markdown(f"Most Common Order Status: **{common_status}**")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=order_status.index, y=order_status.values, order=order_status.index,
                palette=["#068DA9" if score == common_status else "#D3D3D3" for score in order_status.index])
    plt.title("Order Status", fontsize=15)
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(fontsize=12)
    st.pyplot(fig)
    plt.close(fig)

with tab3:
    map_plot.plot()
    with st.expander("See Explanation"):
        st.write('Lebih banyak pelanggan di bagian tenggara dan selatan, terutama di kota besar seperti São Paulo dan Rio de Janeiro.')

st.caption('Copyright (C) Fazlu Rachman 2025')
