import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
import datetime as dt

sns.set(style='dark')

# Sidebar for Date Filter
st.sidebar.header("Filter Tanggal")
start_date = st.sidebar.date_input("Tanggal Mulai", dt.date(2017, 1, 1))
end_date = st.sidebar.date_input("Tanggal Akhir", dt.date(2018, 12, 31))

try:
    all_df = pd.read_csv("./data/all_data.xls")
except:
    all_df = pd.read_excel("./data/all_data.xls")

all_df['order_approved_at'] = pd.to_datetime(all_df['order_approved_at'])
all_df = all_df[(all_df['order_approved_at'].dt.date >= start_date) & (all_df['order_approved_at'].dt.date <= end_date)]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(drop=True, inplace=True)

try:
    geolocation = pd.read_csv('./data/geolocation.xls')
except:
    geolocation = pd.read_excel('./data/geolocation.xls')

# ---- Dashboard Title ----
st.title("Analisis E-Commerce Brasil")
st.write("Dashboard ini menyajikan analisis mendalam mengenai produk paling laris, kota dengan transaksi terbanyak, metode pembayaran yang paling sering digunakan, serta tingkat pelanggan yang melakukan pembelian ulang. Selain itu, dashboard ini juga menampilkan sebaran geografis pelanggan di Brasil dan melakukan Analisis RFM (Recency, Frequency, Monetary) untuk mengelompokkan pelanggan berdasarkan kebiasaan belanja mereka, guna membantu strategi pemasaran dan retensi pelanggan")

# ---- Produk Terlaris ----
st.header("Produk mana yang paling laris dan memberikan pendapatan tertinggi?")
sum_order_items_df = all_df.groupby("product_category_name_english").agg(
    total_sales=("product_id", "count"), 
    total_revenue=("price", "sum")
).reset_index().sort_values(by="total_sales", ascending=False).head(10)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    x=sum_order_items_df["total_sales"],
    y=sum_order_items_df["product_category_name_english"],
    hue=sum_order_items_df["total_revenue"],
    palette="Blues_r",
    ax=ax
)
ax.set_xlabel("Jumlah Penjualan")
ax.set_ylabel("Kategori Produk")
st.pyplot(fig)
st.write("Produk dengan jumlah penjualan terbanyak adalah 'bed_bath_table', sedangkan kategori dengan pendapatan tertinggi adalah 'watches_gifts'.")

# ---- Kota dengan Transaksi Tertinggi ----
st.header("Dari kota mana pelanggan dengan jumlah transaksi tertinggi berasal?")
top_cities = all_df.groupby('customer_city')['customer_id'].nunique().reset_index().rename(columns={'customer_id': 'total_transactions'}).sort_values(by='total_transactions', ascending=False).head(10)

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(y=top_cities['customer_city'], x=top_cities['total_transactions'], palette="Blues_r", ax=ax)
ax.set_xlabel("Jumlah Transaksi Unik")
ax.set_ylabel("Kota Pelanggan")
st.pyplot(fig)
st.write("Kota dengan transaksi tertinggi adalah São Paulo dan Rio de Janeiro, yang merupakan pusat e-commerce di Brasil.")

# ---- Metode Pembayaran ----
st.header("Metode pembayaran apa yang paling sering digunakan?")
payment_counts = all_df.groupby('payment_type')['order_id'].count().reset_index().rename(columns={'order_id': 'total_usage'}).sort_values(by='total_usage', ascending=False)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(y=payment_counts['payment_type'], x=payment_counts['total_usage'], palette="viridis", ax=ax)
ax.set_xlabel("Jumlah Penggunaan")
ax.set_ylabel("Metode Pembayaran")
st.pyplot(fig)
st.write("Metode pembayaran paling populer adalah kartu kredit, diikuti oleh boleto bancário.")

# ---- Pelanggan dengan Pembelian Ulang ----
st.header("Berapa banyak pelanggan yang melakukan pembelian berulang?")
repeat_customers = all_df['customer_id'].value_counts()
one_time_customers = (repeat_customers == 1).sum()
multiple_time_customers = (repeat_customers > 1).sum()

fig, ax = plt.subplots(figsize=(8, 8))
ax.pie([one_time_customers, multiple_time_customers], labels=['One-time Customers', 'Repeat Customers'], autopct='%1.1f%%', colors=['lightcoral', 'lightblue'], startangle=140)
st.pyplot(fig)
st.write("Sejumlah besar pelanggan melakukan pembelian ulang, terutama selama periode promo dan diskon.")

# ---- Peta Sebaran Pelanggan ----
st.header("Dimana saja letak geografis yang memiliki customer terbanyak?")
def plot_brazil_map(data):
    brazil = mpimg.imread(urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'), 'jpg')
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(data["geolocation_lng"], data["geolocation_lat"], alpha=0.3, s=0.3, c='maroon')
    ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
    ax.axis('off')
    return fig

data = geolocation.drop_duplicates(subset='customer_unique_id')
st.pyplot(plot_brazil_map(data))
st.write("Sebagian besar pelanggan berasal dari wilayah Tenggara dan Selatan Brasil, terutama São Paulo dan Rio de Janeiro.")


# ---- RFM Analysis ----
st.header("Analisis RFM (Recency, Frequency, Monetary)")

all_df['order_approved_at'] = pd.to_datetime(all_df['order_approved_at'])
latest_date = all_df['order_approved_at'].max()

rfm_df = all_df.groupby('customer_id').agg(
    Recency=('order_approved_at', lambda x: (latest_date - x.max()).days),
    Frequency=('order_id', 'count'),
    Monetary=('price', 'sum')
).reset_index()


rfm_df['Recency_Score'] = pd.qcut(rfm_df['Recency'], q=4, labels=[4, 3, 2, 1])

# Perbaikan Frequency Score
if rfm_df['Frequency'].nunique() >= 4:
    rfm_df['Frequency_Score'] = pd.qcut(rfm_df['Frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4])
else:
    rfm_df['Frequency_Score'] = pd.cut(rfm_df['Frequency'], bins=min(3, rfm_df['Frequency'].nunique()), labels=[1, 2, 3])

# Perbaikan Monetary Score
if rfm_df['Monetary'].nunique() >= 4:
    rfm_df['Monetary_Score'] = pd.qcut(rfm_df['Monetary'].rank(method='first'), q=4, labels=[1, 2, 3, 4])
else:
    rfm_df['Monetary_Score'] = pd.cut(rfm_df['Monetary'], bins=min(3, rfm_df['Monetary'].nunique()), labels=[1, 2, 3])

# RFM Score
rfm_df['RFM_Score'] = rfm_df[['Recency_Score', 'Frequency_Score', 'Monetary_Score']].sum(axis=1)
st.write(rfm_df.head(10))


# ---- Clustering dengan Manual Grouping ----
st.header("Segmentasi Pelanggan dengan Binning")
def customer_segmentation(row):
    if row['RFM_Score'] >= 10:
        return 'Loyal'
    elif row['RFM_Score'] >= 7:
        return 'Regular'
    else:
        return 'Occasional'

rfm_df['Customer_Segment'] = rfm_df.apply(customer_segmentation, axis=1)
st.write(rfm_df.groupby('Customer_Segment').size())

# ---- Kesimpulan Analisis RFM ----
st.header("Kesimpulan Analisis RFM")
st.write("""
- Sebagian besar pelanggan hanya melakukan **satu kali transaksi** (`Frequency = 1`), menunjukkan bahwa tingkat **retensi pelanggan masih rendah**.
- **Recency tinggi** pada banyak pelanggan menunjukkan bahwa mereka sudah lama tidak bertransaksi lagi, sehingga strategi **re-engagement** bisa diterapkan untuk mengundang mereka kembali.
- **Monetary Score bervariasi**, tetapi mayoritas pelanggan memiliki total belanja yang kecil, yang berarti peluang untuk meningkatkan nilai belanja mereka masih terbuka.
- Perlu **strategi loyalitas pelanggan**, seperti diskon, reward points, atau campaign khusus untuk meningkatkan jumlah pelanggan setia.

**Rekomendasi:**
- Menjalankan **email marketing** atau **notifikasi promo** kepada pelanggan dengan **Recency tinggi** agar mereka kembali berbelanja.
- Meningkatkan jumlah transaksi per pelanggan melalui program **loyalty points** atau **bundling produk**.
- Menargetkan pelanggan dengan **Monetary tinggi** dengan **penawaran eksklusif** agar mereka tetap setia.
""")

st.markdown("""
---
© 2025 - Fazlu Rachman
""", unsafe_allow_html=True)