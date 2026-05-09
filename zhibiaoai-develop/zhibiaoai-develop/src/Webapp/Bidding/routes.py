"""
标书管理路由蓝图 - 处理文件上传、标书生成等
"""
import os
import uuid
import textwrap
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, session, url_for, redirect
from PyPDF2 import PdfReader
from docx import Document
from Webapp import db
from Webapp.config import Config
from Webapp.models import FileRecord

# 创建标书管理蓝图
bp = Blueprint('bidding', __name__,
               url_prefix='/bidding',
               template_folder='../../Templates/bidding')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# 标书管理页
@bp.route('/')
@bp.route('/home')
def home():
    if 'user_id' not in session:
        flash('请先登录', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('bidding/home.html')

# 项目管理页
@bp.route('/projects')
def projects():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('bidding/projects.html')

# 资质管理页
@bp.route('/qualifications')
def qualifications():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('bidding/qualifications.html')

# 标书生成页
@bp.route('/bid-generator')
def bid_generator():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('bidding/bid-generator.html')

# 模版管理页
@bp.route('/templates')
def templates():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('bidding/templates.html')

# 解析结果查看页
@bp.route('/view-parsed-result')
def view_parsed_result():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # 获取查询参数
    qualification_id = request.args.get('id', '')
    qualification_name = request.args.get('name', '')

    # 模拟解析结果数据
    data = {
        "qualification_id": qualification_id,
        "file_info": {
            "qualification_name": qualification_name,
            "qualification_type_cn": "施工资质",
            "original_name": f"{qualification_name}.pdf",
            "file_extension": "pdf",
            "expiry_date": "2025-12-31",
            "upload_date": "2024-01-15",
            "is_valid": True
        },
        "content": f"这是{qualification_name}的解析内容。\n\n该资质证书包含以下信息：\n- 资质等级：一级\n- 发证机关：建设行政主管部门\n- 有效期至：2025年12月31日\n- 业务范围：可承担各类建筑工程施工",
        "parsed_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return render_template('bidding/parsed_result.html', data=data)

# 文档解析API
@bp.route('/document/<int:doc_id>', methods=['POST'])
def process_document(doc_id):
    if 'user_id' not in session:
        return jsonify({"error": "未登录"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "未上传文件，请在form-data中添加键为'file'的文件"}), 400

    file = request.files['file']
    user_id = session['user_id']

    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    # 创建用户目录
    user_dir = os.path.join(Config.UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    try:
        file_ext = os.path.splitext(file.filename)[1].lower()
        save_filename = f"doc_{doc_id}{file_ext}"
        save_path = os.path.join(user_dir, save_filename)

        file.save(save_path)
    except Exception as e:
        return jsonify({"error": f"文件保存失败: {str(e)}"}), 500

    try:
        with open(save_path, 'rb') as f:
            if file.filename.endswith('.pdf'):
                content = parse_pdf(f)
            elif file.filename.endswith('.docx'):
                content = parse_docx(f)
            else:
                os.remove(save_path)
                return jsonify({"error": "仅支持 PDF 和 DOCX 格式的文件"}), 400
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        return jsonify({"error": f"解析失败: {str(e)}"}), 500

    summary = generate_summary(content)

    # 记录到数据库
    file_record = FileRecord(
        user_id=user_id,
        file_path=save_path,
        file_name=file.filename,
        file_type=file_ext,
        file_size=os.path.getsize(save_path),
        status='解析完成'
    )
    db.session.add(file_record)
    db.session.commit()

    return jsonify({
        "doc_id": doc_id,
        "filename": file.filename,
        "saved_path": save_path,
        "original_text": content,
        "summary": summary,
        "file_id": file_record.id
    })

# PDF解析函数
def parse_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()

# Word文档解析函数
def parse_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        if para.text.strip():
            text += para.text + "\n"
    return text.strip()

# 生成摘要函数
def generate_summary(full_text, max_length=300):
    if not full_text:
        return "文档内容为空，无法生成摘要"
    return textwrap.shorten(full_text, width=max_length, placeholder="...")

#文件上传API
@bp.route('/api/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400

    file = request.files['file']
    user_id = session['user_id']

    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if file and allowed_file(file.filename):
        # 生成唯一文件名
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"

        # 创建用户ID/日期目录结构
        today = datetime.now().strftime('%Y-%m-%d')
        upload_dir = os.path.join(Config.UPLOAD_FOLDER, str(user_id), today)
        os.makedirs(upload_dir, exist_ok=True)

        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)

        # 记录到数据库
        file_record = FileRecord(
            user_id=user_id,
            file_path=file_path,
            file_name=file.filename,
            file_type=file_ext,
            file_size=os.path.getsize(file_path),
            status='上传成功，等待处理'  # 添加初始状态
        )

        db.session.add(file_record)
        db.session.commit()

        # 同步处理文件
        try:
            from Webapp.tasks import process_uploaded_file
            result = process_uploaded_file(file_record)
            
            return jsonify({
                'success': True,
                'message': '文件上传并处理成功！',
                'file_id': file_record.id,
                'file_name': file.filename,
                'content': result.get('content', ''),
                'summary': result.get('summary', '')
            }), 200
        except Exception as e:
            file_record.status = f'处理失败: {str(e)}'
            db.session.commit()
            return jsonify({
                'success': False,
                'error': f'文件处理失败: {str(e)}'
            }), 500

    return jsonify({'error': '不支持的文件格式'}), 400

# 获取用户文件列表
@bp.route('/api/files')
def list_files():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401

    user_id = session['user_id']
    files = FileRecord.query.filter_by(user_id=user_id).order_by(FileRecord.upload_time.desc()).all()

    file_list = []
    for file in files:
        file_list.append({
            'id': file.id,
            'name': file.file_name,
            'type': file.file_type,
            'size': file.file_size,
            'upload_time': file.upload_time.isoformat(),
            'status': file.status,
            'path': file.file_path  # 可选：返回文件路径
        })

    return jsonify({'files': file_list})

# 生成标书API
@bp.route('/api/generate-bid', methods=['POST'])
def generate_bid_route():
    print("=" * 50)
    print("收到生成标书请求！")
    print("=" * 50)
    
    if 'user_id' not in session:
        print("用户未登录")
        return jsonify({'error': '未登录'}), 401

    data = request.get_json()
    print(f"接收到的数据：{data}")
    user_id = session['user_id']
    print(f"用户ID：{user_id}")

    # 同步生成标书
    try:
        print("开始调用 generate_bid 函数...")
        from Webapp.tasks import generate_bid
        result = generate_bid(user_id, data)
        print(f"生成结果：{result}")

        return jsonify({
            'success': True,
            'message': '标书生成成功！',
            'document_path': result.get('document_path', ''),
            'result': result.get('result', {})
        }), 200
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"生成标书时发生错误：")
        print(error_detail)
        
        return jsonify({
            'success': False,
            'error': f'标书生成失败: {str(e)}'
        }), 500

# 已移除任务状态API（不再需要异步跟踪）

# 已移除文件状态更新API（不再需要异步回调）