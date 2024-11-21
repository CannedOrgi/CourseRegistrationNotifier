import requests
import bs4
import time
import winsound
token = '7632158464:AAGCd0REs-kDMnEXq2w0jEM-s1O2MvhPOdA'
chat_id = '2109350821'

duration = 1500  #milliseconds
freq = 440  

def sendMessage(message):
    url1 = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {
                    'chat_id': chat_id,
                    'text': message
                }

    response = requests.post(url1, data=payload)

url = "https://academic.iitg.ac.in//sso/gen/student1.jsp"

r = requests.post(url, data={"cid": "EE 605", "sess": "Jan-May", "yr": "2025"})
soup = bs4.BeautifulSoup(r.text, "html.parser")
embedded = []

tr = soup.findAll('tr')
for t in tr[1:]:
    trr = t.findAll('td')
    name = trr[1].contents[0]
    test = trr[2].contents[0]
    embedded.append(name + ", " + test)
print("EE 605 full") if len(embedded)==120 else print(f"EE 605 has {120-len(embedded)} spot left!")

r = requests.post(url, data={"cid": "EE 621", "sess": "Jan-May", "yr": "2025"})
soup = bs4.BeautifulSoup(r.text, "html.parser")
formal = []
tr = soup.findAll('tr')
for t in tr[1:]:
    trr = t.findAll('td')
    name = trr[1].contents[0]
    test = trr[2].contents[0]
    formal.append(name + ", " + test)

print("EE 621 full") if len(formal)==105 else print(f"EE 621 has {105-len(formal)} spot left!")

r = requests.post(url, data={"cid": "EE 659", "sess": "Jan-May", "yr": "2025"})
soup = bs4.BeautifulSoup(r.text, "html.parser")
iot = []

tr = soup.findAll('tr')
for t in tr[1:]:
    trr = t.findAll('td')
    name = trr[1].contents[0]
    test = trr[2].contents[0]
    iot.append(name + ", " + test)
print("EE 659 full") if len(iot)==80 else print(f"EE 659 has {80-len(iot)} spot left!")
fsm = 1

while True:
    if fsm == 1:
        r = requests.post(url, data={"cid": "EE 605", "sess": "Jan-May", "yr": "2025"})
        soup = bs4.BeautifulSoup(r.text, "html.parser")

        embedded1 = []

        tr = soup.findAll('tr')
        for t in tr[1:]:
            trr = t.findAll('td')
            name = trr[1].contents[0]
            test = trr[2].contents[0]
            last = name + ", " + test
            embedded1.append(last)
            if last not in embedded:
                message1 = last + " registered for EE 605!!!"
                print(last + " registered for EE 605!!!")
                sendMessage(message1)

            
                #winsound.Beep(freq, duration)
            else:
                embedded.remove(last)

        for _ in embedded:
            message2 = _ + " de-registered for EE 605!!!"
            print(message2)
            sendMessage(message2)
            winsound.Beep(freq, duration)

        embedded = embedded1
        fsm = 2

    elif fsm == 2:
        r = requests.post(url, data={"cid": "EE 621", "sess": "Jan-May", "yr": "2025"})
        soup = bs4.BeautifulSoup(r.text, "html.parser")

        formal1 = []

        tr = soup.findAll('tr')
        for t in tr[1:]:
            trr = t.findAll('td')
            name = trr[1].contents[0]
            test = trr[2].contents[0]
            last = name + ", " + test
            formal1.append(last)
            if last not in formal:
                message3 = last + " registered for EE 621!!!"
                print(message3)
                sendMessage(message3)
                winsound.Beep(freq, duration)
            else:
                formal.remove(last)

        for _ in formal:
            print(_ + " de-registered for EE 621!!!")
            sendMessage(_ + " de-registered for EE 621!!!")
            winsound.Beep(freq, duration)

        formal = formal1
        fsm = 3

    else:
        r = requests.post(url, data={"cid": "EE 659", "sess": "Jan-May", "yr": "2025"})
        soup = bs4.BeautifulSoup(r.text, "html.parser")

        iot1 = []

        tr = soup.findAll('tr')
        for t in tr[1:]:
            trr = t.findAll('td')
            name = trr[1].contents[0]
            test = trr[2].contents[0]
            last = name + ", " + test
            iot1.append(last)
            if last not in iot:
                print(last + " registered for EE 659!!!")
                sendMessage(last + " registered for EE 659!!!")
                winsound.Beep(freq, duration)
            else:
                iot.remove(last)

        for _ in iot:
            print(_ + " de-registered for EE 659!!!")
            sendMessage(_ + " de-registered for EE 659!!!")
            winsound.Beep(freq, duration)

        iot = iot1
        fsm = 1

    time.sleep(1)
