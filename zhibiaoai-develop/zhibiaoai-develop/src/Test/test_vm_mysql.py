# test_vm_mysql.py
import pymysql
from pymysql.cursors import DictCursor  # 导入DictCursor
from src.Webapp.config import Config

def test_mysql_connection():
    """测试MySQL数据库连接"""
    try:
        print("正在测试MySQL连接...")
        print(f"主机: 192.168.111.152")
        print(f"数据库: Anuo")
        print(f"用户: root")

        # 使用DictCursor获取字典格式的结果
        connection = pymysql.connect(
            host='192.168.111.152',
            user='root',
            password='123456',
            database='Anuo',
            charset='utf8mb4',
            connect_timeout=10,
            cursorclass=DictCursor  # 使用字典游标
        )

        print("✅ MySQL连接成功！")

        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            version = cursor.fetchone()
            print(f"MySQL版本: {version['version']}")  # 现在可以用字典方式访问

            # 检查表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"现有表: {[table['Tables_in_Anuo'] for table in tables]}")

        connection.close()
        return True

    except pymysql.err.OperationalError as e:
        error_code = e.args[0]
        error_message = e.args[1]

        print(f"❌ MySQL连接错误 (代码 {error_code}): {error_message}")

        if error_code == 1045:  # 访问被拒绝
            print("可能的原因: 用户名或密码错误")
        elif error_code == 1049:  # 数据库不存在
            print("可能的原因: 数据库 'Anuo' 不存在")
            print("请先在MySQL中创建数据库: CREATE DATABASE Anuo;")
        elif error_code == 2003:  # 无法连接
            print("可能的原因: MySQL服务未运行或网络问题")
        elif error_code == 1130:  # 主机不允许连接
            print("可能的原因: MySQL用户权限配置问题")
            print("需要在MySQL中执行: GRANT ALL ON Anuo.* TO 'root'@'%';")

        return False

    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def create_database_if_needed():
    """如果数据库不存在则创建"""
    try:
        print("检查数据库是否存在...")

        connection = pymysql.connect(
            host='192.168.111.152',
            user='root',
            password='123456',
            charset='utf8mb4',
            cursorclass=DictCursor  # 这里也添加
        )

        with connection.cursor() as cursor:
            # 检查数据库是否存在
            cursor.execute("SHOW DATABASES LIKE 'Anuo'")
            result = cursor.fetchone()

            if not result:
                print("数据库 'Anuo' 不存在，正在创建...")
                cursor.execute("CREATE DATABASE Anuo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print("✅ 数据库创建成功")
            else:
                print("✅ 数据库已存在")

        connection.close()
        return True

    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

if __name__ == '__main__':
    print("虚拟机MySQL连接测试")
    print("=" * 50)

    # 1. 首先创建数据库（如果不存在）
    if create_database_if_needed():
        print("\n" + "=" * 30)
        # 2. 测试连接
        test_mysql_connection()