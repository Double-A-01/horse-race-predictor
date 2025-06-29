import streamlit as st
from datetime import datetime
import requests
import time
import random
from bs4 import BeautifulSoup

# Utility function to fetch HTML
def get_html(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        time.sleep(random.uniform(1, 2))
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

# Add date input before calling fetch_available_courses
date_input = st.date_input("Select race date", value=datetime.today())

def fetch_available_courses(date):
    date_path = date.strftime('%Y-%m-%d').replace('-', '/')
    base_url = f"https://www.racingpost.com/racecards/{date_path}/"
    html = get_html(base_url)
    if not html:
        print("No HTML returned from Racing Post.")
        return {}
    soup = BeautifulSoup(html, 'html.parser')
    courses = {}
    for link in soup.select('a.rc-meeting-item__link[href]'):
        href = link['href']
        name = link.get_text(strip=True)
        full_url = "https://www.racingpost.com" + href
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
