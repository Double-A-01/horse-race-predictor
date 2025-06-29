import streamlit as st
from datetime import datetime
import requests

(date):
    formatted_date = date.strftime('%Y-%m-%d')
    url = "https://the-racing-api1.p.rapidapi.com/v1/racecards/free"
    headers = {
        "x-rapidapi-host": "the-racing-api1.p.rapidapi.com",
        "x-rapidapi-key": "cc9b94ab41mshe6d1842b43bf287p1d886ejsn789e8e018289"
    }
    params = {
        "day": formatted_date,
        "region_codes": '"gb"'
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        races = []
        for meeting in data.get("data", []):
            if meeting.get("course_name") == COURSE:
                for race in meeting.get("races", []):
                    races.append({
                        "race_time": race.get("race_time"),
                        "race_id": race.get("race_id"),
                        "title": race.get("race_title"),
                        "distance": race.get("distance"),
                        "age_restriction": race.get("age_restriction"),
                        "url": race.get("racecard_url")
                    })
        return races
    except Exception as e:
        st.error(f"Error loading racecard links: {e}")
        return []

# --- UI Inputs (must appear before use) ---
date_input = st.date_input("Select race date", value=datetime.today())
available_courses = fetch_available_courses_api(date_input)
if not available_courses:
    st.warning("No courses found for the selected date.")
    st.stop()
COURSE = st.selectbox("Select racecourse", list(available_courses.keys()))

# --- Display available races for selected course and date ---
race_links = fetch_racecard_links(date_input)
if race_links:
    st.subheader(f"Races at {COURSE} on {date_input.strftime('%Y-%m-%d')}")
    st.dataframe(race_links)
else:
    st.warning("No races found for the selected course and date.")

# [Your existing functions like parse_race, process_scraped_race, etc. continue below without change...]
