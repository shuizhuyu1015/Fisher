from flask import flash, redirect, url_for, render_template, request
from sqlalchemy import or_, desc

from app.libs.email import send_email
from app.libs.enums import PendingStatus
from app.models.user import User
from app.models.wish import Wish
from app.view_models.book import BookViewModel
from app.view_models.drift import DriftCollection
from app.forms.book import DriftForm
from app.models.base import db
from app.models.drift import Drift
from app.models.gift import Gift
from app.web.blueprint import web
from flask_login import login_required, current_user

__author__ = '七月'


@web.route('/drift/<int:gid>', methods=['GET', 'POST'])
@login_required
def send_drift(gid):
    current_gift = Gift.query.get_or_404(gid)
    if current_gift.is_yourself_gift(current_user.id):
        flash('这本书是你自己的，不能向自己索要书籍哦')
        return redirect(url_for('web.book_detail', isbn=current_gift.isbn))

    can = current_user.can_send_drift()
    if not can:
        return render_template('not_enough_beans.html', beans=current_user.beans)

    form = DriftForm(request.form)
    if request.method == 'POST' and form.validate():
        save_drift(form, current_gift)
        send_email(current_gift.user.email, '有人想要一本书', 'email/get_gift.html',
                   wisher=current_user,
                   gift=current_gift)

    gifter = current_gift.user.summary
    return render_template('drift.html', gifter=gifter, user_beans=current_user.beans, form=form)


@web.route('/pending')
@login_required
def pending():
    drifts = Drift.query.filter(or_(Drift.requester_id == current_user.id,
                                    Drift.gifter_id == current_user.id)).order_by(desc(Drift.create_time)).all()
    drifts_view_model = DriftCollection(drifts, current_user.id)
    return render_template('pending.html', drifts=drifts_view_model.data)


@web.route('/drift/<int:did>/reject')
@login_required
def reject_drift(did):
    with db.auto_commit():
        # 防止超权，书籍的赠送者要是登录人，才可以拒绝该交易
        drift = Drift.query.filter(Gift.id == current_user.id, Drift.id == did).first_or_404()
        drift.pending = PendingStatus.Reject
        requester = User.query.get_or_404(drift.requester_id)
        requester.beans += 1
    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/redraw')
@login_required
def redraw_drift(did):
    with db.auto_commit():
        # 防止超权，书籍的索要者要是登录人，才可成功撤销交易
        drift = Drift.query.filter_by(requester_id=current_user.id, id=did).first_or_404()
        drift.pending = PendingStatus.Redraw
        current_user.beans += 1
    return redirect(url_for('web.pending'))


@web.route('/drift/<int:did>/mailed')
@login_required
def mailed_drift(did):
    with db.auto_commit():
        drift = Drift.query.filter_by(gifter_id=current_user.id, id=did).first_or_404()
        drift.pending = PendingStatus.Success
        current_user.beans += 1
        # 书籍赠送成功，将礼物的发送状态改为True
        gift = Gift.query.filter_by(id=drift.gift_id).first_or_404()
        gift.launched = True
        # 书籍赠送成功，将该书籍对应的索要者的心愿改为已完成状态（launched: True）
        Wish.query.filter_by(isbn=drift.isbn, uid=drift.requester_id, launched=False).update({Wish.launched: True})
    return redirect(url_for('web.pending'))


def save_drift(drift_form, current_gift):
    with db.auto_commit():
        drift = Drift()
        # 如果数据库字段和form里定义的字段相同，可使用下面的额方法一次把form里的数据导入到数据库
        drift_form.populate_obj(drift)

        drift.gift_id = current_gift.id
        drift.requester_id = current_user.id
        drift.requester_nickname = current_user.nickname
        drift.gifter_nickname = current_gift.user.nickname
        drift.gifter_id = current_gift.user.id

        book = BookViewModel(current_gift.book)

        drift.book_title = book.title
        drift.book_author = book.author
        drift.book_img = book.image
        drift.isbn = book.isbn

        current_user.beans -= 1

        db.session.add(drift)
