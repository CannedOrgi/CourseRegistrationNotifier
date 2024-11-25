import requests
import bs4
import time

token = '7632158######A'
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

    if not courses_to_check:
        return

    course_id = courses_to_check[fsm_index]

 
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

   
    previous_students = course_states.get(course_id, [])
    if previous_students:
        print('yesss')
    elif not previous_students:
        print("NOO")
    added_students = [s for s in current_students if s not in previous_students]
    removed_students = [s for s in previous_students if s not in current_students]

    if previous_students:
        for user_state in user_states.values():
            if user_state['state'] == 'active' and course_id in user_state['courses']:
                chat_id = user_state['chat_id']
                for student in added_students:
                    send_message(chat_id, f"{student} registered for {course_id}!")
                for student in removed_students:
                    send_message(chat_id, f"{student} de-registered from {course_id}!")

    course_states[course_id] = current_students

    fsm_index = (fsm_index + 1) % len(courses_to_check)
while True:
    updates = fetch_updates()
    for update in updates:
        last_update_id = update["update_id"]
        if "message" not in update:
            continue

        chat_id = update["message"]["chat"]["id"]
        message_id = update["message"]["message_id"]
        text = update["message"].get("text", "").strip()
        print(f"message_id = {message_id}")
        
        if chat_id not in user_states:
            user_states[chat_id] = {
                "chat_id": chat_id,
                "state": "awaiting_roll",
                "roll": None,
                "courses": [],
                "last_message_id": message_id
            }
            send_message(chat_id, "Hello! Please enter your roll number.")
            continue

        user_state = user_states[chat_id]
        print(user_state["state"])

        
        if message_id == user_state.get("last_message_id", 0) + 2 and user_state["state"] == "awaiting_roll":
            user_state["roll"] = text
            user_state["state"] = "awaiting_course"
            user_state["last_message_id"] = message_id
            send_message(chat_id, "Thank you! Please enter the course(s) you want updates for (comma-separated).")
            continue

        if message_id == user_state.get("last_message_id", 0) + 2 and user_state["state"] == "awaiting_course":
            courses_requested = [course.strip() for course in text.split(",")]
            valid_courses = [course for course in courses_requested]
            user_state["courses"] = valid_courses
            print(user_state["courses"])
            user_state["state"] = "active"
            user_state["last_message_id"] = message_id

            send_message(chat_id, f"You are now subscribed to updates for: {', '.join(valid_courses)}.")

        else:
            user_state["last_message_id"] = message_id
            send_message(chat_id, "I'm not sure what you're trying to do. Please wait for updates.")

    print(f"user states: {user_states}")

    courses_to_check_set = set()
    for user_state in user_states.values():
        if user_state.get('state') == 'active':
            courses_to_check_set.update(user_state["courses"])
    courses_to_check = list(courses_to_check_set)

    if courses_to_check:
        check_course_updates()

    time.sleep(1) 
