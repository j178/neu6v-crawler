## Crawler for [六维空间](http://bt.neu6.edu.cn)

### 功能
1. 获取[资源索引页](http://bt.neu6.edu.cn/plugin.php?id=neubt_resourceindex)新增资源, 自动下载种子并添加到 [uTorrent](http://www.utorrent.com/) 中下载
2. 获取[水区](http://bt.neu6.edu.cn/forum-4-1.html)新增主题, 调用图灵机器人 API 自动回复(浮云+1)
3. 自动回复提到'我'的消息

### 要求
1. 网络支持 IPv6, 拥有六维空间账号, 以及足够的浮云
2. 安装 Python3, 依赖库 `requests`, `BeautifulSoup4`, `lxml`
3. 安装 uTorrent, 开启 `WebUI`

### 配置
1. `git clone git@github.com:j178/neu6v-crawler.git`
2. 登录六维账号, 打开浏览器开发者工具, 复制 `LRpW_2132_auth` 与 `LRpW_2132_saltkey` 这两项 cookie值 到`data/cookies.json`中
3. 打开 uTorrent, 进入 `选项-设置-高级-网页界面`, 勾选 `启用网页界面`, 然后在`身份验证`中配置`用户名`和`密码`, 并将它们写入到`data/config.json`中
4. 将 `session.py` 中 `COOKIE_FILE` 改为`data/cookies.json', 同理将 `downloader.py` 中 `CONFIG_FILE` 改为 `data/config.json`

### 运行
- 启动自动下载功能
```sh
python /path/to/project/downloader.py
```
- 开启自动回复爬虫
```sh
python /path/to/project/crawler.py
```

### 自动运行
1. Linux 使用 `crontab` 工具
2. Windows 使用 `任务计划程序`, 添加一个基本任务, 然后在 `触发器` 中打开重复执行功能
