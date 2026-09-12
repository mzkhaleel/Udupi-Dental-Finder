import streamlit as st
from duckduckgo_search import DDGS
import urllib.parse
import time

st.set_page_config(page_title="Udupi Dental Tracker", page_icon="🦷", layout="wide")

st.title("🦷 Udupi & Manipal Dental Course Tracker")
st.markdown("Search for Endodontics, Implants, and Workshops. Results are saved for 1 hour to prevent blocking.")

# --- CACHING LOGIC ---
# This saves the results so you don't get blocked for searching too often
@st.cache_data(ttl=3600) 
def get_cached_results(dummy_trigger):
    queries = [
        "dental workshop Manipal 2024 2026",
        "dental conclave Udupi",
        "endodontics module Manipal MCODS",
        "root canal hands-on Udupi",
        "dental implant course Udupi Karnataka",
        "MCODS Manipal CDE news"
    ]
    
    found_results = []
    
    with DDGS() as ddgs:
        for q in queries:
            try:
                # Small sleep to prevent rate-limiting/blocking
                time.sleep(0.5) 
                results = ddgs.text(q, region='in-en', max_results=8)
                if results:
                    for r in results:
                        content = (r['title'] + r['body']).lower()
                        local_keywords = ["manipal", "udupi", "mcods", "karnataka", "nitte", "mahe"]
                        if any(k in content for k in local_keywords):
                            if r['href'] not in [res['link'] for res in found_results]:
                                found_results.append({
                                    "title": r['title'],
                                    "link": r['href'],
                                    "desc": r['body']
                                })
            except Exception:
                continue # Skip if a specific query is blocked
    return found_results

# --- UI LOGIC ---
if st.button('🔍 Search / Refresh Listings'):
    # We use time.time() to allow manual refresh if the user really wants to
    results = get_cached_results(time.time())
    st.session_state['dental_results'] = results

if 'dental_results' in st.session_state and st.session_state['dental_results']:
    results = st.session_state['dental_results']
    st.success(f"Found {len(results)} listings!")

    # --- EXPORT SECTION ---
    st.subheader("📤 Share / Export Results")
    
    # Prepare text for sharing
    share_text = "🦷 *Udupi Dental Events Found:*\n\n"
    for item in results[:5]: # Top 5 results to keep message short
        share_text += f"📍 {item['title']}\n🔗 {item['link']}\n\n"
    
    encoded_text = urllib.parse.quote(share_text)
    
    col1, col2 = st.columns(2)
    with col1:
        # WhatsApp Link
        wa_url = f"https://wa.me/?text={encoded_text}"
        st.markdown(f'''<a href="{wa_url}" target="_blank">
            <button style="width:100%; border-radius:10px; background-color:#25D366; color:white; padding:10px; border:none; cursor:pointer;">
                Share via WhatsApp
            </button></a>''', unsafe_allow_html=True)
            
    with col2:
        # Email Link
        mail_url = f"mailto:?subject=Dental Courses Udupi&body={encoded_text}"
        st.markdown(f'''<a href="{mail_url}">
            <button style="width:100%; border-radius:10px; background-color:#0078D4; color:white; padding:10px; border:none; cursor:pointer;">
                Share via Email
            </button></a>''', unsafe_allow_html=True)

    st.divider()

    # --- DISPLAY LISTINGS ---
    for item in results:
        with st.container():
            st.markdown(f"### {item['title']}")
            st.write(item['desc'])
            st.markdown(f"[**Open Link**]({item['link']})")
            st.write("---")
            
elif 'dental_results' in st.session_state:
    st.warning("No results found. The search engine might be blocking requests. Please try again in 10 minutes.")
