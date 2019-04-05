"""
    create by Gray 2019-03-18
"""
from flask import jsonify, request, render_template, flash
import json

from app.libs.helper import is_isbn_or_key
from app.spider.yushu_book import YuShuBook
from app.web.blueprint import web
from app.forms.book import SearchForm
from app.view_models.book import BookViewModel, BookCollection


@web.route('/book/search')
def search():
    """
        q: 普通关键字 isbn
        page
        ?q=金庸&page=1
    """
    form = SearchForm(request.args)
    books = BookCollection()

    if form.validate():
        q = form.q.data.strip()
        page = form.page.data
        isbn_or_key = is_isbn_or_key(q)
        yushu_book = YuShuBook()

        if isbn_or_key == 'isbn':
            yushu_book.search_by_isbn(q)
        else:
            yushu_book.search_by_keyword(q, page)

        books.fill(yushu_book, q)

        # 对象序列化，返回字典
        # return json.dumps(books, default=lambda o: o.__dict__)
        # return jsonify(books)
        # return json.dumps(result), 200, {'content-type':'application/json'}
    else:
        flash('搜索的关键字不符合要求，请重新输入关键字')
        # return jsonify(form.errors)
    return render_template('search_result.html', books=books)


@web.route('/book/<isbn>/detail')
def book_detail(isbn):
    pass


@web.route('/test')
def test():
    r = {
        'name': 'gray',
        'age': 19
    }
    return render_template('test.html', data=r)

# @web.route('/hello')
# def hello():
#     return 'hello world', 200, {'content-type':'text/plain'}
