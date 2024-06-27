import time

from selenium import webdriver
from selenium.webdriver.common.by import By


# 드라이버 생성
driver = webdriver.Chrome()
driver.get("https://www.saramin.co.kr/")
driver.implicitly_wait(0.5)

# 상호작용
search_label = driver.find_element(by=By.TAG_NAME, value='label')
driver.execute_script("arguments[0].click();", search_label)
search_box = driver.find_element(by=By.ID, value='ipt_keyword_recruit')
driver.execute_script("arguments[0].setAttribute('value', arguments[1])", search_box, 'airflow')
search_button = driver.find_element(by=By.ID, value='btn_search_recruit')
driver.execute_script("arguments[0].click();", search_button)

# 5분 확인 후 종료
time.sleep(300)
driver.quit()