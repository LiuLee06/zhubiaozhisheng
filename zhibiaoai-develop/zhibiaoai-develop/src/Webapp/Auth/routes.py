"""认证路由蓝图 - 处理登录、注册、注销等"""
from flask import Blueprint, render_template, request, session, jsonify, flash, url_for, redirect
from Webapp import db
from Webapp.Auth.forms import LoginForm, RegistrationForm
from Webapp.models import USER

# 创建认证蓝图
bp = Blueprint('auth', __name__,
               url_prefix='/auth',
               template_folder='../../Templates/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('bidding.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = USER.query.filter_by(username=form.username.data).first()
        # 直接比较明文密码
        if user and user.password == form.password.data:
            session['user_id'] = user.id
            session['username'] = user.username
            user.update_last_login()
            flash('登录成功', 'success')
            return redirect(url_for('bidding.home'))
        else:
            flash('用户名或密码错误', 'error')

    return render_template('auth/login.html', form=form)

@bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的JSON数据'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400

    user = USER.query.filter_by(username=username).first()
    # 直接比较明文密码
    if user and user.password == password:
        session['user_id'] = user.id
        session['username'] = user.username
        user.update_last_login()
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {'id': user.id, 'username': user.username},
            'redirect': url_for('bidding.home')
        })

    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@bp.route('/logout')
def logout():
    session.clear()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = USER(username=form.username.data, email=form.email.data or None)
        # 直接存储明文密码
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@bp.route('/api/current_user')
#获取当前用户信息
def current_user():
    if 'user_id' in session:
        user = USER.query.get(session['user_id'])
        return jsonify({
            'authenticated': True,
            'user': user.to_dict()
        })
    return jsonify({'authenticated': False})