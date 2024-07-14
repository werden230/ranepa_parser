import requests
import json
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def get_html():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
               "Cookie": "after-auth-ou=wait; BITRIX_SM_GUEST_ID=2461087; _ym_uid=1720522536423781435; _ym_d=1720522536; __lhash_=f1ab5267a83a7e10ffb885d02540b7af; BITRIX_SM_GUEST_ID=2461087; BX_USER_ID=d6d83a5228c99cc3df8b1812fcd0a47c; BITRIX_SM_LAST_ADV=5; PHPSESSID=BW8UUH1J8dF3vj4xyy42OH0kbGfsx5S7; BITRIX_CONVERSION_CONTEXT_s1=%7B%22ID%22%3A5%2C%22EXPIRE%22%3A1720817940%2C%22UNIQUE%22%3A%5B%22conversion_visit_day%22%5D%7D; _ym_isad=1; BITRIX_SM_LAST_VISIT=12.07.2024%2008%3A24%3A35; _gcl_au=1.1.1810266909.1720766179; _ga=GA1.2.1175785033.1720766179; _gid=GA1.2.1403872629.1720766179; BITRIX_CONVERSION_CONTEXT_s1=%7B%22ID%22%3A5%2C%22EXPIRE%22%3A1720817940%2C%22UNIQUE%22%3A%5B%22conversion_visit_day%22%5D%7D; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F126.0.0.0%20Safari%2F537.36; _ym_visorc=w; BITRIX_SM_LAST_VISIT=12.07.2024%2011%3A21%3A07; __js_p_=471,1800,0,0,0; __jhash_=1100; __hash_=cc471546a7456f68177035f179644421"
               }
    # url = "https://my.ranepa.ru/online/pk/list/list.php?FT=3&FL=0&FK=&FC=&FB=&FO=&F1=3dfc1680-5eff-4887-a318-288990d0e055&F2=66fef4e2-c613-11e5-80e4-005056a00b6e&F3=fa158c88-0d46-11ef-b514-00155da4ec08&F4=32e2ec09-5ac0-11ed-a2df-149ecf4cb249"
    url = "https://my.ranepa.ru/online/pk/list/list.php?FT=1&FL=0&FK=&FC=&FB=&FO=&F1=3dfc1680-5eff-4887-a318-288990d0e055&F2=66fef4e2-c613-11e5-80e4-005056a00b6e&F3=fa158c88-0d46-11ef-b514-00155da4ec08&F4=32e2ec09-5ac0-11ed-a2df-149ecf4cb249"
    res = requests.get(url=url, headers=headers)

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(str(datetime.now().strftime('%d/%m/%y %H:%M:%S.%f'))+"\n")
        file.write(res.text)

    return res.text


def parse():
    html = get_html()
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("tbody")
    raw_data_list = table.find_all("tr")[1::2]
    data = []
    for item in raw_data_list:
        name = item.find("td", class_="text-field").text.strip()
        raw_data = item.find_all("td", attrs={"style": "text-align:center"})[1:]
        original = raw_data[-1].text.strip() == "Оригинал"
        qwota = raw_data[0].text.split("/")[-1]
        qwota = "  " if qwota not in ("ОК", "ОТК", "БВИ", "ЦО") else qwota
        ID, math, it, soc, rus = [int(i.text) for i in raw_data[1:6]]
        points_sum = sum((ID, math, it, soc, rus)) - min((it, soc))
        priority = int(raw_data[6].text)
        data.append({"name": name, "points": points_sum, "qwota": qwota, "priority": priority, "original": original,
                     "rus": rus, "math": math, "other": max((it, soc))})
    data.sort(key=lambda x: (x['points'], x["math"], x["other"], x["rus"]), reverse=True)
    with open("data.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(data))


def main():
    creation_time = datetime.fromtimestamp(os.path.getmtime("data.json"))
    now = datetime.now()
    delta = now - creation_time
    if (now - creation_time) > timedelta(hours=1):
        parse()
    with open("data.json", "r", encoding="utf-8") as file:
        data = json.loads(file.read())
        file.close()
    i = 1
    for item in data:
        if item["qwota"] != '  ':
            print(f"#{i}", item["name"], item["points"], item["priority"], item["qwota"], item["original"], sep=" | ")
            i += 1


if __name__ == "__main__":
    main()