import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from bs4 import BeautifulSoup
import re
import time
import random
import os

# --- STREAMLIT UI (Date & Course Selection) ---
st.title("Horse Race Predictor")
date_input = st.date_input("Select race date", value=datetime.today())

@st.cache_data(show_spinner=False)
def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        time.sleep(random.uniform(1, 2))
        return response.text
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return ""

def fetch_available_courses(date):
    date_path = date.strftime('%Y-%m-%d').replace('-', '/')
    base_url = f"https://www.racingpost.com/racecards/{date_path}/"
    html = get_html(base_url)
    if not html:
        print("No HTML returned from Racing Post.")
        return {}
    soup = BeautifulSoup(html, 'html.parser')
    courses = {}
    for meeting in soup.select('div.rc-meeting-item__container'):
        link = meeting.find('a', href=True)
        if not link:
            continue
        course_name = meeting.select_one('.rc-meeting-item__title')
        if course_name:
            name = course_name.text.strip()
            full_url = "https://www.racingpost.com" + link['href']
            courses[name] = full_url
    print(f"Found courses: {list(courses.keys())}")
    return courses

available_courses = fetch_available_courses(date_input)
if not available_courses:
    st.warning("No courses found for the selected date.")
    st.stop()
COURSE = st.selectbox("Select racecourse", list(available_courses.keys()))

# The rest of your existing code remains below...

def fetch_racecard_links(date):
    date_path = date.strftime('%Y-%m-%d')
    course_url = available_courses.get(COURSE)
    if not course_url:
        return []
    html = get_html(course_url)
    if not html:
        print("Failed to load course page.")
        return []
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.select('a.racecard__time-link[href*="/racecards/"]'):
        href = link.get('href')
        if href and '/racecards/' in href:
            full_url = "https://www.racingpost.com" + href
            links.append(full_url)
    return links

# [Your existing functions like parse_race, process_scraped_race, etc. continue below without change...]
