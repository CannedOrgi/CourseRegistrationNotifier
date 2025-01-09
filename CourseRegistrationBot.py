import requests
import bs4
import time
import re

token = '7632158464:AAGCd0REs-kDMnEXq2w0jEM-s1O2MvhPOdA'
base_url = f'https://api.telegram.org/bot{token}'
update_url = f'{base_url}/getUpdates'

user_states = {} 
last_update_id = None  
course_states = {} 
fsm_index = 0
courses_to_check = [] 


def send_message(chat_id, text):
    url = f'{base_url}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=payload)

def fetch_updates():
    global last_update_id
    params = {'offset': last_update_id + 1} if last_update_id else {}
    response = requests.get(update_url, params=params)
    return response.json().get('result', [])

def check_course_updates():
    global fsm_index, courses_to_check, course_states

    # Safeguard: Skip if courses_to_check is empty
    if not courses_to_check:
        print("No courses to check.")
        return

    # Adjust fsm_index if it is out of bounds
    if fsm_index >= len(courses_to_check):
        fsm_index = 0  # Reset to the start of the list

    # Safely get the current course ID
    course_id = courses_to_check[fsm_index]

    # Fetch course updates from the website
    url = "https://academic.iitg.ac.in/sso/gen/student1.jsp"
    response = requests.post(url, data={"cid": course_id, "sess": "Jan-May", "yr": "2025"})
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    current_students = []
    for tr in soup.find_all('tr')[1:]:
        tds = tr.find_all('td')
        name = tds[1].text.strip()
        test = tds[2].text.strip()
        student_info = f"{name}, {test}"
        current_students.append(student_info)

    # Compare with previous state
    previous_students = course_states.get(course_id, [])
    added_students = [s for s in current_students if s not in previous_students]
    removed_students = [s for s in previous_students if s not in current_students]

    # Notify users about updates
    if previous_students:
        for user_state in user_states.values():
            if user_state['state'] == 'active' and course_id in user_state['courses']:
                chat_id = user_state['chat_id']
                for student in added_students:
                    send_message(chat_id, f"{student} registered for {course_id}!")
                for student in removed_students:
                    send_message(chat_id, f"{student} de-registered from {course_id}!")

    # Update the state
    course_states[course_id] = current_students

    # Safely update FSM index for the next course
    if courses_to_check:
        fsm_index = (fsm_index + 1) % len(courses_to_check)

while True:
    updates = fetch_updates()
    for update in updates:
        print("UPDATE:", update)
        last_update_id = update["update_id"]
        if "message" not in update:
            continue

        chat_id = update["message"]["chat"]["id"]
        name = update["message"]["chat"]["first_name"]
        message_id = update["message"]["message_id"]
        text = update["message"].get("text", "").strip()
        
        if chat_id not in user_states:
            user_states[chat_id] = {
                "chat_id": chat_id,
                "state": "awaiting_roll",
                "roll": None,
                "courses": [],
                "last_message_id": message_id
            }
            send_message(chat_id, f"Hello {name}, please enter your roll number.")
            continue

        user_state = user_states[chat_id]
        if text.lower() == 'yes' and user_state["state"]=='active':
            send_message(chat_id, "Please enter the course(s) you want updates for (comma-separated).")
            user_state["state"] = "awaiting_course"
            user_state["last_message_id"] = message_id
            continue
        print(user_state["state"])

        
        if text and user_state["state"] == "awaiting_roll":
            user_state["roll"] = text
            user_state["state"] = "awaiting_course"
            user_state["last_message_id"] = message_id
            send_message(chat_id, "Now please enter the course(s) you want updates for (comma-separated).")
            continue

        elif text and user_state["state"] == "awaiting_course":
            courses_requested = [course.strip() for course in text.split(",")]
            def normalize_course(course):
                match = re.match(r"([a-zA-Z]+)\s*(\d+)", course)
                if match:
                    prefix = match.group(1).upper()
                    number = match.group(2)
                    return f"{prefix} {number}"
                return course

            valid_courses = [normalize_course(course) for course in courses_requested]
            user_state["courses"] = valid_courses
            print(user_state["courses"])
            user_state["state"] = "active"
            user_state["last_message_id"] = message_id

            send_message(chat_id, f"You are now subscribed to updates for: {', '.join(valid_courses)}.")
            continue

        elif not text and user_state["state"] !="active":
            send_message(chat_id, "Sorry, please enter it again")
            user_state["last_message_id"] = message_id
            continue

        elif user_state["state"] =="active":
            user_state["last_message_id"] = message_id
            send_message(chat_id, "If you would like to change the list of courses you want updates for, please say 'yes'. Otherwise, please wait for updates.")

    print(f"user states: {user_states}")

    courses_to_check_set = set()
    for user_state in user_states.values():
        if user_state.get('state') == 'active':
            courses_to_check_set.update(user_state["courses"])
    courses_to_check = list(courses_to_check_set)

    if courses_to_check:
        check_course_updates()

    time.sleep(1) 
