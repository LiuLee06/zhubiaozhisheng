"""测试MySQL数据库连接"""
import pymysql
from pymysql.cursors import DictCursor


def test_mysql_connection():
    try:
        print("正在测试MySQL连接...")
        print(f"主机: 192.168.111.152")
        print(f"数据库: Anuo")
        print(f"用户: root")

        # 修改连接参数
        connection = pymysql.connect(
            host='192.168.111.152',  # 直接使用IP地址
            user='root',
            password='123456',
            database='Anuo',
            charset='utf8mb4',
            connect_timeout=10,
            cursorclass=DictCursor
        )

        print("✅ MySQL连接成功！")

        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            version = cursor.fetchone()
            print(f"MySQL版本: {version['version']}")

        connection.close()
        return True

    except pymysql.err.OperationalError as e:
        print(f"❌ MySQL连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False


if __name__ == '__main__':
    test_mysql_connection()