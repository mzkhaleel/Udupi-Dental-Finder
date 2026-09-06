import streamlit as st
from duckduckgo_search import DDGS
from datetime import datetime

st.set_page_config(page_title="Udupi Dental Finder Pro", page_icon="🦷", layout="wide")

st.title("🦷 Udupi & Manipal Dental Course Tracker")
st.markdown("Searching the web for Endodontics, Implants, and Workshops in the Udupi region.")

def search_events():
    # We broaden the terms significantly to ensure we don't miss anything
    queries = [
        "dental workshop Manipal 2024 2026",
        "dental conclave Udupi",
        "endodontics certificate course Manipal",
        "root canal workshop Udupi",
        "dental implant module Karnataka BDS MDS",
        "MCODS Manipal upcoming events",
        "IDA Udupi branch workshops"
    ]
    
    found_results = []
    
    with st.spinner('Scanning all Indian dental portals for Udupi/Manipal updates...'):
        with DDGS() as ddgs:
            for q in queries:
                # Region 'in-en' targets India/English specifically
                # timelimit 'y' looks for things within the last year
                results = ddgs.text(q, region='in-en', max_results=10)
                if results:
                    for r in results:
                        # We only filter out results that are definitely NOT in the right area
                        content = (r['title'] + r['body']).lower()
                        
                        # We look for ANY local keyword
                        local_keywords = ["manipal", "udupi", "mcods", "karnataka", "nitte", "mahe"]
                        if any(k in content for k in local_keywords):
                            if r['href'] not in [res['link'] for res in found_results]:
                                found_results.append({
                                    "title": r['title'],
                                    "link": r['href'],
                                    "desc": r['body']
                                })
    return found_results

if st.button('🔍 Run Deep Search (Wide Scan)'):
    data = search_events()
    
    if data:
        st.success(f"Found {len(data)} potential events and listings!")
        
        # Displaying results in a clean list
        for item in data:
            with st.container():
                # Color code MCODS/Manipal.edu results
                if "manipal.edu" in item['link']:
                    st.markdown(f"### 🏫 {item['title']}")
                    st.info("Primary source: Manipal Academy of Higher Education")
                else:
                    st.markdown(f"### 🌐 {item['title']}")
                
                st.write(item['desc'])
                st.markdown(f"[**Click to open listing**]({item['link']})")
                st.write("---")
    else:
        st.error("Still no matches. Try checking your internet or clicking 'Search' again in a moment.")

st.sidebar.markdown("""
### 💡 Search Tips:
- **Broadening:** I have expanded the search to look for "Manipal" and "MCODS" specifically.
- **Timing:** Academic calendars often update in cycles; if it's empty today, check again after the weekend.
- **Root Canal:** Includes keywords for 'Endodontics' and 'Rotary RCT' workshops.
""")
