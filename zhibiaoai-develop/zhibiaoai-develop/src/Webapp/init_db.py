"""
用于初始化数据库的脚本
"""
from src.Webapp import db, create_app
from src.Webapp.models import USER

def init_database():
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()

        # 创建默认管理员用户（如果不存在）
        if not USER.query.filter_by(username='root').first():
            admin_user = USER(
                username='root',
                email='root@163.com'
            )
            admin_user.set_password('123456')
            db.session.add(admin_user)
            db.session.commit()
            print('默认管理员用户已创建: root/123456')

        print('数据库初始化完成！')

if __name__ == '__main__':
    init_database()