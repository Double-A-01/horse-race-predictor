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
