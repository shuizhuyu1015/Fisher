"""
    create by Gray 2019-04-21
"""
from collections import namedtuple
from .book import BookViewModel


# namedtuple快速定义一个对象，参数：对象名，[]里设置属性名
MyGift = namedtuple('MyGift', ['id', 'book', 'wishes_count'])


class MyGifts:
    def __init__(self, gifts_of_mine, wish_count_list):
        self.gifts = []

        self.__gifts_of_mine = gifts_of_mine
        self.__wish_count_list = wish_count_list

        self.gifts = self.__parse()

    def __parse(self):
        temp_gifts = []
        for gift in self.__gifts_of_mine:
            my_gift = self.__matching(gift)
            temp_gifts.append(my_gift)
        return temp_gifts

    def __matching(self, gift):
        count = 0
        for wish_count in self.__wish_count_list:
            if gift.isbn == wish_count['isbn']:
                count = wish_count['count']
        r = {
            'wishes_count': count,
            'book': BookViewModel(gift.book),
            'id': gift.id
        }
        return r
        # my_gift = MyGift(gift.id, BookViewModel(gift.book), count)
        # return my_gift


# class MyGift:
#     def __init__(self):
#         pass