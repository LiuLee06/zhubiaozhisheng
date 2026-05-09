# check_user_password.py
from src.Webapp import create_app, db
from src.Webapp.models import USER
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

with app.app_context():
    print("=== 检查用户密码详情 ===")

    # 检查所有用户
    users = USER.query.all()
    print(f"用户总数: {len(users)}")

    for user in users:
        print(f"\n--- 用户: {user.username} ---")
        print(f"ID: {user.id}")
        print(f"密码哈希字段: {user.password_hash}")
        print(f"密码哈希长度: {len(user.password_hash) if user.password_hash else 0}")

        # 测试密码验证
        test_passwords = ['123456', 'password', 'admin']  # 常见的测试密码
        for test_pwd in test_passwords:
            is_match = check_password_hash(user.password_hash, test_pwd)
            print(f"测试密码 '{test_pwd}': {'✅ 匹配' if is_match else '❌ 不匹配'}")