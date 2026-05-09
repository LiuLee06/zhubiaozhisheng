"""测试能否连接到虚拟机和3306端口"""
import socket
import subprocess


def test_ping(host):
    """测试ping通虚拟机"""
    try:
        # Windows系统
        result = subprocess.run(['ping', '-n', '4', host],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ 可以ping通 {host}")
            return True
        else:
            print(f"❌ 无法ping通 {host}")
            return False
    except Exception as e:
        print(f"❌ Ping测试失败: {e}")
        return False


def test_port(host, port=3306):
    """测试端口连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"✅ 端口 {port} 可以访问")
            return True
        else:
            print(f"❌ 端口 {port} 无法访问 (错误代码: {result})")
            return False
    except Exception as e:
        print(f"❌ 端口测试失败: {e}")
        return False


if __name__ == '__main__':
    host = '192.168.111.152'
    print(f"测试连接到虚拟机: {host}")
    print("=" * 50)

    test_ping(host)
    test_port(host, 3306)