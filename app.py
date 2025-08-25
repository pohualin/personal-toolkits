import streamlit as st
import sys
from src.util.twitter_downloader import download_twitter_video
from src.util.youtube_util import search_youtube
from src.util.google_sheet_util import read_sheet
from scripts.twitter.dl_from_sheet import main as dl_from_sheet_main

st.title("Personal Toolkits UI")

st.header("Download Twitter Video")
twitter_url = st.text_input("Twitter Video URL")
if st.button("Download Twitter Video"):
    if twitter_url:
        download_twitter_video(twitter_url)
        st.success("Download started!")
    else:
        st.error("Please enter a Twitter video URL.")

# st.header("Search YouTube Channel")
# yt_handle = st.text_input("YouTube Channel Handle")
# last_x_days = st.number_input("Last X Days", min_value=1, max_value=30, value=7)
# if st.button("Search YouTube"):
#     if yt_handle:
#         videos = search_youtube(yt_handle, last_x_days)
#         for v in videos:
#             st.write(f"{v['title']} ({v['published']})")
#     else:
#         st.error("Please enter a YouTube channel handle.")

st.header("Read Google Sheet")
spreadsheet_id = st.text_input("Spreadsheet ID")
range_name = st.text_input("Range (e.g., Sheet1!A1:A10)")
if st.button("Read Sheet"):
    if spreadsheet_id and range_name:
        rows = read_sheet(spreadsheet_id, range_name)
        st.write(rows)
    else:
        st.error("Please enter both Spreadsheet ID and Range.")

st.header("Download Twitter Videos from Google Sheet")
if st.button("Download from Sheet"):
    # You may need to refactor dl_from_sheet.main to accept arguments
    sys.argv = ["dl_from_sheet.py"]
    dl_from_sheet_main()
    st.success("Download from sheet started!")