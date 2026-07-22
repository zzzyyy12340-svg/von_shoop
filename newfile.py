from flask import Flask, request, jsonify, render_template, render_template_string, session, redirect, url_for, send_file
import json
import os
import random
import datetime
import hashlib
import uuid

app = Flask(__name__)
app.secret_key = "vpn_shop_secret_key_2024"
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ========== تنظیمات ==========
CARD_SETTINGS = {
    "number": "6037-9917-1234-5678",
    "owner": "علی رضایی",
    "bank": "بانک ملت"
}

PRODUCTS = [
    {"id": 1, "name": "🌐 VPN حجمی ۱۰ گیگ", "price": 50000, "type": "volume", "value": 10, "stock": 100, "duration": "نامحدود"},
    {"id": 2, "name": "🌐 VPN حجمی ۵۰ گیگ", "price": 200000, "type": "volume", "value": 50, "stock": 100, "duration": "نامحدود"},
    {"id": 3, "name": "🌐 VPN حجمی ۱۰۰ گیگ", "price": 350000, "type": "volume", "value": 100, "stock": 100, "duration": "نامحدود"},
    {"id": 4, "name": "🚀 VPN نامحدود ۱ ماهه", "price": 150000, "type": "unlimited", "value": 1, "stock": 50, "duration": "۱ ماه"},
    {"id": 5, "name": "🚀 VPN نامحدود ۳ ماهه", "price": 400000, "type": "unlimited", "value": 3, "stock": 50, "duration": "۳ ماه"},
    {"id": 6, "name": "🚀 VPN نامحدود ۶ ماهه", "price": 700000, "type": "unlimited", "value": 6, "stock": 30, "duration": "۶ ماه"},
    {"id": 7, "name": "🚀 VPN نامحدود ۱ ساله", "price": 1200000, "type": "unlimited", "value": 12, "stock": 20, "duration": "۱۲ ماه"},
]

USERS = {}
ORDERS = []
PAYMENTS = []
CART = {}
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456"

# ========== صفحات ==========
@app.route('/')
def home():
    return render_template_string(HTML_MAIN, products=PRODUCTS)

@app.route('/admin')
def admin_login():
    return render_template_string(HTML_ADMIN_LOGIN)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/admin')
    total_orders = len(ORDERS)
    total_products = len(PRODUCTS)
    total_users = len(USERS)
    pending_payments = len([p for p in PAYMENTS if p["status"] == "pending"])
    return render_template_string(HTML_ADMIN_DASHBOARD, total_orders=total_orders, total_products=total_products, total_users=total_users, pending_payments=pending_payments, payments=PAYMENTS, products=PRODUCTS, card=CARD_SETTINGS)

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect('/admin/dashboard')
    return "❌ نام کاربری یا رمز عبور اشتباه است!"

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

@app.route('/admin/add-product', methods=['POST'])
def add_product():
    if not session.get('admin_logged_in'):
        return "Unauthorized", 401
    data = request.form
    new_id = max([p["id"] for p in PRODUCTS]) + 1 if PRODUCTS else 1
    PRODUCTS.append({
        "id": new_id,
        "name": data.get('name'),
        "price": int(data.get('price')),
        "type": data.get('type'),
        "value": int(data.get('value')),
        "stock": int(data.get('stock')),
        "duration": data.get('duration')
    })
    return redirect('/admin/dashboard')

@app.route('/admin/delete-product/<int:product_id>')
def delete_product(product_id):
    if not session.get('admin_logged_in'):
        return "Unauthorized", 401
    global PRODUCTS
    PRODUCTS = [p for p in PRODUCTS if p["id"] != product_id]
    return redirect('/admin/dashboard')

@app.route('/admin/update-product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    if not session.get('admin_logged_in'):
        return "Unauthorized", 401
    for p in PRODUCTS:
        if p["id"] == product_id:
            p["name"] = request.form.get('name')
            p["price"] = int(request.form.get('price'))
            p["stock"] = int(request.form.get('stock'))
            break
    return redirect('/admin/dashboard')

@app.route('/admin/update-card', methods=['POST'])
def update_card():
    if not session.get('admin_logged_in'):
        return "Unauthorized", 401
    CARD_SETTINGS["number"] = request.form.get('number')
    CARD_SETTINGS["owner"] = request.form.get('owner')
    CARD_SETTINGS["bank"] = request.form.get('bank')
    return redirect('/admin/dashboard')

@app.route('/admin/approve-payment/<int:payment_id>')
def approve_payment(payment_id):
    if not session.get('admin_logged_in'):
        return "Unauthorized", 401
    for p in PAYMENTS:
        if p["id"] == payment_id:
            p["status"] = "approved"
            break
    return redirect('/admin/dashboard')

@app.route('/admin/reject-payment/<int:payment_id>')
def reject_payment(payment_id):
    if not session.get('admin_logged_in'):
        return "Unauthorized", 401
    for p in PAYMENTS:
        if p["id"] == payment_id:
            p["status"] = "rejected"
            break
    return redirect('/admin/dashboard')

@app.route('/admin/send-config/<int:payment_id>', methods=['POST'])
def send_config(payment_id):
    if not session.get('admin_logged_in'):
        return "Unauthorized", 401
    config = request.form.get('config')
    if not config:
        return "❌ لطفاً لینک اشتراک را وارد کنید!"
    
    for p in PAYMENTS:
        if p["id"] == payment_id:
            p["config"] = config
            p["status"] = "config_sent"
            break
    
    # صفحه تایید
    return render_template_string("""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head><meta charset="UTF-8"><title>✅ ارسال شد</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:'Tahoma',Arial,sans-serif;background:#0a0a1a;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px;color:#fff}
        .box{background:rgba(255,255,255,0.05);padding:40px;border-radius:20px;backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.08);max-width:500px;width:100%;text-align:center}
        h1{color:#2ed573;font-size:32px;margin-bottom:10px}
        .icon{font-size:60px;display:block;margin-bottom:15px}
        .info{background:rgba(255,255,255,0.05);padding:15px;border-radius:12px;margin:15px 0}
        .info strong{color:#ffd700}
        .btn{display:inline-block;background:#00d2ff;color:#fff;padding:12px 30px;border-radius:12px;text-decoration:none;font-weight:700;transition:0.3s;margin-top:10px}
        .btn:hover{opacity:0.85;transform:scale(1.02)}
        .btn-secondary{background:rgba(255,255,255,0.1)}
    </style>
    </head>
    <body>
        <div class="box">
            <span class="icon">✅</span>
            <h1>ارسال شد!</h1>
            <p style="color:#888;">لینک اشتراک با موفقیت برای کاربر ارسال شد.</p>
            <div class="info">
                <p>🆔 شماره سفارش: <strong>#{{ payment_id }}</strong></p>
                <p>🔗 لینک ارسال شده:</p>
                <code style="display:block;background:rgba(0,0,0,0.3);padding:10px;border-radius:8px;margin-top:5px;word-break:break-all;color:#00d2ff;">{{ config }}</code>
            </div>
            <a href="/admin/dashboard" class="btn">🔙 بازگشت به پنل</a>
            <a href="/" class="btn btn-secondary">🏠 فروشگاه</a>
        </div>
    </body>
    </html>
    """, payment_id=payment_id, config=config)

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    return redirect('/')

@app.route('/cart')
def show_cart():
    cart = session.get('cart', [])
    items = []
    total = 0
    for pid in cart:
        product = next((p for p in PRODUCTS if p["id"] == pid), None)
        if product:
            items.append(product)
            total += product["price"]
    return render_template_string(HTML_CART, items=items, total=total)

@app.route('/checkout', methods=['POST'])
def checkout():
    cart = session.get('cart', [])
    if not cart:
        return "سبد خرید خالی است!"
    total = sum([next((p["price"] for p in PRODUCTS if p["id"] == pid), 0) for pid in cart])
    payment_id = len(PAYMENTS) + 1
    PAYMENTS.append({
        "id": payment_id,
        "user": session.get('user', 'کاربر مهمان'),
        "amount": total,
        "receipt": "",
        "status": "pending",
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "config": ""
    })
    session['cart'] = []
    return render_template_string(HTML_CHECKOUT, payment_id=payment_id, total=total, card=CARD_SETTINGS)

@app.route('/upload-receipt', methods=['POST'])
def upload_receipt():
    payment_id = request.form.get('payment_id')
    if not payment_id:
        return "خطا: شماره پرداخت یافت نشد!"
    
    payment = next((p for p in PAYMENTS if p["id"] == int(payment_id)), None)
    if not payment:
        return "خطا: پرداخت یافت نشد!"
    
    if 'receipt' not in request.files:
        return "خطا: هیچ فایلی انتخاب نشده است!"
    
    file = request.files['receipt']
    if file.filename == '':
        return "خطا: فایل انتخاب نشده است!"
    
    if file:
        filename = f"receipt_{payment_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        payment["receipt"] = filename
        payment["status"] = "pending"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>✅ رسید ارسال شد</title></head>
        <body style="font-family:Tahoma;text-align:center;padding:50px;background:#0a0a1a;color:#fff;">
            <div style="max-width:500px;margin:auto;background:rgba(255,255,255,0.05);padding:30px;border-radius:20px;backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.08);">
                <h1 style="color:#2ed573;">✅ رسید شما با موفقیت ارسال شد!</h1>
                <p>🆔 شماره پیگیری: <strong>{payment_id}</strong></p>
                <p>💰 مبلغ: <strong>{payment["amount"]:,} تومان</strong></p>
                <p style="color:#888;">پس از تایید ادمین، کانفیگ برای شما ارسال خواهد شد.</p>
                <a href="/" style="display:inline-block;background:#00d2ff;color:#fff;padding:12px 30px;border-radius:15px;text-decoration:none;margin-top:20px;">🏠 بازگشت به فروشگاه</a>
            </div>
        </body>
        </html>
        """
    
    return "خطا در آپلود فایل!"

@app.route('/my-orders')
def my_orders():
    user_orders = [p for p in PAYMENTS if p["user"] == session.get('user', 'کاربر مهمان')]
    return render_template_string(HTML_MY_ORDERS, orders=user_orders)

@app.route('/get-config/<int:payment_id>')
def get_config(payment_id):
    payment = next((p for p in PAYMENTS if p["id"] == payment_id), None)
    if not payment:
        return "❌ سفارش یافت نشد!"
    if payment["status"] != "config_sent":
        return "❌ کانفیگ هنوز ارسال نشده است!"
    return render_template_string(HTML_GET_CONFIG, payment=payment)

# ========== HTML ها ==========
HTML_MAIN = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛒 Sabzin VPN</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Vazirmatn', sans-serif; background: #0a0a1a; min-height: 100vh; padding: 20px; color: #fff; }
        .header { background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%); padding: 20px 30px; border-radius: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,210,255,0.2); }
        .header h1 { font-size: 28px; color: #fff; }
        .header h1 span { color: #ffd700; }
        .header-links { display: flex; gap: 15px; align-items: center; flex-wrap: wrap; }
        .header-links a { color: white; text-decoration: none; font-weight: 700; padding: 10px 20px; background: rgba(255,255,255,0.15); border-radius: 12px; transition: 0.3s; backdrop-filter: blur(10px); }
        .header-links a:hover { background: rgba(255,255,255,0.3); transform: scale(1.03); }
        .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
        .product-card { background: rgba(255,255,255,0.06); border-radius: 20px; padding: 20px; text-align: center; border: 1px solid rgba(255,255,255,0.08); transition: 0.3s; backdrop-filter: blur(10px); }
        .product-card:hover { transform: translateY(-8px); border-color: #00d2ff; box-shadow: 0 15px 40px rgba(0,210,255,0.1); }
        .product-name { font-size: 16px; font-weight: 700; margin: 10px 0 5px; }
        .product-price { font-size: 20px; font-weight: 700; color: #00d2ff; }
        .product-stock { font-size: 12px; color: #888; margin: 5px 0; }
        .btn { background: linear-gradient(135deg, #00d2ff, #3a7bd5); color: white; border: none; padding: 10px 20px; border-radius: 12px; cursor: pointer; font-weight: 700; width: 100%; transition: 0.3s; font-family: inherit; }
        .btn:hover { opacity: 0.85; transform: scale(1.02); }
        .btn:disabled { opacity: 0.4; cursor: not-allowed; }
        @media (max-width: 600px) { .header { flex-direction: column; gap: 15px; text-align: center; } .products { grid-template-columns: 1fr 1fr; } }
        @media (max-width: 400px) { .products { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛒 <span>Sabzin</span> VPN</h1>
        <div class="header-links">
            <a href="/cart">🛍 سبد خرید ({{ session.get('cart', [])|length }})</a>
            <a href="/my-orders">📦 سفارشات من</a>
            <a href="/admin">👑 مدیریت</a>
        </div>
    </div>
    <div class="products">
        {% for p in products %}
        <div class="product-card">
            <div class="product-name">{{ p.name }}</div>
            <div class="product-price">{{ p.price|int|toLocaleString }} تومان</div>
            <div style="font-size:13px;color:#888;">{{ p.duration }} | {{ p.type }}</div>
            <div class="product-stock">{% if p.stock > 0 %}✅ موجود{% else %}❌ ناموجود{% endif %}</div>
            <a href="/add-to-cart/{{ p.id }}" class="btn" {% if p.stock < 1 %}disabled{% endif %}>➕ خرید</a>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

HTML_CART = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛒 سبد خرید</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Vazirmatn', sans-serif; background: #0a0a1a; min-height: 100vh; padding: 20px; color: #fff; }
        .container { max-width: 700px; margin: auto; background: rgba(255,255,255,0.05); border-radius: 20px; padding: 30px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.08); }
        h1 { text-align: center; color: #00d2ff; margin-bottom: 20px; }
        .item { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.06); align-items: center; flex-wrap: wrap; }
        .item .name { font-weight: 700; }
        .item .price { color: #00d2ff; font-weight: 700; }
        .total { text-align: center; font-size: 24px; font-weight: 700; color: #ffd700; padding: 20px 0; }
        .empty { text-align: center; color: #666; padding: 40px 0; }
        .actions { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-top: 20px; }
        .btn { background: linear-gradient(135deg, #00d2ff, #3a7bd5); color: white; padding: 12px 30px; border-radius: 12px; text-decoration: none; font-weight: 700; border: none; cursor: pointer; font-family: inherit; transition: 0.3s; }
        .btn:hover { opacity: 0.85; transform: scale(1.02); }
        .btn-secondary { background: rgba(255,255,255,0.1); }
        @media (max-width: 600px) { .container { padding: 15px; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛒 سبد خرید</h1>
        {% if items %}
            {% for item in items %}
            <div class="item">
                <span class="name">{{ item.name }}</span>
                <span class="price">{{ item.price|int|toLocaleString }} تومان</span>
            </div>
            {% endfor %}
            <div class="total">💰 مجموع: {{ total|int|toLocaleString }} تومان</div>
            <div class="actions">
                <form action="/checkout" method="POST" style="display:inline;">
                    <button class="btn">✅ ثبت سفارش</button>
                </form>
                <a href="/" class="btn btn-secondary">🏠 ادامه خرید</a>
            </div>
        {% else %}
            <div class="empty">🛒 سبد خرید خالی است!</div>
            <div class="actions"><a href="/" class="btn">🏠 بازگشت به فروشگاه</a></div>
        {% endif %}
    </div>
</body>
</html>
"""

HTML_CHECKOUT = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💳 پرداخت</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Vazirmatn', sans-serif; background: #0a0a1a; min-height: 100vh; padding: 20px; color: #fff; display: flex; align-items: center; justify-content: center; }
        .container { max-width: 500px; margin: auto; background: rgba(255,255,255,0.05); border-radius: 20px; padding: 30px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.08); }
        h1 { text-align: center; color: #ffd700; margin-bottom: 20px; }
        .info { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; margin: 10px 0; }
        .info strong { color: #00d2ff; }
        .card-box { background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 20px; border-radius: 15px; margin: 15px 0; border: 1px solid rgba(255,215,0,0.2); }
        .card-box p { margin: 8px 0; }
        .upload-area { border: 2px dashed rgba(255,255,255,0.2); padding: 30px; border-radius: 15px; text-align: center; margin: 15px 0; transition: 0.3s; cursor: pointer; }
        .upload-area:hover { border-color: #00d2ff; background: rgba(0,210,255,0.05); }
        .btn { background: linear-gradient(135deg, #00d2ff, #3a7bd5); color: white; padding: 12px 30px; border-radius: 12px; border: none; cursor: pointer; font-weight: 700; font-family: inherit; transition: 0.3s; width: 100%; margin-top: 10px; }
        .btn:hover { opacity: 0.85; transform: scale(1.02); }
        .btn-success { background: linear-gradient(135deg, #2ed573, #26de81); }
        .back { display: block; text-align: center; color: #888; margin-top: 15px; text-decoration: none; }
        .back:hover { color: #00d2ff; }
        input[type="file"] { display: none; }
        .file-label { display: block; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 12px; cursor: pointer; text-align: center; transition: 0.3s; }
        .file-label:hover { background: rgba(255,255,255,0.1); }
        #fileName { color: #888; font-size: 13px; margin-top: 5px; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💳 پرداخت</h1>
        
        <div class="info">
            <p>🆔 شماره پیگیری: <strong>{{ payment_id }}</strong></p>
            <p>💰 مبلغ کل: <strong>{{ total|int|toLocaleString }} تومان</strong></p>
        </div>

        <div class="card-box">
            <h3 style="color:#ffd700;margin-bottom:10px;">🏦 اطلاعات کارت</h3>
            <p>شماره کارت: <strong>{{ card.number }}</strong></p>
            <p>به نام: <strong>{{ card.owner }}</strong></p>
            <p>بانک: <strong>{{ card.bank }}</strong></p>
        </div>

        <form action="/upload-receipt" method="POST" enctype="multipart/form-data">
            <input type="hidden" name="payment_id" value="{{ payment_id }}">
            
            <div class="upload-area">
                <p style="margin-bottom:10px;">📸 لطفاً عکس رسید پرداخت را آپلود کنید</p>
                <label class="file-label" for="receipt">
                    📁 انتخاب فایل
                </label>
                <input type="file" name="receipt" id="receipt" accept="image/*" required onchange="document.getElementById('fileName').textContent = this.files[0].name">
                <span id="fileName" style="color:#888;font-size:13px;display:block;margin-top:5px;">هیچ فایلی انتخاب نشده</span>
            </div>

            <button type="submit" class="btn btn-success">✅ ارسال رسید</button>
        </form>

        <a href="/" class="back">🏠 بازگشت به فروشگاه</a>
    </div>
</body>
</html>
"""

HTML_ADMIN_LOGIN = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head><meta charset="UTF-8"><title>👑 ورود ادمین</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Tahoma',Arial,sans-serif;background:#0a0a1a;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.box{background:rgba(255,255,255,0.05);padding:40px;border-radius:20px;backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,0.08);max-width:400px;width:100%}
h1{color:#00d2ff;text-align:center;margin-bottom:30px}
input{width:100%;padding:12px;margin:10px 0;border-radius:12px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;font-size:16px}
input:focus{outline:none;border-color:#00d2ff}
button{width:100%;padding:12px;background:linear-gradient(135deg,#00d2ff,#3a7bd5);color:#fff;border:none;border-radius:12px;font-size:18px;font-weight:700;cursor:pointer;margin-top:10px;transition:0.3s}
button:hover{opacity:0.85}
.back{display:block;text-align:center;color:#888;margin-top:15px;text-decoration:none}
.back:hover{color:#00d2ff}
</style>
</head>
<body>
<div class="box">
    <h1>👑 ورود ادمین</h1>
    <form action="/admin/login" method="POST">
        <input type="text" name="username" placeholder="نام کاربری" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <button type="submit">ورود</button>
    </form>
    <a href="/" class="back">🏠 بازگشت به فروشگاه</a>
</div>
</body>
</html>
"""

HTML_ADMIN_DASHBOARD = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head><meta charset="UTF-8"><title>👑 پنل ادمین</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Tahoma',Arial,sans-serif;background:#0a0a1a;padding:20px;color:#fff}
.container{max-width:1200px;margin:auto}
.header{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-bottom:30px}
.header h1{color:#00d2ff}
.header a{color:#fff;text-decoration:none;background:rgba(255,255,255,0.1);padding:10px 20px;border-radius:12px;transition:0.3s}
.header a:hover{background:rgba(255,255,255,0.2)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:15px;margin-bottom:30px}
.stat{background:rgba(255,255,255,0.05);padding:20px;border-radius:15px;text-align:center;border:1px solid rgba(255,255,255,0.05)}
.stat .num{font-size:28px;font-weight:700;color:#00d2ff}
.stat .label{color:#888;font-size:13px;margin-top:5px}
.section{background:rgba(255,255,255,0.05);padding:20px;border-radius:15px;margin-bottom:20px;border:1px solid rgba(255,255,255,0.05)}
.section h2{color:#00d2ff;font-size:18px;margin-bottom:15px}
.table{width:100%;border-collapse:collapse;font-size:14px}
.table th,.table td{padding:10px;text-align:right;border-bottom:1px solid rgba(255,255,255,0.05)}
.table th{color:#888;font-weight:400}
.badge{padding:3px 12px;border-radius:20px;font-size:12px}
.badge-pending{background:#ffa502;color:#fff}
.badge-approved{background:#2ed573;color:#fff}
.badge-rejected{background:#ff4757;color:#fff}
.badge-config_sent{background:#00d2ff;color:#fff}
.btn{background:rgba(255,255,255,0.1);color:#fff;padding:5px 15px;border-radius:10px;text-decoration:none;font-size:13px;transition:0.3s;border:none;cursor:pointer}
.btn:hover{background:rgba(255,255,255,0.2)}
.btn-success{background:#2ed573;color:#fff}
.btn-danger{background:#ff4757;color:#fff}
.btn-primary{background:#00d2ff;color:#fff}
.btn-warning{background:#ffa502;color:#fff}
.form-inline{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.form-inline input,.form-inline select{padding:8px 12px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff}
.form-inline input:focus{outline:none;border-color:#00d2ff}
.form-inline button{padding:8px 20px}
.receipt-img{max-width:100px;border-radius:10px;cursor:pointer;transition:0.3s}
.receipt-img:hover{transform:scale(1.1)}
@media (max-width:600px){.stats{grid-template-columns:1fr 1fr}}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>👑 پنل ادمین <span style="color:#ffd700;font-size:14px;">Sabzin VPN</span></h1>
        <div>
            <a href="/">🏠 فروشگاه</a>
            <a href="/admin/logout">🚪 خروج</a>
        </div>
    </div>

    <div class="stats">
        <div class="stat"><div class="num">{{ total_orders }}</div><div class="label">📦 سفارشات</div></div>
        <div class="stat"><div class="num">{{ total_products }}</div><div class="label">🛍 محصولات</div></div>
        <div class="stat"><div class="num">{{ total_users }}</div><div class="label">👥 کاربران</div></div>
        <div class="stat"><div class="num">{{ pending_payments }}</div><div class="label">⏳ رسیدهای در انتظار</div></div>
    </div>

    <div class="section">
        <h2>💳 تنظیم شماره کارت</h2>
        <form action="/admin/update-card" method="POST" class="form-inline">
            <input type="text" name="number" value="{{ card.number }}" placeholder="شماره کارت" required>
            <input type="text" name="owner" value="{{ card.owner }}" placeholder="صاحب حساب" required>
            <input type="text" name="bank" value="{{ card.bank }}" placeholder="نام بانک" required>
            <button type="submit" class="btn btn-primary">💾 ذخیره</button>
        </form>
    </div>

    <div class="section">
        <h2>➕ افزودن محصول جدید</h2>
        <form action="/admin/add-product" method="POST" class="form-inline">
            <input type="text" name="name" placeholder="نام محصول" required>
            <input type="number" name="price" placeholder="قیمت" required>
            <select name="type">
                <option value="volume">حجمی</option>
                <option value="unlimited">نامحدود</option>
            </select>
            <input type="number" name="value" placeholder="مقدار" required>
            <input type="number" name="stock" placeholder="موجودی" required>
            <input type="text" name="duration" placeholder="مدت (مثلاً ۱ ماه)" required>
            <button type="submit" class="btn btn-primary">➕ افزودن</button>
        </form>
    </div>

    <div class="section">
        <h2>🛍 محصولات</h2>
        <table class="table">
            <tr><th>نام</th><th>قیمت</th><th>موجودی</th><th>مدت</th><th>عملیات</th></tr>
            {% for p in products %}
            <tr>
                <td>{{ p.name }}</td>
                <td>{{ p.price|int|toLocaleString }} تومان</td>
                <td>{{ p.stock }}</td>
                <td>{{ p.duration }}</td>
                <td>
                    <form action="/admin/update-product/{{ p.id }}" method="POST" style="display:inline;">
                        <input type="text" name="name" value="{{ p.name }}" style="width:80px;padding:4px;border-radius:6px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;">
                        <input type="number" name="price" value="{{ p.price }}" style="width:70px;padding:4px;border-radius:6px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;">
                        <input type="number" name="stock" value="{{ p.stock }}" style="width:50px;padding:4px;border-radius:6px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;">
                        <button type="submit" class="btn" style="padding:4px 10px;">✏️</button>
                    </form>
                    <a href="/admin/delete-product/{{ p.id }}" class="btn btn-danger" style="padding:4px 10px;display:inline-block;" onclick="return confirm('حذف شود؟')">🗑</a>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="section">
        <h2>📸 رسیدهای پرداخت</h2>
        {% if payments %}
        <table class="table">
            <tr><th>#</th><th>کاربر</th><th>مبلغ</th><th>رسید</th><th>وضعیت</th><th>تاریخ</th><th>عملیات</th></tr>
            {% for p in payments %}
            <tr>
                <td>{{ p.id }}</td>
                <td>{{ p.user }}</td>
                <td>{{ p.amount|int|toLocaleString }} تومان</td>
                <td>
                    {% if p.receipt %}
                    <a href="/uploads/{{ p.receipt }}" target="_blank">
                        <img src="/uploads/{{ p.receipt }}" class="receipt-img" alt="رسید">
                    </a>
                    {% else %}
                    <span style="color:#888;">بدون رسید</span>
                    {% endif %}
                </td>
                <td>
                    <span class="badge badge-{{ p.status }}">
                        {% if p.status == 'pending' %}⏳ در انتظار{% elif p.status == 'approved' %}✅ تایید{% elif p.status == 'config_sent' %}📤 کانفیگ ارسال شد{% else %}❌ رد{% endif %}
                    </span>
                </td>
                <td>{{ p.date }}</td>
                <td>
                    {% if p.status == 'pending' and p.receipt %}
                    <a href="/admin/approve-payment/{{ p.id }}" class="btn btn-success" style="padding:4px 10px;">✅ تایید</a>
                    <a href="/admin/reject-payment/{{ p.id }}" class="btn btn-danger" style="padding:4px 10px;">❌ رد</a>
                    <form action="/admin/send-config/{{ p.id }}" method="POST" style="display:inline;">
                        <input type="text" name="config" placeholder="لینک اشتراک..." style="padding:4px;border-radius:6px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;width:150px;">
                        <button type="submit" class="btn btn-warning" style="padding:4px 10px;">📤 ارسال</button>
                    </form>
                    {% elif p.status == 'approved' %}
                    <form action="/admin/send-config/{{ p.id }}" method="POST" style="display:inline;">
                        <input type="text" name="config" placeholder="لینک اشتراک..." style="padding:4px;border-radius:6px;border:1px solid rgba(255,255,255,0.1);background:rgba(255,255,255,0.05);color:#fff;width:150px;">
                        <button type="submit" class="btn btn-warning" style="padding:4px 10px;">📤 ارسال</button>
                    </form>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p style="color:#666;">هیچ رسیدی وجود ندارد.</p>
        {% endif %}
    </div>
</div>
</body>
</html>
"""

HTML_MY_ORDERS = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📦 سفارشات من</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Vazirmatn', sans-serif; background: #0a0a1a; min-height: 100vh; padding: 20px; color: #fff; }
        .container { max-width: 800px; margin: auto; background: rgba(255,255,255,0.05); border-radius: 20px; padding: 30px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.08); }
        h1 { text-align: center; color: #00d2ff; margin-bottom: 20px; }
        .order { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; margin: 10px 0; border-right: 4px solid #00d2ff; }
        .order .id { color: #ffd700; font-weight: 700; }
        .order .status { display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 12px; }
        .order .status-pending { background: #ffa502; }
        .order .status-approved { background: #2ed573; }
        .order .status-rejected { background: #ff4757; }
        .order .status-config_sent { background: #00d2ff; }
        .order .config { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; margin-top: 10px; font-family: monospace; font-size: 13px; word-break: break-all; color: #00d2ff; }
        .get-config-btn { display: inline-block; background: #ffd700; color: #0a0a1a; padding: 8px 20px; border-radius: 10px; text-decoration: none; font-weight: 700; margin-top: 8px; transition: 0.3s; }
        .get-config-btn:hover { opacity: 0.85; transform: scale(1.02); }
        .empty { text-align: center; color: #666; padding: 40px 0; }
        .back { display: block; text-align: center; color: #888; margin-top: 20px; text-decoration: none; }
        .back:hover { color: #00d2ff; }
        .btn { display: inline-block; background: #00d2ff; color: #fff; padding: 10px 20px; border-radius: 12px; text-decoration: none; font-weight: 700; transition: 0.3s; }
        .btn:hover { opacity: 0.85; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📦 سفارشات من</h1>
        {% if orders %}
            {% for o in orders %}
            <div class="order">
                <p><span class="id">🆔 #{{ o.id }}</span> - {{ o.date }}</p>
                <p>💰 مبلغ: {{ o.amount|int|toLocaleString }} تومان</p>
                <p>
                    وضعیت: 
                    <span class="status status-{{ o.status }}">
                        {% if o.status == 'pending' %}⏳ در انتظار تایید{% elif o.status == 'approved' %}✅ تایید شده{% elif o.status == 'config_sent' %}📤 کانفیگ ارسال شد{% elif o.status == 'rejected' %}❌ رد شده{% endif %}
                    </span>
                </p>
                {% if o.status == 'config_sent' %}
                <div class="config">🔗 لینک اشتراک شما: <br>{{ o.config }}</div>
                <a href="/get-config/{{ o.id }}" class="get-config-btn">📥 دریافت مجدد کانفیگ</a>
                {% endif %}
            </div>
            {% endfor %}
        {% else %}
            <div class="empty">📦 شما هیچ سفارشی ندارید.</div>
        {% endif %}
        <div style="text-align:center;">
            <a href="/" class="btn">🏠 بازگشت به فروشگاه</a>
        </div>
    </div>
</body>
</html>
"""

HTML_GET_CONFIG = """
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📥 دریافت کانفیگ</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Vazirmatn', sans-serif; background: #0a0a1a; min-height: 100vh; padding: 20px; color: #fff; display: flex; align-items: center; justify-content: center; }
        .container { max-width: 600px; margin: auto; background: rgba(255,255,255,0.05); border-radius: 20px; padding: 30px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.08); }
        h1 { text-align: center; color: #ffd700; margin-bottom: 20px; }
        .config-box { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 15px; margin: 20px 0; border: 1px solid #00d2ff; }
        .config-box code { color: #00d2ff; font-size: 14px; word-break: break-all; white-space: pre-wrap; }
        .info { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; margin: 10px 0; }
        .info strong { color: #ffd700; }
        .btn { display: inline-block; background: #00d2ff; color: #fff; padding: 12px 30px; border-radius: 12px; text-decoration: none; font-weight: 700; transition: 0.3s; margin-top: 10px; }
        .btn:hover { opacity: 0.85; transform: scale(1.02); }
        .btn-secondary { background: rgba(255,255,255,0.1); }
        .copy-btn { background: #2ed573; }
        .actions { text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📥 دریافت کانفیگ</h1>
        
        <div class="info">
            <p>🆔 شماره سفارش: <strong>#{{ payment.id }}</strong></p>
            <p>💰 مبلغ: <strong>{{ payment.amount|int|toLocaleString }} تومان</strong></p>
            <p>📅 تاریخ: <strong>{{ payment.date }}</strong></p>
        </div>

        <div class="config-box">
            <h3 style="color:#00d2ff;margin-bottom:10px;">🔗 لینک اشتراک شما:</h3>
            <code>{{ payment.config }}</code>
        </div>

        <div class="actions">
            <button class="btn copy-btn" onclick="copyConfig()">📋 کپی لینک</button>
            <a href="/my-orders" class="btn btn-secondary">📦 بازگشت به سفارشات</a>
            <a href="/" class="btn">🏠 فروشگاه</a>
        </div>
    </div>

    <script>
        function copyConfig() {
            const config = document.querySelector('.config-box code').textContent;
            navigator.clipboard.writeText(config).then(() => {
                alert('✅ لینک اشتراک کپی شد!');
            }).catch(() => {
                alert('❌ خطا در کپی کردن!');
            });
        }
    </script>
</body>
</html>
"""

# ========== مسیر برای نمایش رسید ==========
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

# ========== فیلترهای Jinja2 ==========
@app.template_filter('toLocaleString')
def to_locale_string(value):
    try:
        return f"{int(value):,}"
    except:
        return str(value)

@app.template_filter('int')
def to_int(value):
    try:
        return int(value)
    except:
        return 0

# ========== اجرا ==========
if __name__ == '__main__':
    print("=" * 50)
    print("🛒 Sabzin VPN Shop روشن شد!")
    print("📱 آدرس: http://127.0.0.1:5000")
    print("👑 پنل ادمین: http://127.0.0.1:5000/admin")
    print("🔑 نام کاربری: admin | رمز: 123456")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)