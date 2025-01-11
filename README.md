# yooooo!!! suuuuuup~~ homie😎😎 我們是晴報站
## 這是一個天氣自動提醒的專案，使用方式如下：

1. 在txt檔案輸入三個變數：  
    - 第一行：縣市  
    - 第二行：行政區  
    - 第三行：日期(e.g: 今天、明天、後天、三天後、四天後、五天後、六天後、七天後) 第三行不限輸入幾個，不同天以空格分開  


2. 創一個名字叫.env的資料夾，在裡面輸入三個變數  
    - weather_api = (來這裡 https://opendata.cwa.gov.tw/user/authkey 登入會員，並取得授權碼)  

    - e-mail = (你的e-mail！)  

    - mail_password = (來這裡 https://myaccount.google.com/apppasswords?rapt=AEjHL4NKuN8xFqAqevfJ4_67v34kVKEJiWXBFuOZkdqkDmbGFAElqfQ7OkvnhHJYPFUWi6FinDRc4IEOAJQ0ts0B4CJhN0AcZdX6yARXsjFryABA0_cIDH8  取得你的應用程式密碼)  

3. 打開terminal輸入 pip install -r requirements.txt    

4. 就可以執行啦！
--- 
### 常見錯誤：
請確定你進行操作時的位置  
在終端機輸入 dir(windows) 、 ls (macOS/Linux)  
應該會出現類似下面的內容，如果沒有請用cd導到正確位置

```text
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----         2025/1/11  下午 12:51             11 .gitignore                                                                                                                    

-a----         2025/1/11  下午 12:51             90 administrative_district.txt                                                                                                   

-a----         2025/1/11  下午 12:51           1042 README.md                                                                                                                     

-a----         2025/1/11  下午 12:51            758 requirements.txt                                                                                                              

-a----         2025/1/11  下午 12:51          24353 weather_project.py                                                                      

```                                   


### 備註：
若需自動執行，請設定工作排程器。