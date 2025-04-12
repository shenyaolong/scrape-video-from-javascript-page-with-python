from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import random
import time
import re

# 设置 Chrome 选项以连接到已打开的浏览器
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# 初始化 WebDriver
try:
    driver = webdriver.Chrome(options=options)
    print("成功连接到 Chrome 浏览器！")
except Exception as e:
    raise


def click_element(target_id, tag_name=None):
    try:
        target = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, target_id))
        )
        if tag_name and target.tag_name != tag_name:
            return False
        actions = ActionChains(driver)
        driver.execute_script("arguments[0].scrollIntoView(true);", target)
        actions.move_to_element(target).click().perform()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[aria-current="step"]'))
        )
        time.sleep(random.uniform(5, 10))
        return True
    except:
        return False


def extract_video_links():

    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        iframe = iframes[0]
        try:
            driver.switch_to.frame(iframe)
            iframe_content = driver.page_source
            m3u8_pattern = r'(https://embed-ssl\.wistia\.com/deliveries/[a-f0-9]+)\.m3u8'
            matches = re.findall(m3u8_pattern, iframe_content)
            driver.switch_to.default_content()
            if matches:
                edited_url = [matches[0] + ".mp4"]
                return edited_url
            return []
        except:
            driver.switch_to.default_content()
            return []
    return []


def sanitize_filename(title):
    illegal_chars = r'[:\\/*?"<>|]'
    clean_title = re.sub(':', ' -', title)
    clean_title = re.sub(illegal_chars, '', clean_title)
    return clean_title.strip()


def get_page_info(index):
    try:
        current_page = driver.page_source
        soup = BeautifulSoup(current_page, 'html.parser')

        course_title_elem = soup.find(
            'h3', class_="course-player__content-header__title _content-header__title_h7ytgy")
        course_title = course_title_elem.text.strip() if course_title_elem else "无课程标题"

        current_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[aria-current="step"]'))
        )
        current_id = int(current_element.get_attribute("id")[5:])
        current_text = current_element.text.strip()

        title_match = re.match(r'^(.*?)(?:\n|$)', current_text, re.DOTALL)
        tag_match = re.search(r'\n\s*(\w+)(?:\s|$)', current_text)
        current_page_title = title_match.group(
            1).strip() if title_match else current_text
        current_page_tag = tag_match.group(1).strip() if tag_match else ""

        indexed_title = f"{index}. {sanitize_filename(current_page_title)}"
        video_links = []
        if current_page_tag == "VIDEO":
            video_links = extract_video_links()

        return {
            "course_title": course_title,
            "page_id": f"ember{current_id}",
            "page_title": indexed_title,
            "page_tag": current_page_tag,
            "video_links": video_links
        }
    except:
        return None


# 初始化索引和进度
index = 0
all_pages_info = []

# 主逻辑循环
while True:
    try:
        page_info = get_page_info(index)
        if not page_info:
            break

        if page_info['video_links']:
            filename = f"{page_info['page_title']}.mp4"
            url = page_info['video_links'][0]
            output_line = f"{filename},{url}"
            print(output_line)
            index += 1
        elif page_info['page_tag'] != "VIDEO":
            index += 1

        all_pages_info.append(page_info)

        current_id = int(page_info['page_id'][5:])
        next_id = current_id + 4
        if click_element(f"ember{next_id}", tag_name="a"):
            continue

        chapter_id = current_id + 2
        if click_element(f"ember{chapter_id}", tag_name="div"):
            index = 0
            lesson_id = chapter_id + 5
            if click_element(f"ember{lesson_id}", tag_name="a"):
                continue
            else:
                break
        break  # +4 和 +2 均失败，结束

    except:
        break

# 保存到文件
with open("course_data.txt", "w", encoding="utf-8") as f:
    for info in all_pages_info:
        if info['video_links']:
            filename = f"{info['page_title']}.mp4"
            url = info['video_links'][0]
            f.write(f"{filename},{url}\n")

print("操作完成，保持浏览器打开状态")
driver.quit()
