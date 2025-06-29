import requests
from datetime import datetime

# --- Prompt user for date input ---
date_str = input("Enter race date (YYYY-MM-DD): ")
date_input = datetime.strptime(date_str, "%Y-%m-%d")

# --- Replace this function to manually provide course selection ---
def fetch_available_courses_api(date):
    formatted_date = date.strftime('%Y-%m-%d')
    url = "https://the-racing-api1.p.rapidapi.com/v1/racecards/free"
    headers = {
        "x-rapidapi-host": "the-racing-api1.p.rapidapi.com",
        "x-rapidapi-key": "cc9b94ab41mshe6d1842b43bf287p1d886ejsn789e8e018289"
    }
    params = {
        "day": formatted_date,
        "region_codes": "gb"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        courses = {}
        for meeting in data.get("data", []):
            name = meeting.get("course_name")
            if name:
                courses[name] = meeting
        return courses
    except Exception as e:
        print(f"API error: {e}")
        return {}

# --- Display course options and accept user selection ---
available_courses = fetch_available_courses_api(date_input)
if not available_courses:
    print("No courses found for the selected date.")
    exit()

print("Available courses:")
for idx, course in enumerate(available_courses.keys(), start=1):
    print(f"{idx}. {course}")

choice = int(input("Select a course by number: "))
COURSE = list(available_courses.keys())[choice - 1]
print(f"\n✅ You selected: {COURSE}\n")
