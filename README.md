# 基于 JavaScript 页面的视频爬虫工具
## 一款使用 Python 开发的工具，通过 Selenium WebDriver 和 BeautifulSoup 从 JavaScript 渲染的网页中爬取视频内容。

## 功能特点
* 连接到已运行的 Chrome 浏览器实例
* 通过识别页面结构自动导航课程内容
* 从 iframe 元素中提取视频 URL
* 将 m3u8 链接转换为直接的 MP4 视频链接
* 对文件名进行处理，确保兼容各操作系统
* 将视频元数据保存到文本文件中以供后续使用

启用远程调试模式启动 Chrome：
  `chrome.exe --remote-debugging-port=9222`
  
免责声明
此工具仅供教育目的使用。请负责任地使用，并确保您有权限访问和下载您爬取的任何网站内容。
