from os import listdir
import os
import sys
import json
import re
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from pprint import pprint
from selenium import webdriver
import requests
import shutil
from dotenv import load_dotenv

# 到時候改成py檔再放回去，記得改'administrative_district.txt'成filename
# current_dir = os.path.dirname(os.path.abspath(__file__))
# filename = os.path.join(current_dir, 'administrative_district.txt')

with open('administrative_district.txt', "r", encoding='utf-8') as fn:
    city_name, district, chinese_input_date = [
        i.strip() for i in fn.readlines()]
print(city_name, district, chinese_input_date)

load_dotenv()


def get_weather_api():
    '''
    取得下載網址
    '''
    # 氣象局資料集代碼對應表
    city_to_dataset = {
        "基隆市": "F-D0047-051",
        "臺北市": "F-D0047-063",
        "台北市": "F-D0047-063",
        "新北市": "F-D0047-071",
        "桃園市": "F-D0047-007",
        "新竹市": "F-D0047-055",
        "新竹縣": "F-D0047-011",
        "苗栗縣": "F-D0047-015",
        "臺中市": "F-D0047-075",
        "台中市": "F-D0047-075",
        "彰化縣": "F-D0047-019",
        "南投縣": "F-D0047-023",
        "雲林縣": "F-D0047-027",
        "嘉義市": "F-D0047-059",
        "嘉義縣": "F-D0047-031",
        "臺南市": "F-D0047-079",
        "台南市": "F-D0047-079",
        "高雄市": "F-D0047-067",
        "屏東縣": "F-D0047-035",
        "宜蘭縣": "F-D0047-003",
        "花蓮縣": "F-D0047-043",
        "臺東縣": "F-D0047-039",
        "台東縣": "F-D0047-039",
        "澎湖縣": "F-D0047-047",
        "金門縣": "F-D0047-087",
        "連江縣": "F-D0047-083"
    }

    # 固定 API 前綴(Base URL)與授權碼
    api_prefix = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/"
    # 去這裡 https://opendata.cwa.gov.tw/user/authkey  先登入會員再取得授權碼
    authorization = f"{os.getenv("weather_api")}"

    while True:
        # 查找使用者輸入的資料集代碼
        dataset_id = city_to_dataset.get(city_name)
        if dataset_id:
            # 組合完整 API URL
            api_url = f"{api_prefix}{dataset_id}?Authorization={
                authorization}&downloadType=WEB&format=JSON"
            return city_name, api_url
        else:
            print("你有設定過縣市了嗎?沒有的話先去設定!🤣🤣")
            sys.exit()


def download_weather_data(url, city_name):
    """
    根據 URL 下載天氣資料並儲存到桌面資料夾
    """
    # 取得使用者的桌面路徑並創建資料夾
    desktop_path = os.path.expanduser("~\\Desktop")
    save_folder = os.path.join(desktop_path, "weather_data")

    # 如果桌面沒有weather_data的資料，就當個創世神吧！ 有的話就什麼都不做
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # 構建檔案儲存路徑，使用縣市名稱命名檔案
    save_file = os.path.join(save_folder, f"{city_name}_weather_data.json")

    # 發送 HTTP 請求下載文件
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_file, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)  # 將檔案內容寫入指定位置
        print(f"檔案已成功下載至 {save_file}")
    else:
        print("下載失敗，狀態碼:", response.status_code)
        sys.exit()


def import_weather_data(city_name):
    """
    導入下載的天氣資料並返回資料
    """
    desktop_path = os.path.expanduser("~\\Desktop")
    save_folder = os.path.join(desktop_path, "weather_data")
    save_file = os.path.join(save_folder, f"{city_name}_weather_data.json")

    if os.path.exists(save_file):
        try:
            # 讀取並解析 JSON 檔案
            with open(save_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
            print(f"檔案 {save_file} 成功載入")
            return data
        except Exception as e:
            print(f"讀取檔案時發生錯誤: {e}")
            sys.exit()
    else:
        print(f"檔案 {save_file} 不存在，請先下載資料")
        sys.exit()


def get_weather_data(chinese_input_date, location_name, weather_data):

    today = datetime.now().date()
    chinese_to_days = {
        "今天": 0,
        "明天": 1,
        "後天": 2,
        "三天後": 3,
        "四天後": 4,
        "五天後": 5,
        "六天後": 6,
        "七天後": 7
    }
    if chinese_input_date in chinese_to_days:
        input_date = today + \
            timedelta(days=chinese_to_days[chinese_input_date])
        today_date = input_date.strftime("%Y年%m月%d日")
    else:
        print('無效輸入')  # 表示無效輸入
        sys.exit()

    weather_information = {}
    # Location是key，對應的value是一個List，這樣會遍歷list裡所有的index
    for location in weather_data["cwaopendata"]["Dataset"]["Locations"]["Location"]:
        # 搜尋使用者輸入的行政區
        if location["LocationName"] == location_name:
            # weatherElement的value是一個list，會遍歷list所有內容
            for element in location["WeatherElement"]:
                # 尋找使用者輸入的時間
                # input_date = today + timedelta(days=chinese_to_days[chinese_input_date])
                for time in element["Time"]:
                    start_time = datetime.strptime(
                        time["StartTime"], "%Y-%m-%dT%H:%M:%S+08:00").date()
                    end_time = datetime.strptime(
                        time["EndTime"], "%Y-%m-%dT%H:%M:%S+08:00").date()

                    # 符合就返回特定時間的資料
                    if chinese_input_date == "今天":
                        if input_date <= end_time:
                            element_name = element["ElementName"]
                            value = time["ElementValue"]  # 提取ElementValue的值
                            # print(f"{element_name}:")
                            weather_information[element_name] = value
                            for key, val in value.items():
                                weather_information[key] = val
                            # print(f"  {key}: {val}")
                            # print("\n")

                    elif chinese_input_date == "七天後":
                        if input_date == end_time:
                            element_name = element["ElementName"]
                            value = time["ElementValue"]  # 提取ElementValue的值

                            # print(f"{element_name}:")
                            weather_information[element_name] = value
                            for key, val in value.items():
                                weather_information[key] = val
                            # print(f"  {key}: {val}")
                            # print("\n")

                    if start_time == input_date == end_time:
                        element_name = element["ElementName"]
                        value = time["ElementValue"]  # 提取ElementValue的值

                        # print(f"{element_name}:")
                        weather_information[element_name] = value
                        for key, val in value.items():
                            weather_information[key] = val
                            # print(f"  {key}: {val}")
                        # print("\n")
    # print(weather_information)
    weather_informations = {
        "日期": today_date,
        "平均溫度": weather_information.get('Temperature', ''),
        "最高溫度": weather_information.get('MaxTemperature', ''),
        "最低溫度": weather_information.get('MinTemperature', ''),
        "平均露點溫度": weather_information.get('DewPoint', ''),
        "平均相對濕度": weather_information.get('RelativeHumidity', ''),
        "最高體感溫度": weather_information.get('MaxApparentTemperature', ''),
        "最低體感溫度": weather_information.get('MinApparentTemperature', ''),
        "最大舒適度": weather_information.get('MaxComfortIndexDescription', ""),
        "最小舒適度": weather_information.get('MinComfortIndexDescription', ''),
        "風速": weather_information.get('WindSpeed', ''),
        "風向": weather_information.get('WindDirection', ''),
        "12小時降雨機率": weather_information.get('ProbabilityOfPrecipitation', ''),
        "天氣現象": weather_information.get('Weather', ''),
        "天氣預報綜合描述": weather_information.get('WeatherDescription', ''),
        '紫外線指數': weather_information.get('UVIndex', '')
    }
    # print(weather_informations)
    return weather_informations


def get_outfit_suggestions(weather_informations):
    suggestions = []

    try:
        uv_index = int(weather_informations['紫外線指數'])
    except:
        uv_index = None
        print('沒有紫外線指數的資料')
    try:
        temperature = int(weather_informations["平均溫度"])
    except:
        temperature = None
        print('沒有平均溫度的資料')
    try:
        humidity = int(weather_informations["平均相對濕度"])
    except:
        humidity = None
        print('沒有相對溼度的資料')
    try:
        rain_chance = int(weather_informations["12小時降雨機率"])
    except:
        rain_chance = None
        print('沒有降雨機率的資料')
    try:
        max_temp = int(weather_informations["最高溫度"])
    except:
        max_temp = None
        print('沒有最高溫度的資料')
    try:
        min_temp = int(weather_informations["最低溫度"])
    except:
        min_temp = None
        print('沒有最低溫度的資料')
    try:
        weather_descrip = weather_informations['天氣預報綜合描述']
    except:
        weather_descrip = None
        print('沒有天氣預報綜合描述的資料')

    if weather_descrip is not None:
        suggestions.append(f"{weather_informations['日期']} 天氣預測：")
    else:
        suggestions.append("❓ 找不到天氣預報綜合描述的資料，自己去google吧🤣")

    if temperature is not None:
        if temperature > 35:
            suggestions.append("🔥 天氣熱到彷彿站在火爐旁！短袖短褲是你的最佳夥伴，還可以選淺色衣服，當個清涼系代表！")
            suggestions.append("🔥 記得戴寬邊帽、酷炫太陽眼鏡，塗上防曬霜，讓自己成為行走的防曬廣告！")
        elif 30 <= temperature <= 35:
            suggestions.append(
                "☀️ 今天的天氣就是你，如此燦爛及耀眼；記得注意防曬，別讓你的皮膚受到受傷；也要補充水分，時時保持熱情活力！")
            suggestions.append("☀️ 拿件薄外套防冷氣突襲，畢竟辦公室冷氣常常自帶北極風效果。")
        elif 25 <= temperature < 30:
            suggestions.append("🌤️ 舒適得想去海邊浪一浪！短袖薄長袖隨你選，配上輕便長褲或裙子，怎麼穿都好看！")
            suggestions.append("🌤️ 早晚溫差有點調皮，隨身帶個薄外套，讓自己溫暖不尷尬。")
        elif 20 <= temperature < 25:
            suggestions.append("🌥️ 微涼微風，長袖衣物搭配輕薄外套，氣質滿分又不失溫暖～")
            suggestions.append("🌥️ 選件針織衫，走路帶風自帶文青氣息，今天的你最有型！")
        elif 15 <= temperature < 20:
            suggestions.append("🌬️ 涼風襲來，快披上你的帥氣風衣或夾克，下身選件厚實長褲，不會錯！")
            suggestions.append("🌬️ 如果想更暖和，來條圍巾吧，既實用又加分，暖心暖身！")
        elif temperature < 15:
            suggestions.append("❄️ 冷冷冷！毛衣厚外套全上陣，內搭保暖衣，讓你像熊一樣可愛又暖！")
            suggestions.append("❄️ 帽子、手套、圍巾，三件套缺一不可，還有厚底靴，凍腳可是很痛苦的～")
    else:
        suggestions.append("❓ 找不到溫度的資料，自己去google吧🤣")

    if max_temp or min_temp is not None:
        temp_diff = max_temp - min_temp
        if temp_diff >= 10:
            suggestions.append(f"📊 今天溫差高達{temp_diff}度！建議採用洋蔥式穿搭：")
            if max_temp > 25:
                suggestions.append("🌡️ 早晚較涼時可穿長袖薄外套，中午熱時可脫到只剩短袖，隨時應變！")
            else:
                suggestions.append("🌡️ 可以穿保暖內搭+毛衣+外套，冷的時候全部穿上，熱的時候再一件件脫下。")
        elif 5 <= temp_diff < 10:
            suggestions.append(f"📊 今天溫差{temp_diff}度，準備一件外套以應付溫度變化。")

        if max_temp >= 30:
            suggestions.append(
                "🌞 今日最高溫達" + str(max_temp) + "度！建議準備防曬用品，多補充水分。")

        if min_temp <= 15:
            suggestions.append("❄️ 今日最低溫僅" + str(min_temp) + "度！記得添加保暖衣物。")
    else:
        suggestions.append("❓ 找不到溫差的資料，自己去google吧🤣")

    if humidity is not None:
        if humidity > 90:
            suggestions.append("💦 濕氣重到像住在水裡，速乾衣物是你的救星！")
            suggestions.append("💦 記得帶雨具，雨傘雨衣隨你挑，畢竟沒人想臨時變落湯雞～")
        elif 70 <= humidity <= 90:
            suggestions.append("🌫️ 濕度偏高，透氣輕便的衣服最貼心，別讓自己汗流浹背～")
        elif 50 <= humidity < 70:
            suggestions.append("🌈 濕度剛剛好，隨意穿搭都能舒適出門，今天的你最放鬆！")
        elif humidity < 50:
            suggestions.append("💨 空氣乾得像沙漠，補水和保濕乳液不能少，讓肌膚水嫩嫩！")
    else:
        suggestions.append("❓ 找不到濕氣的資料，自己去google吧🤣")

    if rain_chance is not None:
        if rain_chance == -1:
            suggestions.append("❓ 找不到降雨機率資料，自己去google吧🤣")
        elif rain_chance > 80:
            suggestions.append(
                "☔ 100%的降雨機率，包包裡記得放一把傘，還是說外頭正在下雨呢？煙雨濛濛的城市也別有一般風情，找個咖啡廳坐下來享受一下雨中即景")
        elif 50 < rain_chance <= 80:
            suggestions.append(
                "🌦️ 雨水說來就來，摺疊傘放包包，給自己一個安心出門的理由～快乾材質衣物在這種天氣裡特別貼心，濕了也不怕！")
        elif rain_chance == 50:
            suggestions.append(
                "🌦️ 擲個硬幣吧，今天降雨機率50%，正面就帶傘，反面就直接出門，來一場驚心動魄的雨中漫步吧？")
        elif 20 <= rain_chance < 50:
            suggestions.append("🌤️ 今天降雨機率雖然不高，但帶把傘也是可以遮個陽吧～當然不帶也行，一切操之在你。")
        elif rain_chance < 20:
            suggestions.append("☀️ 陽光普照，心情跟著晴朗起來！今天很適合來場熱情澎湃的約會！")
    else:
        suggestions.append("❓ 找不到降雨機率資料，自己去google吧🤣")

    if uv_index is not None:

        if uv_index >= 11:
            suggestions.append("🌞 紫外線強到會曬出光環！全副武裝，長袖、防曬衣物、寬邊帽、墨鏡一個不能少！")
        elif 8 <= uv_index < 11:
            suggestions.append("🌤️ 紫外線強，但還不至於致命。防曬霜和帽子先準備好，皮膚感謝你！")
        elif 6 <= uv_index < 8:
            suggestions.append(
                "☁️ 紫外線適中，一起到戶外享受溫暖的陽光，補充難得的維生素D，預防骨質疏鬆、增加肌肉，不過記得注意防曬，避免皮膚受到傷害")
        elif uv_index < 6:
            suggestions.append("🌥️ 紫外線低，輕鬆自在，但長時間戶外活動還是擦點防曬霜比較穩妥！")
    else:
        suggestions.append("❓ 找不到紫外線資料😢😭 自己去google吧~")
    suggestions.append(f'\n天氣描述:{weather_descrip}\n\n')
    suggestions = '\n'.join(suggestions)
    return suggestions


def weather_app():

    # 呼叫函式並獲得 API URL
    city_name, download_URL = get_weather_api()
    if download_URL:
        print(f"\n下載的 URL: {download_URL}")
        # 下載並儲存資料
        download_weather_data(download_URL, city_name)

        # 導入資料並處理
    weather_data = import_weather_data(city_name)

    weather_informations = {}

    if ' ' in chinese_input_date:
        chinese_input_date_list = chinese_input_date.split()
        weather_informations = {}

        for idx, single_date in enumerate(chinese_input_date_list, start=1):
            weather_informations[f'{idx}'] = get_weather_data(
                single_date, district, weather_data)

        pprint(weather_informations)

        suggestions = []
        for key, value in weather_informations.items():

            suggestion = get_outfit_suggestions(value)
            suggestions.append(suggestion)
        suggestions = '\n'.join(suggestions)

    else:
        weather_information = get_weather_data(
            chinese_input_date, district, weather_data)
        suggestions = get_outfit_suggestions(weather_information)

    print(suggestions)
    return suggestions


weather_text = weather_app()


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # 無視窗模式
chrome_options.add_experimental_option(
    "excludeSwitches", ['enable-automation'])
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()


def initium(driver):  # 端傳媒

    url = 'https://theinitium.com/latest'
    driver.get(url)
    driver.implicitly_wait(5)
    result = []
    initium_data = {}

    for i in range(1, 5):
        title = driver.find_element(
            'xpath', f'//*[@id="main"]/div[1]/div/article[{i}]/a/div[1]/h4').text
        subtitle = driver.find_element(
            'xpath', f'//*[@id="main"]/div[1]/div/article[{i}]/a/div[1]/span/span').text
        link = driver.find_element(
            'xpath', f'//*[@id="main"]/div[1]/div/article[{i}]/a').get_attribute('href')
        result.append({'標題': title, '副標': subtitle, 'Link': link})

    for item in result:
        title = item['標題']
        subtitle = item['副標']
        link = item['Link']

        # 輸出結果
        print(f"標題: {title} | 副標: {subtitle} | 連結: {link}")
        initium_data[f"標題: {title} | 副標: {subtitle}"] = link
    return initium_data


print("端傳媒:")
initium_data = initium(driver)
print(initium_data)


def cnyes():

    chrome_version = listdir(r'C:\Program Files (x86)\Google\Chrome\Application')[
        0].split('.')[0]
    page = 1
    limit = 30
    cnyes_news = {}

    headers = {
        'Origin': 'https://news.cnyes.com/',
        'Referer': 'https://news.cnyes.com/',
        'User-Agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36',
    }

    r = requests.get(f"https://api.cnyes.com/media/api/v1/newslist/category/headline?page={
                     page}&limit={limit}", headers=headers)

    if r.status_code != requests.codes.ok:
        print('請求失敗', r.status_code)
        return None
    cnyes = r.json()['items']
    pprint(cnyes)

    URL = 'https://news.cnyes.com/news/id/'
    for cnyes_data in cnyes["data"][:5]:
        title = cnyes_data["title"]
        keyword = ",".join(cnyes_data["keyword"])if isinstance(
            cnyes_data["keyword"], list) else cnyes_data["keyword"]
        newsURL = URL + str(cnyes_data["newsId"])

        cnyes_news[f"標題: {title} | 關鍵字: {keyword}"] = newsURL
        print(f"標題: {title} | 關鍵字: {keyword} | 連結: {newsURL}")

    return cnyes_news


print("\n鉅亨網:")
cnyes_data = cnyes()
print(cnyes_data)


def bbc_news(driver):  # BBC

    url = 'https://www.bbc.com/zhongwen/trad'
    driver.get(url)
    driver.implicitly_wait(5)
    bbc_news_data = {}

    news_items = driver.find_elements(
        'css selector', 'section[aria-labelledby="high-collection-1"] ul[role="list"] h3 a')
    dates = driver.find_elements(
        'css selector', 'ul[role="list"] div.promo-text time')

    # 提取標題和連結，只取前 5 筆
    for idx, item in enumerate(news_items[:5]):
        title = item.text  # 提取標題
        link = item.get_attribute('href')  # 提取連結
        date = dates[idx].text if idx < len(dates) else "日期未知"  # 獲取日期，避免索引錯誤

        # 輸出資訊
        print(f"標題: {title} | 日期: {date} | 連結: {link}")
        bbc_news_data[f'標題: {title} | 日期: {date}'] = link
    return bbc_news_data


def bbc_taiwan(driver):  # BBC
    url = 'https://www.bbc.com/zhongwen/trad/topics/cd6qem06z92t'
    driver.get(url)
    driver.implicitly_wait(5)
    bbc_taiwan_data = {}

    # 使用 CSS Selector 抓取新聞項目
    news_items = driver.find_elements('css selector', 'ul[role="list"] h2 a')
    dates = driver.find_elements(
        'css selector', 'ul[role="list"] div.promo-text time')

# 提取標題、日期、連結，只取前 3 筆
    for idx, item in enumerate(news_items[:3]):
        title = item.text.replace("視頻,", "")  # 移除「視頻」
        title = re.sub(r", 節目全長 \d{1,2},\d{2}", "",
                       title)  # 移除「, 節目全長 3:29」這類文字
        title = title.strip()  # 去除前後空格
        link = item.get_attribute('href')  # 提取連結
        date = dates[idx].text if idx < len(dates) else "日期未知"  # 獲取日期，避免索引錯誤

        # 輸出資訊
        print(f"標題: {title} | 日期: {date} | 連結: {link}")
        bbc_taiwan_data[f'標題: {title} | 日期: {date}'] = link
    return bbc_taiwan_data


print("\nBBC 中文網:")
bbc_news_data = bbc_news(driver)
print(bbc_news_data)
print("\nBBC 中文網-台灣:")
bbc_taiwan_data = bbc_taiwan(driver)
print(bbc_taiwan_data)


def news_app():

    initium_data = initium(driver)
    cnyes_data = cnyes()
    bbc_news_data = bbc_news(driver)
    bbc_taiwan_data = bbc_taiwan(driver)

    all_datas = [(initium_data, "端傳媒"), (cnyes_data, "鉅亨網"),
                 (bbc_news_data, "BBC 中文網"), (bbc_taiwan_data, "BBC 中文網-台灣")]
    html_content = """<!DOCTYPE html><html><head><title>你的天氣小助手</title></head>"""
    for data, web_title in all_datas:
        html_content += f'<br><h2>{web_title}</h2>'
        for nwes_title, link in data.items():
            html_content += f'<h3><a href="{link}">{nwes_title}</a></h3>'
    html_content += "</body></html>"
    # print(html_content)
    return html_content


html_content = news_app()


# ---- 信件內容設定 ---- #
sender_email = f"{os.getenv("e-mail")}"  # 你的 Gmail 帳號
sender_password = f"{os.getenv("mail_password")}"  # 你的應用程式專用密碼
receiver_email = f"{os.getenv("e-mail")}"  # 你的收件信箱

subject = "天氣提醒服務測試郵件"
body = "你好！\n\n祝你有美好的一天！😊\n天氣資訊如下：\n\n" + weather_text

# ---- 設定郵件格式 ---- #
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))  # 郵件純文字內容
msg.attach(MIMEText(html_content, 'html', 'utf-8'))

try:
    # ---- 連接 Gmail SMTP 伺服器 ---- #
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.ehlo()
        server.login(sender_email, sender_password)  # 登入 Gmail 帳號
        server.sendmail(sender_email, receiver_email, msg.as_string())  # 發送郵件
    print("郵件發送成功！")
except Exception as e:
    print(f"郵件發送失敗：{e}")
