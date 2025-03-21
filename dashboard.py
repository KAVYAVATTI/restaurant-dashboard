import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# Load Data
df = pd.read_csv('fully_geocoded_restaurants.csv')

st.set_page_config(page_title="Restaurant Analytics Dashboard", layout="wide")

# Sidebar Filters
st.sidebar.title("🔍 Filters")
cities = st.sidebar.multiselect("Select City", df['City'].unique(), default=df['City'].unique())
categories = st.sidebar.multiselect("Select Category", df['Category'].unique(), default=df['Category'].unique())
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.0)
min_reviews = st.sidebar.slider("Minimum Reviews", 0, int(df['Reviews'].max()), 10)

# Filtered Data
filtered_df = df[(df['City'].isin(cities)) &
                 (df['Category'].isin(categories)) &
                 (df['Google_Rating'] >= min_rating) &
                 (df['Reviews'] >= min_reviews)]

# Title
st.title("🍽️ Restaurant Analytics Dashboard")

# Summary Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Restaurants", len(filtered_df))
col2.metric("Average Rating", round(filtered_df['Google_Rating'].mean(), 2))
col3.metric("Total Reviews", filtered_df['Reviews'].sum())
col4.metric("Avg Distance (m)", round(filtered_df['Distance (meters)'].mean(), 2))

st.markdown("---")

# Visual 1: Category Count
cat_count = filtered_df['Category'].value_counts().reset_index()
cat_count.columns = ['Category', 'Count']  # Rename columns properly
fig1 = px.bar(cat_count, x='Category', y='Count', 
              title="Restaurant Count by Category",
              color='Category',
              text_auto='.2s')  # Adds data labels
st.plotly_chart(fig1, use_container_width=True)

# Visual 2: Average Rating by City
avg_rating_city = filtered_df.groupby('City')['Google_Rating'].mean().reset_index()
fig2 = px.bar(avg_rating_city, x='City', y='Google_Rating', 
              title="Average Rating by City", color='Google_Rating', text_auto='.2f')
st.plotly_chart(fig2, use_container_width=True)

# Visual 3: Review Distribution
fig3 = px.histogram(filtered_df, x='Reviews', nbins=30,
                    title="Review Count Distribution",
                    color_discrete_sequence=['indianred'])
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# Geospatial Map
st.subheader("🌍 Restaurant Locations Map")
map_center = [filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()]
m = folium.Map(location=map_center, zoom_start=5)

for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=5,
        popup=f"{row['Name']} ({row['Google_Rating']})",
        color='blue',
        fill=True,
        fill_color='blue'
    ).add_to(m)
folium_static(m, width=1000)

# Data Table
st.markdown("---")
st.subheader("📋 Filtered Restaurant Data")
st.dataframe(filtered_df[['City', 'Name', 'Category', 'Google_Rating', 'Reviews', 'Distance (meters)']])

# Download Option
csv = filtered_df.to_csv(index=False)
st.download_button("Download Filtered Data as CSV", data=csv, file_name='filtered_restaurants.csv', mime='text/csv')

st.markdown("---")
st.subheader("🧠 Smart Restaurant Recommender")

# User Inputs
selected_city = st.selectbox("Select City", df['City'].unique(), key='rec_city')
selected_category = st.selectbox("Select Category", df['Category'].unique(), key='rec_category')
max_distance = st.slider("Preferred Max Distance (meters)", 100, int(df['Distance (meters)'].max()), 1000)

# Filter based on user input
rec_df = df[(df['City'] == selected_city) &
            (df['Category'] == selected_category) &
            (df['Distance (meters)'] <= max_distance)]

# Smart Scoring: Weighted score (e.g., 70% Rating, 30% Reviews normalized)
if not rec_df.empty:
    rec_df['Score'] = (rec_df['Google_Rating'] * 0.7) + (rec_df['Reviews']/rec_df['Reviews'].max() * 0.3)
    top_recommendations = rec_df.sort_values(by='Score', ascending=False).head(5)

    # Display Results
    for _, row in top_recommendations.iterrows():
        st.markdown(f"### 🍽️ {row['Name']}")
        st.write(f"⭐ Rating: {row['Google_Rating']} | 💬 Reviews: {row['Reviews']}")
        st.write(f"📍 Distance: {round(row['Distance (meters)'], 2)} m | 📊 Score: {round(row['Score'], 2)}")
        st.markdown("---")
else:
    st.warning("No restaurants found matching your preferences.")

