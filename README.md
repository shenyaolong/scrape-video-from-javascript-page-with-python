基于 JavaScript 页面的视频爬虫工具
一款使用 Python 开发的工具，通过 Selenium WebDriver 和 BeautifulSoup 从 JavaScript 渲染的网页中爬取视频内容。

功能特点
连接到已运行的 Chrome 浏览器实例
通过识别页面结构自动导航课程内容
从 iframe 元素中提取视频 URL
将 m3u8 链接转换为直接的 MP4 视频链接
对文件名进行处理，确保兼容各操作系统
将视频元数据保存到文本文件中以供后续使用
环境要求
Python 3.x
Google Chrome 浏览器
ChromeDriver（与您的 Chrome 版本兼容）
以下 Python 包：
selenium
beautifulsoup4
安装方法
克隆此仓库：

安装所需的 Python 包：

使用方法
启用远程调试模式启动 Chrome：

在浏览器中导航到您想要爬取的课程/网站

运行脚本：

脚本将：

连接到已打开的 Chrome 浏览器
导航遍历课程页面
提取视频链接
在控制台打印进度信息
将视频链接保存到 course_data.txt 文件中
工作原理
脚本连接到启用远程调试的 Chrome 浏览器
使用 Selenium 和 BeautifulSoup 识别当前页面元素
对于视频页面，从 iframe 元素中提取视频 URL
通过识别并点击导航元素来浏览下一页
所有视频 URL 将以格式化的文件名保存到文本文件中
配置选项
您可以修改 main.py 中的以下变量来自定义行为：

options.add_experimental_option("debuggerAddress", "127.0.0.1:9222") - 如有需要，可更改端口号
根据需要调整提取函数中的等待时间和匹配模式
许可证
本项目为开源项目，采用 MIT 许可证。

免责声明
此工具仅供教育目的使用。请负责任地使用，并确保您有权限访问和下载您爬取的任何网站内容。