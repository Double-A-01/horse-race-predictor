def fetch_racecard_links(date):
    date_path = date.strftime('%Y-%m-%d').replace('-', '/')
    base_url = f"https://www.racingpost.com/racecards/{date_path}/"
    html = get_html(base_url)
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for link in soup.select('a.rc-meeting-item__link'):
        link_text = link.get_text(strip=True).lower()
        course_clean = COURSE.lower()
        if course_clean in link_text:
            full_url = "https://www.racingpost.com" + link['href']
            links.append(full_url)
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

# --- STREAMLIT UI CONTINUED ---
try:
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
