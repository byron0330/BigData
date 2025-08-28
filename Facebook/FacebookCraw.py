import json, time , re , utils , uuid
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from MongoDb import MongoHelper
mongo = MongoHelper()
control = True

def click_all_post(driver):
    elements = utils.get_displayed_texts(driver)
    print(f"找到 {len(elements)} 個元素")
    for i in elements:
        try:
            driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'nearest'});"
            "window.scrollBy(0, -120);", 
            i
            )
            content_index = 1
            t = (i.text or "")
            if "排序" in t or "最相關" in t or "載入中……" in t:
                continue
            content_el = i.find_elements(By.XPATH,".//div[@class='m bg-s2' and @data-type='container']")[1]
            t = content_el.text.strip()
            if t =="":
                content_el = i.find_elements(By.XPATH,".//div[@class='m bg-s2' and @data-type='container']")[3]
                t = content_el.text.strip()

            if "查看更多" in t:
                # morebtn = content_el.find_element(By.XPATH, ".//span[normalize-space(.)='查看更多' or normalize-space(.)='See more']")
                try:
                    driver.execute_script(
                            "arguments[0].click();",
                            content_el.find_element(By.XPATH, ".//div[@data-mcomponent='TextArea']//span[normalize-space(.)='查看更多' or normalize-space(.)='See more']")
                        )
                except:
                    driver.execute_script(
                            "arguments[0].click();",
                            content_el.find_element(By.XPATH, ".//div[@data-mcomponent='ServerTextArea']//span[normalize-space(.)='查看更多' or normalize-space(.)='See more']")
                        )
                time.sleep(1.5)
        except:
            pass

def get_comment(driver,random_id):
    try:
        global control
        backButton = driver.find_element(By.XPATH,".//div[@role='button' and @aria-label='返回']")
        box = driver.find_element(By.XPATH,".//div[@class='m displayed']")
        # print(box.text)
        comment = box.find_elements(By.XPATH,".//div[@class='m bg-s1' and @data-type='container']")
        for c in comment:
            author = c.find_element(By.XPATH,".//span[@class='f20']").text
            try:
                content =  c.find_element(By.XPATH,".//span[@class='f1']").text
            except:
                content = "貼圖"
            Creattime = c.find_element(By.XPATH,".//span[@class='f19']").text
            data={
                    "Type":"Comment",
                    "Author":author,
                    "Content":content,
                    "CreatedAt":utils.getRealTime(Creattime),
                    "PostId" : random_id,
                }
            print(data)
            control = mongo.save_one(data)
    except:
        pass
    finally:
        driver.back()
        time.sleep(2)

def get_post_data(driver):
    global control
    elements = utils.get_displayed_texts(driver)
    for i in elements:
        try:
            random_id = str(uuid.uuid4())
            driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', inline:'nearest'});"
            "window.scrollBy(0, 100);",
            i
            )
            t = (i.text or "")
            if "排序" in t or "最相關" in t or "載入中……" in t:
                continue
            box = i.find_elements(By.XPATH,".//div[@class='m bg-s2' and @data-type='container']")
            if box[1].text != "":
                content = box[1].text
            else:
                content = box[3].text
                
            data={
                "Type":"Post",
                "Author":box[0].find_element(By.XPATH, ".//span[@class='f2 a']").text,
                "Content":content,
                "CreatedAt":utils.getRealTime(box[0].find_elements(By.XPATH, ".//span[contains(normalize-space(.), '󰞋󱙷')]")[-1].text),
                "PostId" : random_id,
                
            }
            print(data)
            commentCount = utils.extract_int(box[-2].find_elements(By.XPATH,".//div[@class='m' and @role='button']")[2].text)
            print("留言數量：" , commentCount)

            if commentCount > 0 :
                y = driver.execute_script("return window.pageYOffset")
                box[-2].click()
                time.sleep(2)
                get_comment(driver,random_id)
                driver.execute_script(f"window.scrollTo(0, {y});")
                time.sleep(2)
            control = mongo.save_one(data)
            print("已存入")
            print("==========================================")
        except Exception as e:
            print(e.__traceback__.tb_lineno)
            pass


service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone 12 Pro"})
driver = webdriver.Chrome(options=options)
driver.set_window_size(480, 980)
wait = WebDriverWait(driver, 20)

driver.get("https://m.facebook.com")
wait.until(
    EC.any_of(
        EC.presence_of_element_located((By.NAME, "email")),  # 登入表單
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'m') and contains(@class,'displayed')]"))
    )
)

with open("cookies.json", "r", encoding="utf-8") as f:
    cookies = json.load(f)
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print("跳過:", cookie["name"], e)


driver.refresh()
wait.until(
    EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'m') and contains(@class,'displayed')]"))
)
driver.get("https://m.facebook.com/groups/443709852472133?locale=zh_TW")
wait.until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='m displayed']"))
)

while control:
    click_all_post(driver,)
            
    get_post_data(driver)
    time.sleep(2)
    utils.smooth_scroll_once(driver)
    time.sleep(2)

    try:
        btn = driver.find_element(By.XPATH, "//div[@class='m bg-s2 displayed']")
        if btn.text =="查看更多":
            btn.click()
            print("出現查看更多貼文按鈕")
    except:
        print("未出現查看更多貼文按鈕")
