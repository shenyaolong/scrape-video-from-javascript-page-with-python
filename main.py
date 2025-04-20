from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import random
import time
import re
import os
import requests


# 连接到浏览器函数


options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=options)
print("成功连接到 Chrome 浏览器！")

# 工具函数


def sanitize_filename(title):
    """规范化文件名，替换非法字符"""
    illegal_chars = r'[:\\/*?"<>|]'
    clean_title = re.sub(':', ' -', title)
    clean_title = re.sub(illegal_chars, '', clean_title)
    return clean_title.strip()


def final_output(path, name, url):
    return f"#O,{path}\n{name},{url}"


def click_by_id(target_id):
    """点击指定 ID 的元素，动态等待页面切换"""
    try:
        target = driver.find_element((By.ID, target_id))
        actions = ActionChains(driver)
        driver.execute_script("arguments[0].scrollIntoView(true);", target)
        actions.move_to_element(target).click().perform()
        return True
    except:
        return False


def click_by_url(url):
    try:
        target = driver.find_element(By.XPATH, f"//a[@href='{url}']")
        actions = ActionChains(driver)
        driver.execute_script("arguments[0].scrollIntoView(true);", target)
        actions.move_to_element(target).click().perform()
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
                mp4_url = matches[0] + ".mp4"
                return mp4_url
            return []
        except:
            driver.switch_to.default_content()
            return []
    return []


def extract_download_link():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    download_links = driver.find_elements(By.TAG_NAME, "a")[-2:]
    file_elements = soup.find_all(
        'span', class_='course-player__download-files__label _download-files__label_1j5gba')
    file_names = [sanitize_filename(file_element.text)
                  for file_element in file_elements if file_element.text]
    downloadable_files = [link.get_attribute(
        'href') for link in download_links]
    root_path = "C:/Users/75299/Downloads"
    output1 = final_output(root_path, file_names[0], downloadable_files[0])
    output2 = final_output(root_path, file_names[1], downloadable_files[1])
    return f"{output1}\n{output2}"


def analyze_course_page():
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        chapter_divs = [
            chapter for chapter in soup.find_all('div', class_="course-player__chapters-item _chapters-item_1tqvoe ember-view ui-accordion ui-widget ui-helper-reset")
            if not any(keyword in chapter.text for keyword in ["Orientation", "Benchmark Assessment", "Final Assessment", "Course Feedback", "Next Step"])
        ]
        chapter_text = [sanitize_filename(chapter.find(
            'h2').text.strip()) for chapter in chapter_divs]
        chapter_ids = [chapter['id']
                       for chapter in chapter_divs if chapter.has_attr('id')]
        all_links = soup.find_all(
            'a', id=lambda x: x and x.startswith('ember'))
        video_ids = []
        for link in all_links:
            details_div = link.select_one(
                '.content-item__details._content-item__details_nffvg8')
            if details_div and any(keyword in details_div.text.strip().upper() for keyword in ["VIDEO", "DOWNLOAD"]):
                video_ids.append(link['id'])

        all_ids = sorted(chapter_ids + video_ids, key=lambda x: int(x[5:]))
        current_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[aria-current="step"]'))
        )
        current_id = current_element.get_attribute("id")

        url_links = soup.find_all(
            'a', class_='course-player__content-item__link _content-item__link_nffvg8 ember-view')
        link_list = [link.get('href')
                     for link in url_links if link.get('href')]
        return {
            "current_id": current_id,
            "link_list": link_list,
            "clickable_ids": all_ids,
            "chapters": chapter_text
        }
    except Exception as e:
        print(f"Error extracting course page: {e}")
        return []


# 主程序
root_path = "C:/Users/75299/Downloads"
df = pd.DataFrame(columns=['title', 'link', 'path', 'type', 'output', 'id'])

# 获取课程标题和链接
course_title = [
    'Data Science in Python - Regression',
    'Interactive Dashboards with Plotly & Dash',
    'Advanced SQL Querying',
    'Advanced MySQL Database Administration',
    'MySQL Database Administration',
    'Advanced MySQL for Marketing & Web Analytics',
    'MySQL Data Analysis',
    'Microsoft Power BI Service',
    'Microsoft Power BI Desktop',
    'Microsoft PL-300 Exam Prep',
    'Advanced DAX for Power BI',
    'Tableau Server for Analysts',
    'Tableau Speed & Performance',
    'Tableau Desktop Certification Prep',
    'Intro to Tableau Prep',
    'Advanced Tableau Desktop',
    'Intro to Tableau Desktop',
    'Microsoft Excel Foundations',
    'Microsoft Copilot for Excel',
    'Intro to Financial Modeling',
    'Statistics for Data Analysis',
    'Advanced Excel Dashboard Design',
    'Excel MO-201 Exam Prep',
    'Excel Pro Tips - Pivot Tables',
    'Excel Pro Tips - Visualization',
    'Excel Pro Tips - Analytics',
    'Excel Pro Tips - Formulas',
    'Excel Pro Tips - Productivity',
    'Excel Pro Tips - Formatting',
    'Power Query, Power Pivot & DAX',
    'Excel Pivot Tables & Charts',
    'Excel Charts & Graphs',
    'Excel Formulas & Functions',
    'Intro to Alteryx Designer',
    'Intro to Google Sheets',
    'Launching Your Data Career',
    'Thinking Like an Analyst',
    'Machine Learning 2 - Classification',
    'Machine Learning 3 - Regression',
    'Machine Learning 4 - Unsupervised Learning',
    'Machine Learning 1 - Data Profiling',
    'Acing the Analyst Interview',
    'Data & AI Ethics',
    'Cloud Basics for Data Professionals',
    'Optimizing Your Resume',
    'Building a World-Class Portfolio',
    'Building your Personal Brand',
    'Networking & Applying for Jobs',
    'Data Literacy Foundations',
    'Finding Your Path in Data',
    'ChatGPT for Data Analytics']

course_link = [
    'https://thinkificenroller.mavenanalytics.io/course/4e87be60-9d4c-48e8-aef2-62d9b4adef42?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/b39416c8-cf09-4eeb-b240-e9ac9eee0a71?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/e1bd8e71-ea39-48d8-bf48-7ada08a8a833?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/f444df94-4ad5-48e5-b02b-c8f6011d1d12?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/99586ae3-df1a-4ab6-b5ee-ed985d826c02?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/1102a7e6-e5d1-49ed-8cb3-ca5819758dd7?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/df6683ac-53f4-41ca-b448-42f2a28ca1d0?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/776c6189-6f22-4e9f-af87-865c67835786?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/23897c20-455a-4a00-801f-fd048a11a49d?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/c9da672d-56a0-4382-a2fa-db3d903dc602?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/8684b283-0365-4a2f-9624-f5cac37d6cf1?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/c03c0de5-dffc-40d8-ad52-b9bb377dacb5?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/400ade1c-c2ac-4488-9ddf-f037329253ad?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/e593e675-b378-44d2-bbf7-6ea24c0154d5?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/f5ea00b2-2f96-456b-b394-eeac5a47ed51?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/5c98cff0-41b7-4817-92db-a0cd2880dfd3?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/96396113-9489-4498-b2b6-08b77e2ba88a?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/18c574d8-d64e-499a-ac67-247a2cd044f7?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/59278084-ebe1-44e7-834d-1ed05a8ebe86?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/471ca483-a702-4a7d-b142-73086a193af1?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/33468c00-4ab7-4e5b-a5ba-9729e73590ac?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/f88cd8c3-3fa3-4afe-9233-5c859bb77042?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/d2dc6ff3-ccda-41a1-bf50-3bcc6bcabcb0?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/0253f0ff-0c43-4fb0-808d-cae4720f61c4?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/5f85edab-ecdc-47cf-b3a7-9e5ad953bcb4?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/9bb95bb7-38bb-43ec-b7d3-2660a9b38347?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/8adc05a7-1f0f-441b-aca2-380f8a3235b3?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/9aee1658-ca1c-4b97-8259-bea7ffb2e7e3?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/6634b138-8b89-4d90-97bc-0f710509bd16?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/76f43eb1-d97f-4fad-9097-f55ab0d5c07d?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/997547ab-48d2-4b4b-9b28-e48b286522c4?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/9014b0fd-3403-4b06-9421-cbe09b49b746?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/db5cfef2-f9f4-4c41-8559-3aa05745fd43?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/cf4eb33e-99e7-4daa-894b-d72e5d84393b?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/9f06f6da-b843-4a1f-b784-68619aef15b0?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/30ad9678-de66-49ea-8e62-5eea9d9f4571?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/bd73222a-5302-431c-bd25-e62ef4ee4aa0?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/496739ae-a7d5-4f04-9e28-9c1e894851b9?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/6bfae800-2e99-4f92-a438-58bf7444c6c5?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/2adde790-f588-4915-b3cb-5196b64faccc?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/0ef5dd00-a276-4cd8-a7a1-00e68adfaeef?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/05e431dd-74bb-4898-b904-86327b7d2f46?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/d2b99b66-957e-4bfe-bccf-72d4d300fa21?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/4c87bb7f-6dbb-498f-888f-0eab40118ffe?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/29f07de6-bc2a-4f3b-b789-b67972ecc56a?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/9bfe87a3-f16b-4fee-b084-e3b9f0730044?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/37f8a0ad-fcf7-48ae-a619-ad4b04a95cd9?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/4f0ed362-3bf1-4423-a2f8-6b13898e5732?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/b2e2e55b-a7a3-4c24-af6f-c0e97b56bb68?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/5a440b5f-7806-4ea6-bdd8-72af12bb715c?error_callback=https://app.mavenanalytics.io/',
    'https://thinkificenroller.mavenanalytics.io/course/0c04c2c7-c856-4dc9-93bd-d0dd44b143d1?error_callback=https://app.mavenanalytics.io/']

# 课程进度条
course_progress = tqdm(range(len(course_title)), desc="课程进度")
for i in course_progress:
    course_progress.set_description(f"处理课程: {course_title[i]}")
    try:
        course_path = os.path.join(root_path, course_title[i])
        df.loc[len(df)] = [course_title[i], course_link[i],
                           course_path, "course", None, None]

        # 跳转到第i个课程页面
        click_by_url(course_link[i])
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # 读取课程信息
        course_info = analyze_course_page()
        links = course_info["link_list"]
        chapters = course_info["chapters"]
        click_order = course_info["clickable_ids"]
        current_id = course_info["current_id"]

        # 章节进度条
        chapter_progress = tqdm(chapters, desc="章节进度", leave=False)
        for chapter_idx, chapter in enumerate(chapters):
            chapter_progress.set_description(f"处理章节: {chapter}")

            # 获取章节标题和路径
            chapter_title = f"{chapter_idx}. {sanitize_filename(chapter)}"
            chapter_path = os.path.join(course_path, chapter_title)
            chapter_id = click_order[chapter_idx]
            df.loc[len(df)] = [chapter_title, None,
                               chapter_path, "chapter", None, chapter_id]

            # 获取课程信息
            lesson_progress = tqdm(range(len(links)), desc="课程进度", leave=False)
            for lesson_idx in lesson_progress:
                lesson_progress.set_description(f"处理课程: {lesson_idx}")
                try:
                    lesson_info = links[lesson_idx]
                    is_video = "VIDEO" in lesson_info.upper()
                    downloadable = "DOWNLOAD" in lesson_info.upper()
                    lesson_id = click_order[lesson_idx]
                    lesson_title = f"{lesson_idx}. {sanitize_filename(lesson_info)}"
                    lesson_path = os.path.join(chapter_path, lesson_title)

                    # 处理视频课程
                    if is_video:
                        video_url = extract_video_links()
                        output = final_output(
                            lesson_path, lesson_title, video_url)
                        if video_url:
                            df.loc[len(df)] = [lesson_title, links[lesson_idx],
                                               lesson_path, "video", output, lesson_id]

                    # 处理下载资源
                    elif downloadable:
                        download_url = extract_download_link()
                        if download_url:
                            df.loc[len(df)] = [lesson_title, links[lesson_idx],
                                               lesson_path, "resource", download_url, lesson_id]

                except Exception as e:
                    print(f"课程 {lesson_idx} 处理失败: {e}")

            # 保存章节数据
            df.to_csv(os.path.join(root_path, 'output.csv'),
                      index=False, encoding='utf-8-sig')
            print(f"章节 {chapter_title} 处理完成")

        # 检查是否为最后一个ID
        try:
            next_id = click_order[click_order.index(current_id) + 1]
        except IndexError:
            print("没有更多的课程，返回主页")
            click_by_url("https://app.mavenanalytics.io/")
            print("导航到学习页面")
            click_by_url("https://app.mavenanalytics.io/learning-plan")

        # 保存课程数据
        df.to_csv(os.path.join(root_path, 'output.csv'),
                  index=False, encoding='utf-8-sig')
        print(f"课程 {course_title[i]} 处理完成")

    except Exception as e:
        print(f"课程 {course_title[i]} 处理失败: {e}")
        break

    finally:
        # 最终保存
        df.to_csv(os.path.join(root_path, 'output.csv'),
                  index=False, encoding='utf-8-sig')
        print("抓取完成! 结果已保存到output.csv")
