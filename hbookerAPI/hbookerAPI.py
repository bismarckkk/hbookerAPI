from Crypto.Cipher import AES
import base64
import hashlib
import ujson
import requests
import urlList
import re
import time
from multiprocessing.dummy import Pool as ThreadPool
import pandas as pd

iv = b'\0' * 16
headers = {'User-Agent': 'Android'}


def encrypt(text, key):
    aeskey = hashlib.sha256(key.encode('utf-8')).digest()
    aes = AES.new(aeskey, AES.MODE_CFB, iv)
    return base64.b64encode(aes.encrypt(text))


def decrypt(encrypted, key='zG2nSeEfSHfvTCHy5LCcqtBbQehKNLXn'):
    aeskey = hashlib.sha256(key.encode('utf-8')).digest()
    aes = AES.new(aeskey, AES.MODE_CBC, iv)
    return pkcs7unpadding(aes.decrypt(base64.b64decode(encrypted)))


def pkcs7unpadding(data):
    length = len(data)
    unpadding = ord(chr(data[length - 1]))
    return data[0:length - unpadding]


def post(url, data, show=False):
    r = requests.post(url, data=data, headers=headers).text
    r = str(decrypt(r), encoding='unicode_escape').replace(r'\/', '/')
    r = re.sub(r'\"\[(.*?)\]\"', '""', r)
    if show:
        print(r)
    r = ujson.loads(r)
    if r['code'] != '100000':
        raise IOError(r['tip'])
    return r['data']


class Book:
    id = 0
    name = ''
    related_list = []   # 同类作品，为书ID的列表
    book_recommend_list = []     # 书荒推荐，为书ID的列表
    info = {}
    '''info参考样例：
    "book_info": {
		“book_id": "",
        "book_name": "",
        "description": "",          书的简介
        "book_src ": "",            书的来源
        "category_index ": "",      书的分类
        "tag ": "",                 一部分tag，str型，逗号分隔，不建议使用这个对象，有可能有缺失，下面有个taglist更全
        "total_word_count ": "",    总字数
        "up_status ": "",           暂时不知道有啥用
        "update_status ": "",       更新状态，1是完本
        "is_paid ": "",             是否收费，1是收费
        "discount ": "",            折扣，0~1小数表示几折，1不打折
        "discount_end_time ": "",   折扣结束时间
        "cover ": "",               封面，指向一个网页
        "author_name": "",          作者名
        "uptime": "",               上次更新时间
        "newtime": "",              创建时间
        "review_amount": "",        评论总数
        "reward_amount": "",        打赏总数
        "chapter_amount": "",       章节总数
        "is_original": "",          是否原创
        "total_click": "",          总点击
        "month_click": "",          月点击
        "week_click": "",           周点击
        "month_no_vip_click": "",   非VIP月点击
        "week_no_vip_click": "",    非VIP周点击
        "total_recommend": "",      总推荐票
        "month_recommend": "",      月推荐票
        "week_recommend": "",       周推荐票
        "total_favor": "",          暂时不知道是啥，怀疑是人气
        "month_favor": "",          同上
        "week_favor": "",           同上
        "current_yp": "",           当前月票
        "total_yp": "",             总月票
        "current_blade": "",        当前刀片
        "total_blade": "",          总刀片
        "week_fans_value": "",      周新增粉丝值
        "month_fans_value": "",     月新增粉丝值
        "total_fans_value": "",     总粉丝值
        "last_chapter_info": {      上次更新章节信息
            "chapter_id": "",       章节ID
            "book_id": "",          书ID
            "chapter_index": "",    章节索引
            "chapter_title": "",    章节名
            "uptime": "",           上传时间
            "mtime": "",            怀疑是发布时间
        },
        "tag_list": [{              tag信息，为数组
            "tag_id": "",           tag id，后期将实现根据tag id找书
            "tag_type": "",         tag类型，3是读者加的，1是作者加的
            "tag_name": ""          tag名
        }],
        "book_type": "",            书籍类型，暂时不知道是干嘛的
        "transverse_cover": ""      也不知道是干嘛的
    },
    "is_inshelf": "",               是否收藏
    "is_buy": "",                   是否订阅
    "up_reader_info": {             作者信息
        "reader_id": "",            这一堆都是用户信息模板，去看那个的注释
        "account": "",
        "reader_name": "",
        "avatar_url": "",
        "avatar_thumb_url": "",
        "base_status": "1",
        "exp_lv": "13",
        "exp_value": "44111",
        "gender": "1",
        "vip_lv": "3",
        "vip_value": "331000",
        "is_author": "1",
        "is_uploader": "0",
        "is_following": "0",
        "used_decoration": [],
        "is_in_blacklist": "0",
        "ctime": "2016-04-2815:35:37"
    }
    '''
    def __init__(self, id, UserInfo):
        r = post(urlList.BOOK_GET_INFO_BY_ID, {'book_id': id, **UserInfo})
        self.info = {
            'book_info': r['book_info'],
            'is_inshelf': r['is_inshelf'],
            'is_buy': r['is_buy'],
            'up_reader_info': r['up_reader_info']   # TODO: 更换成读者类
        }
        self.related_list = [it['book_id'] for it in r['related_list']]
        self.book_recommend_list = [it['book_id'] for it in r['book_shortage_reommend_list']]
        print(self.info)
        print(self.related_list)
        print(self.book_recommend_list)


class BookShelf:
    id = 0
    books = None
    count = 0
    end = False
    common = {}

    def __init__(self, id, UserInfo, loadCount=100):
        self.common = UserInfo
        self.id = id
        self.page = 0
        self.updateShelfNext(loadCount)
        print(self.books)

    def updateShelfNext(self, count=100):
        data = {'shelf_id': self.id, 'count': count, 'page': self.page, **self.common}
        infos = post(urlList.BOOKSHELF_GET_SHELF_BOOK_LIST, data)['book_list']
        if len(infos) == 0:
            self.end = True
        else:

            def processInfo(info):
                return {
                    'id': info['book_info']['book_id'],
                    'name': info['book_info']['book_name'],
                    'category': int(info['book_info']['category_index']),
                    'words': info['book_info']['total_word_count'],
                    'discount': info['book_info']['discount'],
                    'discount_end_time': info['book_info']['discount_end_time'],
                    'cover': info['book_info']['cover'],
                    'author': info['book_info']['author_name'],
                    'uptime': info['book_info']['uptime'],
                    'review_amount': info['book_info']['review_amount'],
                    'last_chapter_id': info['book_info']['last_chapter_info']['chapter_id'],
                    'last_chapter_index': info['book_info']['last_chapter_info']['chapter_index'],
                    'last_chapter_title': info['book_info']['last_chapter_info']['chapter_title'],
                    'top': info['top_time'],
                    'last_read_chapter_id': info['last_read_chapter_id'],
                    'last_read_chapter_title': info['last_read_chapter_title'],
                    'last_read_time': time.localtime(int(info['last_read_chapter_update_time']))
                }

            pool = ThreadPool()
            results = pool.map(processInfo, infos)
            pool.close()
            pool.join()
            self.count += len(results)
            self.page += 1
            if self.books is not None:
                self.books = self.books.append(pd.DataFrame(results))
            else:
                self.books = pd.DataFrame(results)
            print(len(self.books))
            self.books.sort_values(by=["top", "last_read_time"], axis=0, ascending=[False, False], inplace=True)
            self.books.reset_index(drop=True)

    def load2end(self, wait=1):
        while not self.end:
            self.updateShelfNext()
            time.sleep(wait)
        print(self.books)


class Session:
    key = 'zG2nSeEfSHfvTCHy5LCcqtBbQehKNLXn'
    login = False
    userInfo = {}
    commonUserInfo = {'account': None, 'login_token': None, 'app_version': '2.6.020'}

    def __init__(self, loginToken=None, account=None):
        if loginToken is not None and account is not None:
            self.commonUserInfo = {
                'account': account,
                'login_token': loginToken,
                'app_version': '2.6.020'
            }

    def login(self, user, passwd):
        self.userInfo = post(urlList.MY_SIGN_LOGIN, {'login_name': user, 'passwd': passwd})
        self.commonUserInfo = {
            'account': self.userInfo['reader_info']['account'],
            'login_token': self.userInfo['login_token'],
            'app_version': '2.6.020'
        }
        return {
            'account': self.userInfo['reader_info']['account'],
            'login_token': self.userInfo['login_token']
        }

    def getBookShelfList(self):
        return post(urlList.BOOKSHELF_GET_SHELF_LIST, self.commonUserInfo)['shelf_list']

    def getBookShelf(self, id):
        return BookShelf(id, self.commonUserInfo)


def getBookShelf(session, id):
    return BookShelf(id, session.common)

