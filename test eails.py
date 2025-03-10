import requests

url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/delete/id/%7Bmail_id%7D/"

headers = {
	"X-RapidAPI-Key": "",
	"X-RapidAPI-Host": "privatix-temp-mail-v1.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

print(response.json())
