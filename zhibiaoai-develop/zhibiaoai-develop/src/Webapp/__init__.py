"""
应用初始化文件
"""
import os
import pymysql
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from Webapp.config import Config

db = SQLAlchemy()

def ensure_database_exists():
    """
    自动创建数据库（如果不存在）
    """
    try:
        # 从配置中解析数据库连接信息
        db_uri = Config.SQLALCHEMY_DATABASE_URI
        # 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
        
        # 解析连接字符串
        import re
        pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/([^?]+)'
        match = re.match(pattern, db_uri)
        
        if not match:
            print("警告: 无法解析数据库连接字符串")
            return
        
        user, password, host, port, database = match.groups()
        
        # 先连接MySQL（不指定数据库）
        connection = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        try:
            with connection.cursor() as cursor:
                # 创建数据库（如果不存在）
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"✓ 数据库 '{database}' 已就绪")
            connection.commit()
        finally:
            connection.close()
            
    except Exception as e:
        print(f"创建数据库时出错: {e}")
        print("请确保MySQL服务正在运行，并且配置信息正确")

def init_database_tables(app):
    """
    创建所有数据表并初始化默认数据
    """
    with app.app_context():
        try:
            # 导入所有模型以确保它们被注册
            from Webapp.models import USER, FileRecord
            
            # 创建所有表
            db.create_all()
            print("✓ 数据库表已创建")
            
            # 检查并创建默认管理员用户
            if not USER.query.filter_by(username='root').first():
                admin_user = USER(
                    username='root',
                    email='root@163.com'
                )
                admin_user.set_password('123456')
                db.session.add(admin_user)
                db.session.commit()
                print("✓ 默认管理员用户已创建 (用户名: root, 密码: 123456)")
            else:
                print("✓ 默认管理员用户已存在")
                
        except Exception as e:
            print(f"初始化数据表时出错: {e}")
            db.session.rollback()

# 应用工厂函数，用于创建 Flask 应用
def create_app():
    # 计算模板和静态文件的绝对路径
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    TemplateDir = os.path.join(base_dir, 'Webapp', 'Templates')
    StaticDir = os.path.join(base_dir, 'Webapp')
    app = Flask(__name__,
                template_folder=TemplateDir)
    # 加载配置
    app.config.from_object(Config)

    # 允许所有域的跨域请求
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # 自动创建数据库（如果不存在）
    ensure_database_exists()

    # 初始化数据库
    db.init_app(app)

    # 自动创建所有表并初始化数据
    init_database_tables(app)

    # 导入并注册蓝图
    from Webapp.Auth.routes import bp as auth_bp
    from Webapp.Bidding.routes import bp as bidding_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(bidding_bp)

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app
