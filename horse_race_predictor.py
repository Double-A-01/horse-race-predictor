# horse_race_predictor.py (Enhanced with Web Scraping, Results, Storage, Form Analysis)

import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import streamlit as st
from bs4 import BeautifulSoup
import re
import time
import random
import os

# --- CONFIGURATION ---
COURSE = "Carlisle"
DRAW_BIAS = {i: 0 for i in range(1, 21)}
STORAGE_PATH = "race_results.csv"

WEIGHTS = {
    "form": 0.4,
    "cd_record": 5,
    "trainer_jockey": 10,
    "going": 3,
    "draw": 1,
    "freshness": 2,
    "or_trend": 2,
    "odds": 2
}

# --- UTILITY FUNCTIONS ---
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

def implied_prob(odds_str):
    try:
        f = re.findall(r'(\d+)/(\d+)', odds_str)
        if f:
            return float(f[0][1]) / (float(f[0][0]) + float(f[0][1]))
    except:
        return 0
    return 0

def enhanced_form_score(form_str):
    clean_form = re.sub(r'[^0-9]', '', form_str[-3:])
    score = sum(10 - int(ch)*2 for ch in clean_form if ch.isdigit())
    return score

# --- SCRAPER FUNCTIONS ---
def fetch_racecard_links(date):
    date_path = date.strftime('%Y-%m-%d').replace('-', '/')
    base_url = f"https://www.racingpost.com/racecards/{date_path}/"
    html = get_html(base_url)
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.select('a.rc-meeting-item__link'):
        if COURSE.lower() in link.text.lower():
            links.append("https://www.racingpost.com" + link['href'])
    return links

def parse_race(race_url):
    html = get_html(race_url)
    soup = BeautifulSoup(html, 'html.parser')
    race_title = soup.select_one('h2.racecardHeader__title')
    going_tag = soup.select_one('span.raceTimeCourseName__going')
    table = soup.select_one('table.racecardTable')
    if not race_title or not going_tag or not table:
        return []
    race_title = race_title.text.strip()
    going_text = going_tag.text.strip()
    runners = []
    for row in table.select('tbody tr'):
        try:
            horse = row.select_one('a.rc-horse-name').text.strip()
            odds = row.select_one('td.rc-odds').text.strip()
            form = row.select_one('span.formline').text.strip()
            trainer = row.select_one('a.rc-trainer-name').text.strip()
            jockey = row.select_one('a.rc-jockey-name').text.strip()
            draw_cell = row.select_one('td.draw')
            draw = int(draw_cell.text.strip()) if draw_cell and draw_cell.text.strip().isdigit() else 0
            pos_tag = row.select_one('td.pos')
            position = pos_tag.text.strip() if pos_tag and pos_tag.text.strip().isdigit() else ""
            runners.append({
                "horse": horse,
                "odds": odds,
                "form": form,
                "trainer": trainer,
                "jockey": jockey,
                "draw": draw,
                "going": going_text,
                "race": race_title,
                "position": position
            })
        except Exception as e:
            print(f"Error parsing runner row: {e}")
            continue
    return runners

def score_runner(runner):
    score = 0
    score += runner['form_score'] * WEIGHTS['form']
    score += DRAW_BIAS.get(runner['draw'], 0) * WEIGHTS['draw']
    score += runner['implied_odds'] * 100 * WEIGHTS['odds']
    return score

def process_scraped_race(runners):
    for r in runners:
        r['form_score'] = enhanced_form_score(r['form'])
        r['implied_odds'] = implied_prob(r['odds'])
        r['score'] = score_runner(r)
        r['won'] = 1 if r['position'] == '1' else 0
        r['top3'] = 1 if r['position'] in ['1','2','3'] else 0
    return pd.DataFrame(runners).sort_values("score", ascending=False)

def store_results(df):
    try:
        if not os.path.exists(STORAGE_PATH):
            df.to_csv(STORAGE_PATH, index=False)
        else:
            df.to_csv(STORAGE_PATH, mode='a', index=False, header=False)
    except Exception as e:
        print(f"Error storing results: {e}")

def plot_summary(df):
    try:
        if 'won' in df.columns:
            df[['won','top3']].mean().plot(kind='bar', title='Prediction Accuracy')
            plt.xticks(rotation=0)
            plt.ylim(0, 1)
            st.pyplot(plt.gcf())
    except Exception as e:
        st.write(f"Plotting error: {e}")

def show_overall_summary():
    try:
        if os.path.exists(STORAGE_PATH):
            all_data = pd.read_csv(STORAGE_PATH)
            summary = all_data.groupby('horse')[['score', 'won', 'top3']].mean().sort_values('score', ascending=False)
            st.subheader("Summary of All Predictions")
            st.dataframe(summary.reset_index())
    except Exception as e:
        st.write(f"Summary load error: {e}")

# --- STREAMLIT UI ---
st.title("Horse Race Predictor (Web-Scraped + Historical Analysis)")

try:
    date_input = st.date_input("Select race date", value=datetime.today())
    links = fetch_racecard_links(date_input)

    if not links:
        st.warning("No racecards found for that course/date.")

    for link in links:
        st.markdown(f"### [{link}]({link})")
        data = parse_race(link)
        if not data:
            st.info("No data found or failed to parse race.")
            continue
        df = process_scraped_race(data)
        st.dataframe(df[['horse','score','odds','form','draw','position']].reset_index(drop=True))
        store_results(df)
        plot_summary(df)
        st.markdown("---")

    show_overall_summary()

except Exception as e:
    st.error(f"An error occurred: {e}")
