"""
配置类文件
"""
import os

class Config:
    # 计算基础路径
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@localhost:3306/Anuo?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'Webapp', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    # 允许的文件格式
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    # Session配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_TYPE = 'filesystem'
    
    # AI API 配置 - 豆包
    AI_API_KEY = 'e53b68fa-3414-45ff-879a-883f4c56bbc3'
    AI_BASE_URL = 'https://ark.cn-beijing.volces.com/api/v3'
    AI_MODEL = 'doubao-seed-1-6-flash-250828'



