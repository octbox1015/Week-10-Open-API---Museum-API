import streamlit as st
import requests
import pandas as pd

# ====== PAGE CONFIG ======
st.set_page_config(page_title="MET Museum Art Explorer", page_icon="🎨", layout="wide")

# ====== INTRODUCTION ======
st.title("🎨 MET Museum Art Explorer - Advanced Version")
st.markdown("""
Welcome to the **Advanced MET Museum Art Explorer**!  

This app allows you to **search artworks by keyword, type, creation period, and artist nationality**, explore high-resolution images, and learn detailed information about each artwork.

**How to use:**
1. Enter a keyword (e.g., "flower", "portrait") in the search box.
2. Optionally filter by art type, creation year range, or artist nationality.
3. Browse artworks in the results section.
4. Click any image for detailed information and a link to the MET Museum website.

All data is sourced from the [MET Museum Open API](https://metmuseum.org/).
""")

# ====== USER INPUT ======
keyword = st.text_input("Enter keyword(s) to search artworks:", "flower")
art_type = st.selectbox("Filter by type (optional):", ["All", "Painting", "Sculpture", "Drawing", "Print"])
nationality = st.text_input("Filter by artist nationality (optional, e.g., 'American'):", "")
date_range = st.slider("Select creation period (year):", 1000, 2025, (1800, 2000))
search_button = st.button("Search")

if search_button and keyword:
    # ====== SEARCH ARTWORKS ======
    search_url = f"https://collectionapi.metmuseum.org/public/collection/v1/search?q={keyword}"
    search_response = requests.get(search_url).json()
    
    if search_response['total'] > 0:
        object_ids = search_response['objectIDs'][:50]  # limit to first 50 for demo
        st.write(f"Found {search_response['total']} artworks. Showing first {len(object_ids)} results.")

        artworks = []
        for obj_id in object_ids:
            obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}"
            obj_data = requests.get(obj_url).json()
            
            # Filter by type
            if art_type != "All" and obj_data.get("objectName", "").lower() != art_type.lower():
                continue
            
            # Filter by date
            try:
                year = int(obj_data.get("objectDate", "0")[:4])
                if year < date_range[0] or year > date_range[1]:
                    continue
            except:
                pass

            # Filter by nationality
            if nationality:
                if nationality.lower() not in obj_data.get("artistNationality", "").lower():
                    continue

            artworks.append({
                "title": obj_data.get("title", "Untitled"),
                "artist": obj_data.get("artistDisplayName", "Unknown"),
                "date": obj_data.get("objectDate", "Unknown"),
                "medium": obj_data.get("medium", "Unknown"),
                "nationality": obj_data.get("artistNationality", "Unknown"),
                "image": obj_data.get("primaryImageSmall", ""),
                "url": obj_data.get("objectURL", "")
            })
        
        # Display artworks in grid (2 columns for demo)
        cols = st.columns(2)
        for idx, art in enumerate(artworks):
            col = cols[idx % 2]
            with col:
                st.subheader(art["title"])
                st.write(f"Artist: {art['artist']} | Date: {art['date']} | Medium: {art['medium']} | Nationality: {art['nationality']}")
                if art["image"]:
                    st.image(art["image"], use_column_width=True)
                st.markdown(f"[View on MET Museum]({art['url']})")
                st.markdown("---")
    else:
        st.warning("No artworks found for this keyword.")
