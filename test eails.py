import requests

url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/delete/id/%7Bmail_id%7D/"

headers = {
	"X-RapidAPI-Key": "a66cd04b83mshf9dc611913c244dp11dd70jsn8d2ebb3791d1",
	"X-RapidAPI-Host": "privatix-temp-mail-v1.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

print(response.json())