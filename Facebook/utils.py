
from selenium.webdriver.common.by import By
import json, time , re
from datetime import datetime, timedelta
now_time = datetime.now()

def get_displayed_texts(driver):
    return driver.find_elements(By.XPATH, "//div[@class='m displayed']")

def smooth_scroll_once(driver):
    for _ in range(50):
        driver.execute_script("window.scrollBy(0, 120);")
        time.sleep(0.06)

def extract_int(text: str):
    match = re.search(r"\d+", text)
    if match:
        return int(match.group()) 
    return 0 


def getRealTime(time_str: str) -> datetime:
    time_str = time_str.strip()

    # 1. 幾分鐘前
    if re.search(r"(\d+)\s*分鐘", time_str):
        mins = int(re.search(r"(\d+)\s*分鐘", time_str).group(1))
        return now_time - timedelta(minutes=mins)

    # 2. 幾小時前
    elif re.search(r"(\d+)\s*小時", time_str):
        hours = int(re.search(r"(\d+)\s*小時", time_str).group(1))
        return now_time - timedelta(hours=hours)

    # 3. 幾天前
    elif re.search(r"(\d+)\s*天", time_str):
        days = int(re.search(r"(\d+)\s*天", time_str).group(1))
        return now_time - timedelta(days=days)
    
    elif re.search(r"(\d+)\s*週", time_str):
        week = int(re.search(r"(\d+)\s*週", time_str).group(1))
        days = 7 * week
        return now_time - timedelta(days=days)
    
    elif re.search(r"(\d+)\s*個月", time_str): #
        week = int(re.search(r"(\d+)\s*個月", time_str).group(1))
        days = 30 * week
        return now_time - timedelta(days=days)
    # 4. 幾月幾日
    elif re.search(r"(\d+)\s*月\s*(\d+)\s*日", time_str):
        m = re.search(r"(\d+)\s*月\s*(\d+)\s*日", time_str)
        month, day = int(m.group(1)), int(m.group(2))
        result = datetime(now_time.year, month, day)
        # 如果日期比現在還晚，就認為是去年
        if result > now_time:
            result = datetime(now_time.year - 1, month, day)
        return result

    # 無法解析 → 回傳現在
    return now_time