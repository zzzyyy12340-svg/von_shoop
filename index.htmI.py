<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌐 سایت مفید</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Tahoma', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { text-align: center; color: #764ba2; margin-bottom: 20px; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            border: 2px solid #e0e0e0;
            transition: all 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            border-color: #764ba2;
        }
        .card h3 { color: #333; margin-bottom: 10px; }
        .card p { color: #666; }
        input, select {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 10px;
            margin: 5px 0;
            font-size: 14px;
        }
        button {
            background: #764ba2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        button:hover { background: #5a3d7a; transform: scale(1.02); }
        .result-box {
            background: #e8f0fe;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-right: 4px solid #764ba2;
        }
        .result-box strong { color: #764ba2; }
        .date-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin: 15px 0;
        }
        .date-box h2 { font-size: 28px; }
        .date-box p { font-size: 18px; opacity: 0.9; }
        .flex { display: flex; gap: 10px; flex-wrap: wrap; }
        .flex input { flex: 1; }
        .flex button { flex: 0 0 auto; }
        .qr-img { max-width: 200px; margin: 10px auto; display: block; }
        @media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 سایت مفید</h1>
        
        <div class="date-box" id="dateBox">
            <h2 id="dateDisplay">بارگذاری...</h2>
            <p id="timeDisplay">⏳</p>
        </div>

        <div class="grid">
            <div class="card">
                <h3>🎲 تاس</h3>
                <p id="diceResult">0</p>
                <button onclick="rollDice()">تاس بنداز</button>
            </div>
            <div class="card">
                <h3>🎯 عدد شانس</h3>
                <p id="randomResult">0</p>
                <button onclick="getRandom()">بگیر</button>
            </div>
            <div class="card">
                <h3>🌤 آب و هوا</h3>
                <input type="text" id="cityInput" placeholder="نام شهر..." value="تهران">
                <button onclick="getWeather()">بررسی</button>
                <div id="weatherResult" class="result-box" style="display:none;"></div>
            </div>
            <div class="card">
                <h3>📱 QR Code</h3>
                <input type="text" id="qrInput" placeholder="متن..." value="https://google.com">
                <button onclick="generateQR()">ساخت</button>
                <div id="qrResult"></div>
            </div>
            <div class="card">
                <h3>🔗 کوتاه‌کننده</h3>
                <input type="text" id="urlInput" placeholder="لینک بلند...">
                <button onclick="shortenURL()">کوتاه کن</button>
                <div id="shortResult" class="result-box" style="display:none;"></div>
            </div>
            <div class="card">
                <h3>🔢 مبدل واحد</h3>
                <div class="flex">
                    <input type="number" id="valueInput" placeholder="عدد...">
                    <select id="fromUnit">
                        <option value="km">کیلومتر</option>
                        <option value="mile">مایل</option>
                        <option value="kg">کیلوگرم</option>
                        <option value="pound">پوند</option>
                        <option value="c">سانتی‌گراد</option>
                        <option value="f">فارنهایت</option>
                    </select>
                    <select id="toUnit">
                        <option value="mile">مایل</option>
                        <option value="km">کیلومتر</option>
                        <option value="pound">پوند</option>
                        <option value="kg">کیلوگرم</option>
                        <option value="f">فارنهایت</option>
                        <option value="c">سانتی‌گراد</option>
                    </select>
                </div>
                <button onclick="convertUnits()">تبدیل</button>
                <div id="convertResult" class="result-box" style="display:none;"></div>
            </div>
        </div>
    </div>

    <script>
        async function updateDate() {
            try {
                const response = await fetch('/date');
                const data = await response.json();
                document.getElementById('dateDisplay').textContent = data.date;
                document.getElementById('timeDisplay').textContent = '🕐 ' + data.time;
            } catch {
                document.getElementById('dateDisplay').textContent = 'خطا در دریافت تاریخ';
            }
        }
        updateDate();
        setInterval(updateDate, 1000);

        async function rollDice() {
            const response = await fetch('/dice');
            const data = await response.json();
            document.getElementById('diceResult').textContent = data.result;
        }

        async function getRandom() {
            const response = await fetch('/random');
            const data = await response.json();
            document.getElementById('randomResult').textContent = data.number;
        }

        async function getWeather() {
            const city = document.getElementById('cityInput').value;
            const response = await fetch(`/weather?city=${city}`);
            const data = await response.json();
            const resultBox = document.getElementById('weatherResult');
            if (data.error) {
                resultBox.style.display = 'block';
                resultBox.innerHTML = '<strong>❌</strong> ' + data.error;
            } else {
                resultBox.style.display = 'block';
                resultBox.innerHTML = `<strong>🌤 ${data.city}</strong><br>${data.condition}<br>🌡 ${data.temp}<br>💨 ${data.wind}`;
            }
        }

        async function generateQR() {
            const text = document.getElementById('qrInput').value;
            const response = await fetch(`/qr?text=${encodeURIComponent(text)}`);
            const data = await response.json();
            const resultBox = document.getElementById('qrResult');
            if (data.qr) {
                resultBox.innerHTML = `<img src="data:image/png;base64,${data.qr}" class="qr-img">`;
            } else {
                resultBox.innerHTML = '<strong>❌ خطا</strong>';
            }
        }

        async function shortenURL() {
            const url = document.getElementById('urlInput').value;
            if (!url) { alert('لطفاً لینک وارد کن!'); return; }
            const response = await fetch(`/shorten?url=${encodeURIComponent(url)}`);
            const data = await response.json();
            const resultBox = document.getElementById('shortResult');
            if (data.short) {
                resultBox.style.display = 'block';
                resultBox.innerHTML = `<strong>✅</strong> <a href="${data.short}" target="_blank">${data.short}</a>`;
            } else {
                resultBox.style.display = 'block';
                resultBox.innerHTML = '<strong>❌</strong> ' + data.error;
            }
        }

        async function convertUnits() {
            const value = document.getElementById('valueInput').value;
            const from = document.getElementById('fromUnit').value;
            const to = document.getElementById('toUnit').value;
            if (!value) { alert('لطفاً عدد وارد کن!'); return; }
            const response = await fetch(`/convert?value=${value}&from=${from}&to=${to}`);
            const data = await response.json();
            const resultBox = document.getElementById('convertResult');
            if (data.result !== undefined) {
                resultBox.style.display = 'block';
                resultBox.innerHTML = `<strong>🔢 نتیجه:</strong> ${data.result}`;
            } else {
                resultBox.style.display = 'block';
                resultBox.innerHTML = '<strong>❌</strong> تبدیل نامعتبر!';
            }
        }
    </script>
</body>
</html>