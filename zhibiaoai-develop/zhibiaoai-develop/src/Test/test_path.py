import os
from src.main import create_app

app = create_app()

with app.app_context():
    print("Template folder:", app.template_folder)
    print("Static folder:", app.static_folder)
    print("Upload folder:", app.config['UPLOAD_FOLDER'])

    # 检查模板文件是否存在
    template_files = ['index.html', 'auth/login.html', 'bidding/home.html']
    for template in template_files:
        template_path = os.path.join(app.template_folder, template)
        print(f"Template {template}: {'Exists' if os.path.exists(template_path) else 'Missing'}")