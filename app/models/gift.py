"""
    create by Gray 2019-04-10
"""
from flask import current_app
from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, desc, func
from sqlalchemy.orm import relationship
from app.models.base import Base, db
from app.spider.yushu_book import YuShuBook
from collections import namedtuple


# 快速定义一个对象的方法
EachGiftWishCount = namedtuple('EachGiftWishCount', ['count', 'isbn'])


class Gift(Base):
    id = Column(Integer, primary_key=True)
    launched = Column(Boolean, default=False)
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    isbn = Column(String(15), nullable=False)

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    def is_yourself_gift(self, uid):
        return True if uid == self.uid else False

    @classmethod
    def get_user_gifts(cls, uid):
        gifts = Gift.query.filter_by(uid=uid, launched=False).order_by(desc(Gift.create_time)).all()
        return gifts

    @classmethod
    def get_wish_count(cls, isbn_list):
        from app.models.wish import Wish
        # 根据传入的一组isbn，到Wish表中检索出相应的礼物，并计算出某个礼物的Wish心愿数量
        count_list = db.session.query(func.count(Wish.id), Wish.isbn).filter(
            Wish.launched == False,
            Wish.isbn.in_(isbn_list),
            Wish.status == 1).group_by(
            Wish.isbn).all()
        count_list = [{'count': w[0], 'isbn': w[1]} for w in count_list]
        return count_list

    @classmethod
    def recent(cls):
        recent_gift = Gift.query.filter_by(
            launched=False).group_by(
            Gift.isbn).order_by(
            desc(Gift.create_time)).limit(
            current_app.config['RECENT_BOOK_COUNT']).distinct().all()
        return recent_gift

    def delete(self):
        self.status = 0
