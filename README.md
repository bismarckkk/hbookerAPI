这是一个刺猬猫/欢乐书客API的简单实现，正在绝赞更新中
====
> 本项目从另一项目
[HbookerAppNovelDownloader](https://github.com/hang333/HbookerAppNovelDownloader)
有所借鉴  

### 本项目一切开发旨在学习，请勿用于非法用途
+ 本项目仅供学习和娱乐用途使用
+ 本项目不会支持任何和钱相关的协议
+ 本项目不会支持任何涉及账户安全的操作
+ 请勿借助本项目进行刷票、伪造数据等损害社区公平的行为
+ 其他任何衍生软件行为与本项目无关


目前实现的功能
----
1. 登录（所以猫客不登陆到底能干什么
2. 获取书架列表
3. 从书架获取书籍列表
4. 获取书籍简单信息

所以这玩意现在就只能用来做做数据分析，想干别的的就先别想了

TODO
----
1. 建立用户类，完成关注，取关等基本操作
2. 完善书架列表操作，如新增、移除书架
3. 完善书架操作，如移动书籍、收藏、移出等
4. 支持获取章节基本信息（不含正文内容）
5. 基本的数据分析支持

start
----
#### 通过pypi安装
```shell script
pip install hbookerAPI
```
#### 从仓库安装
将仓库clone到本地，把hbookerAPI文件夹拷贝到你的工作目录下
#### 示例使用
```python
import hbookerAPI

# 初次登陆
session = hbookerAPI.Session()
session.login('你的账号', '你的密码')

# 可持久化保存session.commonUserInfo中的loginToken和account到本地
# 之后登录可直接
session = hbookerAPI.Session(loginToken, account)

bookShelves = session.getBookShelfList()
shelf = session.getBookShelf(bookShelves[0]['shelf_id'])

print(shelf.books)
```