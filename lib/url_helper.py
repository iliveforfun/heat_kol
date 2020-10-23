'''
this file is used to get needed url
'''


def get_page_url(url, page, offset=25):
    # 豆瓣小组每一页的offset为25
    return url + str((page - 1) * offset)


if __name__ == '__main__':
    print(get_page_url('sss', 1))
