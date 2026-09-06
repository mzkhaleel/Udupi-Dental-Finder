import streamlit as st
from duckduckgo_search import DDGS
from datetime import datetime

st.set_page_config(page_title="Udupi Dental Finder", page_icon="🦷")

st.title("🦷 Udupi Dental Event & Course Finder")
st.markdown("Searching for Implant courses, short modules, workshops, and news in **Udupi/Manipal**.")

def search_events():
    # We use broader queries here to catch "3 days", "weekend", or "general events"
    queries = [
        "dental implant course Udupi Manipal",
        "dental module BDS MDS Udupi",
        "MCODS Manipal dental workshops news CDE",
        "dental hands-on workshop Udupi",
        "IDA Udupi dental events news",
        "dental open house Udupi"
    ]
    
    found_results = []
    
    with st.spinner('Scanning the entire web for Udupi dental updates...'):
        with DDGS() as ddgs:
            for q in queries:
                # We search the web
                results = ddgs.text(q, max_results=8)
                for r in results:
                    content = (r['title'] + r['body']).lower()
                    
                    # LOCATION FILTER: Must mention Udupi or Manipal
                    if "udupi" in content or "manipal" in content:
                        # Ensure it's not a duplicate
                        if r['href'] not in [res['link'] for res in found_results]:
                            found_results.append({
                                "title": r['title'],
                                "link": r['href'],
                                "desc": r['body']
                            })
    return found_results

if st.button('🔍 Live Search for Dental Events in Udupi'):
    data = search_events()
    
    if data:
        st.success(f"Found {len(data)} potential updates!")
        for item in data:
            # We use expanders to keep the list clean
            with st.expander(item['title']):
                st.write(f"**Snippet from web:** {item['desc']}")
                st.markdown(f"[**Visit Website / View Details**]({item['link']})")
    else:
        st.error("No recent events found. Try again in a few days!")

st.sidebar.markdown("""
### What this finds:
* **Modules:** 2-day, 3-day, or 5-day workshops.
* **Courses:** Longer 2-6 week implant training.
* **Events:** IDA meetings, Open Houses, and CDE programs.
* **Location:** Strictly filtered for **Udupi** and **Manipal**.
""")