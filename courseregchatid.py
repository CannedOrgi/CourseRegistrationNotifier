import requests

# Replace with your bot token
token = '7632158464:AAGCd0REs-kDMnEXq2w0jEM-s1O2MvhPOdA'
url = f'https://api.telegram.org/bot{token}/getUpdates'

# Make a request to Telegram API
response = requests.get(url)
data = response.json()

# Print the raw data to inspect all updates
print(data)
