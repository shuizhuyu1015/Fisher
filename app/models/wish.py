"""
    create by Gray 2019-04-14
"""

from sqlalchemy import Column, Integer, Boolean, String, ForeignKey, desc, func
from sqlalchemy.orm import relationship
from app.models.base import Base, db
from app.spider.yushu_book import YuShuBook


class Wish(Base):
    id = Column(Integer, primary_key=True)
    launched = Column(Boolean, default=False)
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))
    isbn = Column(String(15), nullable=False)

    @classmethod
    def get_user_wishes(cls, uid):
        wishes = Wish.query.filter_by(uid=uid, launched=False).order_by(desc(Wish.create_time)).all()
        return wishes

    @classmethod
    def get_gift_count(cls, isbn_list):
        from app.models.gift import Gift
        # 根据传入的一组isbn，到Gift表中检索出相应的礼物，并计算出某个礼物的可赠送人数
        count_list = db.session.query(func.count(Gift.id), Gift.isbn).filter(
            Gift.launched == False,
            Gift.isbn.in_(isbn_list),
            Gift.status == 1).group_by(
            Gift.isbn).all()
        count_list = [{'count': g[0], 'isbn': g[1]} for g in count_list]
        return count_list

    @property
    def book(self):
        yushu_book = YuShuBook()
        yushu_book.search_by_isbn(self.isbn)
        return yushu_book.first

    def delete(self):
        self.status = 0
