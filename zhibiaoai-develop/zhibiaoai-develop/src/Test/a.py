from src.main import app

print(app.static_folder)  # 应该显示完整路径到src/Webapp/Static
print(app.static_url_path)  # 应该显示/static