import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from search_service import SearchService

st.set_page_config(page_title="Udupi Dental Tracker", page_icon="🦷", layout="wide")


@st.cache_resource
def service():
    folder = Path(os.environ.get("DENTAL_DATA_DIR", str(Path(__file__).parent / "data")))
    return SearchService(folder / "listings.json")


def timestamp(value):
    return datetime.fromtimestamp(value, timezone.utc).strftime("%d %b %Y, %H:%M UTC")


st.title("🦷 Udupi & Manipal Dental Course Tracker")
st.write("Find dental courses, conferences and workshops. Successful listings are saved for later visits.")
st.caption("These are search leads, including possible past events. Confirm dates, location and registration with the organiser.")
engine = service()
left, right = st.columns(2)
normal = left.button("🔍 Search / Show saved listings", use_container_width=True)
force = right.button("Check for new listings", use_container_width=True)
st.caption("Saved searches are reused for one hour. Checking for new listings is limited to once every 10 minutes across this server.")

# Keep status separate from the saved-listings display.
status = st.empty()
listing_area = st.empty()


def render():
    snapshot = engine.snapshot()
    results = snapshot["results"]
    with listing_area.container():
        if not results:
            st.info("No saved listings yet. Run a search. If the provider is unavailable, use the direct search links below.")
            return
        st.success(f"{len(results)} saved listings")
        st.caption("Last search that found matches: " + timestamp(snapshot["last_success"]))
        if snapshot["issues"]:
            st.warning("The last refresh was incomplete. Saved listings are still shown.")
        text = "🦷 Udupi & Manipal dental listings — verify event dates\n\n" + "\n\n".join(
            f"{r['title']}\n{r['link']}" for r in results[:5])
        a, b = st.columns(2)
        a.link_button("Share top 5 via WhatsApp", "https://wa.me/?text=" + quote(text))
        b.link_button("Share top 5 via email", "mailto:?subject=" + quote("Dental courses Udupi") + "&body=" + quote(text))
        st.download_button("Download all listings", "\n\n".join(
            f"{r['title']}\n{r['link']}\nLast found: {timestamp(r['last_seen'])}\n{r['desc']}" for r in results),
            file_name="dental-listings.txt", mime="text/plain")
        for item in results:
            st.subheader(item["title"])
            st.write(item["desc"])
            st.caption("Last found in search: " + timestamp(item["last_seen"]))
            st.link_button("Open listing", item["link"])
            st.divider()


if normal or force:
    with st.spinner("Checking search sources. This can take about a minute or longer if providers are slow."):
        message = engine.refresh(force=force)
    status.info(message)
render()

with st.expander("Direct searches and search status"):
    st.write("These open your browser; they are not verified event listings.")
    for label, query in [("Dental events in Udupi / Manipal", "dental workshop conference Udupi Manipal"),
                         ("MCODS official website search", "site:manipal.edu mcods manipal CDE workshop")]:
        st.link_button(label, "https://www.google.com/search?q=" + quote(query))
    for issue in engine.snapshot()["issues"]:
        st.text(issue)
