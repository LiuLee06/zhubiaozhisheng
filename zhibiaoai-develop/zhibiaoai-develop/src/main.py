"""
初始化Flask应用并启动开发服务器（ flask run 的替代）
"""
from flask import render_template
from Webapp import create_app

# 创建应用实例
app = create_app()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)