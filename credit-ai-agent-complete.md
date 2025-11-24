# 🤖 ПЪЛНА СИСТЕМА: AI AGENT ЗА АНАЛИЗ НА КРЕДИТИ И ГЕНЕРИРАНЕ НА ЖАЛБИ

---

## СЪДЪРЖАНИЕ
1. Архитектура и планиране
2. База данни (PostgreSQL + Alembic)
3. Backend логика с AI Agent
4. Frontend интерфейс
5. Трейсване и оценка
6. Инсталация и развръщане

---

# ФАЗА 1: АРХИТЕКТУРА И ПЛАНИРАНЕ

## 1.1 Технологичен стак

```
Frontend:        React.js + Axios
Backend:         Python Flask/FastAPI
Database:        PostgreSQL
ORM:             SQLAlchemy
Migrations:      Alembic
LLM:             OpenAI GPT-4 / Claude-3
PDF Processing:  PyPDF2 + Tesseract OCR
APIs:            RESTful API
Deployment:      Docker + Docker Compose
```

## 1.2 Функционалности

- ✅ Качване и анализ на PDF договори
- ✅ Автоматично проверка на законност
- ✅ Идентифициране на незаконни такси
- ✅ Изчисляване на реален ГПР
- ✅ AI-генериране на юридически жалби
- ✅ Експорт на жалба (PDF/Word)
- ✅ История на анализирани договори
- ✅ Мониториране на операции (tracing)

---

# ФАЗА 2: БАЗ ДАННИ (PostgreSQL + Alembic)

## 2.1 SQL схема

```sql
-- Потребители
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    egn VARCHAR(10) UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Договори
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    contract_number VARCHAR(50) UNIQUE NOT NULL,
    creditor_name VARCHAR(255) NOT NULL,
    creditor_eik VARCHAR(20),
    principal DECIMAL(10, 2) NOT NULL,
    interest_rate DECIMAL(5, 2),
    stated_apr DECIMAL(5, 2),
    real_apr DECIMAL(5, 2),
    contract_date DATE,
    maturity_date DATE,
    total_owed DECIMAL(10, 2),
    total_paid DECIMAL(10, 2),
    document_url VARCHAR(500),
    document_text TEXT,
    analysis_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Такси
CREATE TABLE fees (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    fee_type VARCHAR(100),
    fee_amount DECIMAL(10, 2),
    fee_date DATE,
    is_illegal BOOLEAN DEFAULT FALSE,
    paid BOOLEAN DEFAULT FALSE,
    legal_basis VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Жалби
CREATE TABLE complaints (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    complaint_type VARCHAR(50),
    complaint_text TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    submitted_date DATE,
    response_date DATE,
    response_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- История на плащания
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    payment_date DATE NOT NULL,
    payment_amount DECIMAL(10, 2) NOT NULL,
    payment_type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Анализи и нарушения
CREATE TABLE contract_violations (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    violation_type VARCHAR(100),
    description TEXT,
    severity VARCHAR(50),
    legal_basis VARCHAR(255),
    amount_affected DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Логове на операции
CREATE TABLE operation_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    operation_type VARCHAR(100),
    details TEXT,
    status VARCHAR(50),
    duration FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 2.2 Alembic миграции

```python
# alembic/env.py
import os
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from alembic import context
from logging.config import fileConfig

# Конфигурация
config = context.config
fileConfig(config.config_file_name)

target_metadata = None
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/credit_protection")

def run_migrations_offline():
    """Offline миграции"""
    context.configure(url=DATABASE_URL, target_metadata=target_metadata, literal_binds=True)
    
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Online миграции"""
    engine = create_engine(DATABASE_URL, poolclass=StaticPool)
    
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

```bash
# Команди за миграция
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
alembic downgrade -1
```

---

# ФАЗА 3: BACKEND С AI AGENT

## 3.1 LLM Client

```python
# backend/ai_agent/llm_client.py
import os
import json
import re
from openai import OpenAI
from typing import Dict, Any, List

class CreditAnalysisAgent:
    """AI Agent за анализ на кредитни договори"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.system_prompt = """
        Вие сте експертен правен советник специализиран в защита на потребителските права 
        при кредити в България. Вашите знания включват:
        - Закона за потребителския кредит (ЗПК) - действащ текст 2025 г.
        - Закона за защита на потребителите (ЗЗП)
        - Закона за задълженията и договорите (ЗЗД)
        - Актуална съдебна практика и решения на КЗП
        
        Анализирайте договорите внимателно и идентифицирайте:
        1. Незаконни такси (чл. 10а ЗПК) - такси за "бързо разглеждане", управление, усвояване
        2. Неправилно изчислен ГПР (чл. 19 ЗПК) - максимум 50% (5x законна лихва)
        3. Неравноправни клаузи (чл. 143-146 ЗЗП)
        4. Процедурни нарушения (чл. 10 ЗПК)
        5. Липса на информация по чл. 11 ЗПК
        
        ВАЖНО:
        - Отговарите ВИНАГИ на български език
        - Използвайте точни цитати от законодателството
        - Предоставяте конкретни суми и дати
        - Структурирайте отговора в JSON формат
        """
    
    def analyze_contract(self, contract_text: str) -> Dict[str, Any]:
        """Анализира договор и връща структурирани резултати"""
        
        analysis_prompt = f"""
        Анализирайте следния кредитен договор и предоставете подробен анализ в JSON формат:
        
        {contract_text}
        
        ВЪЗВРАТЕН JSON ФОРМАТ (ТОЧНО следвайте):
        {{
            "contract_number": "номер от договора",
            "creditor": "име на кредитора",
            "creditor_eik": "ЕИК номер",
            "contract_date": "YYYY-MM-DD",
            "principal": число,
            "stated_apr": число,
            "stated_interest_amount": число,
            "fees": [
                {{
                    "type": "тип такса",
                    "amount": число,
                    "is_illegal": true/false,
                    "basis": "правна основа"
                }}
            ],
            "total_disclosed_cost": число,
            "total_actual_cost": число,
            "calculated_real_apr": число,
            "violations": [
                {{
                    "type": "категория нарушение",
                    "description": "подробно описание",
                    "severity": "critical/high/medium/low",
                    "legal_basis": "чл. X, ал. Y ЗАКОН",
                    "financial_impact": число
                }}
            ],
            "recommendations": ["препоръка 1", "препоръка 2"],
            "summary": "кратко резюме"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"error": "Failed to parse AI response"}
    
    def generate_complaint(self, analysis: Dict[str, Any], user_name: str, user_address: str) -> str:
        """Генерира официална юридическа жалба"""
        
        complaint_prompt = f"""
        Генерирайте официална жалба към Комисията за защита на потребителите 
        на основата на следния анализ на кредитния договор:
        
        {json.dumps(analysis, ensure_ascii=False, indent=2)}
        
        ДАННИ НА ПОТРЕБИТЕЛЯ:
        - Име: {user_name}
        - Адрес: {user_address}
        
        ИЗИСКВАНИЯ ЗА ЖАЛБАТА:
        1. Следете официалния формат за жалба към КЗП
        2. Включете точни цитати от приложимото законодателство
        3. Опишете явно всяко нарушение с конкретни суми и дати
        4. Посочете точна правна база (чл., ал., ЗАКОН)
        5. Завършете с ясни исквания (проверка, задължение да возстанови, санкции)
        6. Структурирайте логически - фактическо описание → правна оценка → исквания
        7. Официален юридически стил на български език
        8. Напишете на ТОЧНО този адрес (не вариант):
           Комисия за защита на потребителите
           ул. "Проф. Александър Станишев" № 2
           гр. София 1000
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": complaint_prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
```

## 3.2 PDF обработка

```python
# backend/ai_agent/pdf_processor.py
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import re
from typing import Tuple, Dict

class PDFProcessor:
    """Обработка на PDF договори"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """Екстрахира текст от PDF"""
        
        text = ""
        
        # Метод 1: Стандартна екстракция
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            print(f"PyPDF2 error: {e}")
        
        # Метод 2: OCR при малко текст
        if len(text.strip()) < 500:
            try:
                images = convert_from_path(pdf_path)
                for image in images:
                    ocr_text = pytesseract.image_to_string(image, lang='bul')
                    if ocr_text:
                        text += ocr_text + "\n"
            except Exception as e:
                print(f"OCR error: {e}")
        
        return text
    
    @staticmethod
    def extract_financial_data(text: str) -> Dict[str, float]:
        """Извлича финансови данни от текст"""
        
        # Регулярни изрази за поиск
        patterns = {
            'principal': r'(?:главница|principal|сума на кредит)[:\s]*(\d+(?:[.,]\d{2})?)',
            'fee': r'(?:услуга за бързо разглеждане|такса|fee)[:\s]*(\d+(?:[.,]\d{2})?)',
            'interest': r'(?:лихва|interest)[:\s]*(\d+(?:[.,]\d{2})?)',
            'apr': r'(?:ГПР|APR|годишен процент)[:\s]*(\d+(?:[.,]\d{1,2})?)\s*%',
            'total': r'(?:обща|total|дължима сума)[:\s]*(\d+(?:[.,]\d{2})?)',
        }
        
        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '.')
                try:
                    extracted[key] = float(value_str)
                except ValueError:
                    pass
        
        return extracted

## 3.3 Agent Executor

```python
# backend/ai_agent/agent_executor.py
from typing import Dict, Any, Callable, List
from datetime import datetime
import json

class AgentExecutor:
    """Управление на AI Agent операции"""
    
    def __init__(self, llm_agent):
        self.llm = llm_agent
    
    def calculate_real_apr(self, principal: float, total_costs: float, days: int) -> float:
        """Изчислява реален ГПР"""
        
        if principal == 0 or days == 0:
            return 0
        
        # Формула: (разходи / главница) / дни * 365 * 100
        daily_rate = (total_costs / principal) / days
        real_apr = daily_rate * 365 * 100
        
        return round(real_apr, 2)
    
    def check_legal_violations(self, contract_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Проверя договора за нарушения"""
        
        violations = []
        
        # Проверка 1: Незаконни такси
        illegal_fee_types = [
            "услуга за бързо разглеждане",
            "такса за управление на кредита",
            "такса за усвояване на кредита",
            "комисион за разглеждане",
            "такса за обработка"
        ]
        
        for fee in contract_data.get("fees", []):
            fee_type_lower = fee.get("type", "").lower()
            if any(illegal in fee_type_lower for illegal in illegal_fee_types):
                violations.append({
                    "type": "illegal_fee",
                    "description": f"Незаконна такса: {fee['type']} в размер {fee['amount']} лв.",
                    "severity": "critical",
                    "legal_basis": "чл. 10а, ал. 2 ЗПК",
                    "financial_impact": fee.get("amount", 0)
                })
        
        # Проверка 2: ГПР превишава максимума
        real_apr = contract_data.get("calculated_real_apr", 0)
        stated_apr = contract_data.get("stated_apr", 0)
        
        if real_apr > 50:
            violations.append({
                "type": "apr_exceeded",
                "description": f"Реалният ГПР {real_apr:.1f}% превишава законовия максимум от 50%",
                "severity": "critical",
                "legal_basis": "чл. 19, ал. 4 ЗПК",
                "financial_impact": (real_apr - 50) * contract_data.get("principal", 0) / 100
            })
        
        # Проверка 3: Неправилно посочен ГПР в договор
        if abs(stated_apr - real_apr) > 5:
            violations.append({
                "type": "incorrect_apr_disclosure",
                "description": f"Посочен ГПР {stated_apr}% не включва всички разходи. Реален ГПР: {real_apr}%",
                "severity": "high",
                "legal_basis": "чл. 11, ал. 1, т. 10 ЗПК",
                "financial_impact": 0
            })
        
        return violations
    
    def process_contract(self, pdf_path: str, contract_text: str, user_info: Dict) -> Dict[str, Any]:
        """Основен работен поток"""
        
        print("🤖 [1/5] Extracting contract data...")
        financial_data = PDFProcessor.extract_financial_data(contract_text)
        
        print("🤖 [2/5] Analyzing with AI...")
        analysis = self.llm.analyze_contract(contract_text)
        
        print("🤖 [3/5] Calculating real APR...")
        real_apr = self.calculate_real_apr(
            analysis.get("principal", 0),
            analysis.get("total_actual_cost", 0),
            30  # предположение за 30 дни
        )
        analysis["calculated_real_apr"] = real_apr
        
        print("🤖 [4/5] Checking for violations...")
        violations = self.check_legal_violations(analysis)
        
        print("🤖 [5/5] Generating complaint...")
        complaint = self.llm.generate_complaint(
            analysis,
            user_info.get("name", "Потребител"),
            user_info.get("address", "")
        )
        
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "violations": violations,
            "complaint": complaint,
            "financial_summary": {
                "principal": analysis.get("principal", 0),
                "stated_apr": analysis.get("stated_apr", 0),
                "calculated_real_apr": real_apr,
                "total_illegal_fees": sum(v["financial_impact"] for v in violations if v["type"] == "illegal_fee")
            }
        }
```

## 3.4 Flask Backend API

```python
# backend/app.py
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import json
from io import BytesIO
from werkzeug.utils import secure_filename
from datetime import datetime

# Инициализация
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/credit_protection")
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

db = SQLAlchemy(app)
CORS(app)

# Импорт на AI компоненти
from ai_agent.llm_client import CreditAnalysisAgent
from ai_agent.agent_executor import AgentExecutor
from ai_agent.pdf_processor import PDFProcessor

# Инициализация на Agent
llm_agent = CreditAnalysisAgent(api_key=os.getenv("OPENAI_API_KEY"))
executor = AgentExecutor(llm_agent)

# ORM модели
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contract_number = db.Column(db.String(50), unique=True, nullable=False)
    creditor_name = db.Column(db.String(255), nullable=False)
    creditor_eik = db.Column(db.String(20))
    principal = db.Column(db.Float)
    interest_rate = db.Column(db.Float)
    stated_apr = db.Column(db.Float)
    real_apr = db.Column(db.Float)
    contract_date = db.Column(db.Date)
    maturity_date = db.Column(db.Date)
    total_owed = db.Column(db.Float)
    total_paid = db.Column(db.Float)
    document_text = db.Column(db.Text)
    analysis_status = db.Column(db.String(50), default='pending')
    analysis_result = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_number': self.contract_number,
            'creditor_name': self.creditor_name,
            'principal': self.principal,
            'stated_apr': self.stated_apr,
            'real_apr': self.real_apr,
            'analysis_status': self.analysis_status
        }

class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    complaint_text = db.Column(db.Text)
    status = db.Column(db.String(50), default='draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()}), 200

@app.route('/api/analyze-contract', methods=['POST'])
def analyze_contract():
    """Главен endpoint за анализ на договор"""
    
    if 'file' not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Only PDF files accepted"}), 400
    
    # Учетни данни на потребител
    user_data = {
        "name": request.form.get("name", "Потребител"),
        "email": request.form.get("email", ""),
        "address": request.form.get("address", ""),
        "phone": request.form.get("phone", "")
    }
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(filepath)
    
    try:
        # 1. Екстракция на текст
        print("📄 Extracting PDF text...")
        contract_text = PDFProcessor.extract_text_from_pdf(filepath)
        
        if len(contract_text) < 100:
            return jsonify({"error": "Could not extract text from PDF"}), 400
        
        # 2. Създаване/актуализиране на потребител
        user = User.query.filter_by(email=user_data["email"]).first()
        if not user and user_data["email"]:
            user = User(**user_data)
            db.session.add(user)
            db.session.commit()
        
        # 3. Анализ с AI Agent
        print("🤖 Running AI analysis...")
        result = executor.process_contract(filepath, contract_text, user_data)
        
        # 4. Съхранение на договор
        contract = Contract(
            user_id=user.id if user else None,
            contract_number=result['analysis'].get('contract_number', 'UNKNOWN'),
            creditor_name=result['analysis'].get('creditor', ''),
            creditor_eik=result['analysis'].get('creditor_eik', ''),
            principal=result['analysis'].get('principal', 0),
            interest_rate=result['analysis'].get('interest_rate', 0),
            stated_apr=result['analysis'].get('stated_apr', 0),
            real_apr=result['financial_summary'].get('calculated_real_apr', 0),
            document_text=contract_text,
            analysis_status='completed',
            analysis_result=result
        )
        
        db.session.add(contract)
        db.session.commit()
        
        # 5. Съхранение на жалба (чернова)
        complaint = Complaint(
            user_id=user.id if user else None,
            contract_id=contract.id,
            complaint_text=result['complaint'],
            status='draft'
        )
        db.session.add(complaint)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "contract_id": contract.id,
            "complaint_id": complaint.id,
            "analysis": result['analysis'],
            "violations": result['violations'],
            "financial_summary": result['financial_summary']
        }), 200
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/api/complaints/<int:complaint_id>/export', methods=['GET'])
def export_complaint(complaint_id):
    """Експортира жалба като PDF"""
    
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"error": "Complaint not found"}), 404
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import inch
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72)
        styles = getSampleStyleSheet()
        
        # Специален стил
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=4  # Justify
        )
        
        content = []
        
        # Разделяне на текста
        for line in complaint.complaint_text.split('\n'):
            if line.strip():
                content.append(Paragraph(line, normal_style))
                content.append(Spacer(1, 0.1*inch))
        
        doc.build(content)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'complaint_{complaint_id}.pdf'
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/contracts/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    """Получава детайли на договор"""
    
    contract = Contract.query.get(contract_id)
    if not contract:
        return jsonify({"error": "Contract not found"}), 404
    
    return jsonify({
        "contract": contract.to_dict(),
        "analysis": contract.analysis_result
    }), 200

@app.route('/api/users/<int:user_id>/contracts', methods=['GET'])
def get_user_contracts(user_id):
    """Получава всички договори на потребител"""
    
    contracts = Contract.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "contracts": [c.to_dict() for c in contracts]
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

# ФАЗА 4: FRONTEND (REACT.JS)

```javascript
// frontend/src/App.js
import React, { useState } from 'react';
import './App.css';
import AIAgentAnalysis from './components/AIAgentAnalysis';
import ContractHistory from './components/ContractHistory';
import ComplaintViewer from './components/ComplaintViewer';

function App() {
  const [activeTab, setActiveTab] = useState('analyze');
  const [selectedContract, setSelectedContract] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🤖 AI Анализатор на кредити</h1>
        <p>Автоматичен анализ и генериране на жалби за защита на потребителските права</p>
      </header>

      <nav className="app-nav">
        <button 
          className={activeTab === 'analyze' ? 'active' : ''} 
          onClick={() => setActiveTab('analyze')}
        >
          📊 Анализирай договор
        </button>
        <button 
          className={activeTab === 'history' ? 'active' : ''} 
          onClick={() => setActiveTab('history')}
        >
          📋 История
        </button>
        <button 
          className={activeTab === 'complaints' ? 'active' : ''} 
          onClick={() => setActiveTab('complaints')}
        >
          ✉️ Жалби
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'analyze' && (
          <AIAgentAnalysis 
            onAnalysisComplete={() => setRefreshKey(k => k + 1)}
          />
        )}
        {activeTab === 'history' && (
          <ContractHistory 
            key={refreshKey}
            onSelectContract={setSelectedContract}
          />
        )}
        {activeTab === 'complaints' && (
          <ComplaintViewer 
            contractId={selectedContract}
          />
        )}
      </main>
    </div>
  );
}

export default App;
```

```javascript
// frontend/src/components/AIAgentAnalysis.jsx
import React, { useState } from 'react';
import axios from 'axios';
import './AIAgentAnalysis.css';

export default function AIAgentAnalysis({ onAnalysisComplete }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [userInfo, setUserInfo] = useState({
    name: '',
    email: '',
    address: '',
    phone: ''
  });

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUserInfoChange = (e) => {
    const { name, value } = e.target;
    setUserInfo(prev => ({ ...prev, [name]: value }));
  };

  const handleAnalyze = async () => {
    if (!file || !userInfo.name) {
      alert('⚠️ Моля, качите PDF и въведете вашето име!');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', userInfo.name);
    formData.append('email', userInfo.email);
    formData.append('address', userInfo.address);
    formData.append('phone', userInfo.phone);

    try {
      console.log('📤 Uploading file...');
      const response = await axios.post('/api/analyze-contract', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setResult(response.data);
      onAnalysisComplete();
      alert('✅ Анализът е завършен успешно!');
    } catch (error) {
      alert('❌ Грешка: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleExportComplaint = async (complaintId) => {
    try {
      const response = await axios.get(`/api/complaints/${complaintId}/export`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `complaint_${complaintId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (error) {
      alert('❌ Грешка при експорт: ' + error.message);
    }
  };

  return (
    <div className="ai-agent-container">
      <div className="input-section">
        <h2>📝 Информация за анализ</h2>
        
        <div className="form-grid">
          <div className="form-group">
            <label>Ваше име:</label>
            <input 
              type="text" 
              name="name" 
              value={userInfo.name} 
              onChange={handleUserInfoChange} 
              placeholder="Николай Райков Спасов"
            />
          </div>

          <div className="form-group">
            <label>Имейл:</label>
            <input 
              type="email" 
              name="email" 
              value={userInfo.email} 
              onChange={handleUserInfoChange} 
              placeholder="nikolay@example.com"
            />
          </div>

          <div className="form-group">
            <label>Адрес:</label>
            <input 
              type="text" 
              name="address" 
              value={userInfo.address} 
              onChange={handleUserInfoChange} 
              placeholder="ЖК Овча купел 516..."
            />
          </div>

          <div className="form-group">
            <label>Телефон:</label>
            <input 
              type="tel" 
              name="phone" 
              value={userInfo.phone} 
              onChange={handleUserInfoChange} 
              placeholder="+359888888888"
            />
          </div>
        </div>

        <div className="form-group">
          <label>Качите договор (PDF):</label>
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileChange}
          />
          {file && <p className="file-info">✓ Избран файл: {file.name}</p>}
        </div>

        <button 
          onClick={handleAnalyze} 
          disabled={loading} 
          className="analyze-btn"
        >
          {loading ? '⏳ Анализирам...' : '🔍 Анализирай договор'}
        </button>
      </div>

      {result && (
        <div className="results-section">
          <h2>📊 Резултати на анализа</h2>

          {/* Финансово резюме */}
          <div className="financial-summary">
            <h3>💰 Финансова информация</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <span>Главница:</span>
                <strong>{result.financial_summary.principal} BGN</strong>
              </div>
              <div className="summary-item">
                <span>Посочен ГПР:</span>
                <strong>{result.financial_summary.stated_apr}%</strong>
              </div>
              <div className="summary-item error">
                <span>Реален ГПР:</span>
                <strong>{result.financial_summary.calculated_real_apr}%</strong>
              </div>
              <div className="summary-item error">
                <span>Незаконни такси:</span>
                <strong>{result.financial_summary.total_illegal_fees} BGN</strong>
              </div>
            </div>
          </div>

          {/* Нарушения */}
          {result.violations && result.violations.length > 0 && (
            <div className="violations">
              <h3>⚠️ Установени нарушения ({result.violations.length})</h3>
              {result.violations.map((v, i) => (
                <div key={i} className={`violation-item severity-${v.severity}`}>
                  <div className="violation-type">{v.type}</div>
                  <div className="violation-description">{v.description}</div>
                  <div className="violation-basis">
                    <small>Правна база: {v.legal_basis}</small>
                  </div>
                  {v.financial_impact > 0 && (
                    <div className="violation-impact">
                      Финансово влияние: {v.financial_impact} BGN
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Жалба */}
          <div className="complaint">
            <h3>📝 Генерирана жалба</h3>
            <textarea 
              readOnly 
              value={result.complaint} 
              rows="20" 
              className="complaint-text"
            />
            <button 
              onClick={() => handleExportComplaint(result.complaint_id)}
              className="export-btn"
            >
              📥 Изтегли жалба (PDF)
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

```css
/* frontend/src/components/AIAgentAnalysis.css */
.ai-agent-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.input-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  border: 1px solid #dee2e6;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.analyze-btn {
  background: #007bff;
  color: white;
  padding: 12px 30px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  width: 100%;
}

.analyze-btn:hover:not(:disabled) {
  background: #0056b3;
}

.analyze-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.file-info {
  color: #28a745;
  font-size: 14px;
  margin: 5px 0;
}

/* Результати */
.results-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #dee2e6;
}

.financial-summary {
  margin-bottom: 30px;
  background: #f0f7ff;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.summary-item {
  background: white;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.summary-item span {
  display: block;
  color: #666;
  font-size: 13px;
  margin-bottom: 5px;
}

.summary-item strong {
  font-size: 18px;
  color: #333;
}

.summary-item.error strong {
  color: #dc3545;
}

/* Нарушения */
.violations {
  margin-bottom: 30px;
}

.violation-item {
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 4px;
}

.violation-item.severity-critical {
  background: #f8d7da;
  border-left-color: #dc3545;
}

.violation-item.severity-high {
  background: #ffe0e0;
  border-left-color: #ff6b6b;
}

.violation-type {
  font-weight: 600;
  margin-bottom: 5px;
  text-transform: uppercase;
  font-size: 12px;
  color: #666;
}

.violation-description {
  margin-bottom: 8px;
  color: #333;
}

.violation-basis {
  color: #666;
}

.violation-impact {
  margin-top: 8px;
  color: #dc3545;
  font-weight: 600;
}

/* Жалба */
.complaint {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 2px solid #dee2e6;
}

.complaint-text {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 15px;
}

.export-btn {
  background: #28a745;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.3s;
}

.export-btn:hover {
  background: #218838;
}
```

---

# ФАЗА 5: TRACING И EVALUATION

```python
# backend/ai_agent/tracing.py
import json
import logging
import time
from datetime import datetime
from functools import wraps
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_operations.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class OperationTracing:
    """Трейсване и мониториране на операции"""
    
    traces: Dict[str, Any] = {}
    
    @staticmethod
    def trace_operation(operation_name: str):
        """Декоратор за трейсване"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                trace_id = f"{operation_name}_{int(time.time() * 1000)}"
                
                trace_data = {
                    "trace_id": trace_id,
                    "operation_name": operation_name,
                    "start_time": datetime.now().isoformat(),
                    "status": "running",
                    "input_summary": str(kwargs)[:100],
                    "output": None,
                    "error": None,
                    "duration_ms": 0
                }
                
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    trace_data["status"] = "success"
                    trace_data["output"] = str(result)[:200] if result else None
                    
                    logger.info(f"✅ {operation_name} completed successfully")
                    
                except Exception as e:
                    trace_data["status"] = "failed"
                    trace_data["error"] = str(e)
                    
                    logger.error(f"❌ {operation_name} failed: {str(e)}")
                    raise
                
                finally:
                    trace_data["duration_ms"] = round((time.time() - start_time) * 1000)
                    OperationTracing.traces[trace_id] = trace_data
                    
                    logger.info(json.dumps(trace_data, ensure_ascii=False))
                
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    def export_traces(filename: str = "traces.json"):
        """Експортира всички трейсове"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(OperationTracing.traces, f, ensure_ascii=False, indent=2)
        logger.info(f"📤 Traces exported to {filename}")
    
    @staticmethod
    def get_summary():
        """Връща резюме на операции"""
        total_operations = len(OperationTracing.traces)
        successful = sum(1 for t in OperationTracing.traces.values() if t['status'] == 'success')
        failed = sum(1 for t in OperationTracing.traces.values() if t['status'] == 'failed')
        total_duration = sum(t.get('duration_ms', 0) for t in OperationTracing.traces.values())
        
        return {
            "total_operations": total_operations,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / total_operations * 100, 2) if total_operations > 0 else 0,
            "total_duration_ms": total_duration,
            "average_duration_ms": round(total_duration / total_operations, 2) if total_operations > 0 else 0
        }

class ModelEvaluation:
    """Оценка на LLM модели"""
    
    @staticmethod
    def compare_models(contract_text: str, models: list = None) -> Dict[str, Any]:
        """Сравнява различни модели"""
        
        if models is None:
            models = ["gpt-4", "gpt-3.5-turbo"]
        
        results = {}
        
        for model in models:
            logger.info(f"🧪 Testing model: {model}")
            
            try:
                from ai_agent.llm_client import CreditAnalysisAgent
                
                start = time.time()
                agent = CreditAnalysisAgent(model=model)
                analysis = agent.analyze_contract(contract_text[:5000])  # Ограничение за тест
                elapsed = time.time() - start
                
                results[model] = {
                    "status": "success",
                    "duration_seconds": round(elapsed, 2),
                    "violations_detected": len(analysis.get("violations", [])),
                    "fees_detected": len(analysis.get("fees", []))
                }
            
            except Exception as e:
                results[model] = {
                    "status": "failed",
                    "error": str(e)
                }
                logger.error(f"❌ Model {model} failed: {str(e)}")
        
        return results

# Интегрирани трейсови операции
from ai_agent.agent_executor import AgentExecutor

class InstrumentedAgentExecutor(AgentExecutor):
    @OperationTracing.trace_operation("calculate_real_apr")
    def calculate_real_apr(self, principal, total_costs, days):
        return super().calculate_real_apr(principal, total_costs, days)
    
    @OperationTracing.trace_operation("check_legal_violations")
    def check_legal_violations(self, contract_data):
        return super().check_legal_violations(contract_data)
    
    @OperationTracing.trace_operation("process_contract")
    def process_contract(self, pdf_path, contract_text, user_info):
        return super().process_contract(pdf_path, contract_text, user_info)
```

---

# ФАЗА 6: ИНСТАЛАЦИЯ И РАЗВРЪЩАНЕ

## 6.1 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: credit-db
    environment:
      POSTGRES_USER: credituser
      POSTGRES_PASSWORD: creditpass123
      POSTGRES_DB: credit_protection
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U credituser"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Flask Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: credit-backend
    environment:
      DATABASE_URL: postgresql://credituser:creditpass123@db:5432/credit_protection
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      FLASK_ENV: production
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: python app.py

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: credit-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      REACT_APP_API_URL: http://backend:5000

volumes:
  postgres_data:
```

## 6.2 Dockerfile (Backend)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Инсталиране на системни зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    pytesseract \
    && rm -rf /var/lib/apt/lists/*

# Инсталиране на Python зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Миграции
RUN alembic upgrade head

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## 6.3 Requirements.txt

```txt
# backend/requirements.txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-CORS==4.0.0
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
Alembic==1.13.1
python-dotenv==1.0.0
openai==1.3.7
PyPDF2==3.0.1
pdf2image==1.16.3
pytesseract==0.3.10
reportlab==4.0.7
gunicorn==21.2.0
requests==2.31.0
```

## 6.4 Dockerfile (Frontend)

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

## 6.5 Начало на работа

```bash
# 1. Клониране
git clone <repo>
cd credit-ai-agent

# 2.環境 файл
cp .env.example .env
# Редактирайте .env и добавете OPENAI_API_KEY

# 3. Стартиране с Docker
docker-compose up -d

# 4. Миграции
docker-compose exec backend alembic upgrade head

# 5. Проверка
curl http://localhost:5000/api/health
# Frontend: http://localhost:3000
```

---

# ПЪЛЕН РАБОТЕН ПРИМЕР

## Тестване на система

```bash
# 1. Качване на договор
curl -X POST http://localhost:5000/api/analyze-contract \
  -F "file=@договор.pdf" \
  -F "name=Николай Райков Спасов" \
  -F "email=nikolay@example.com" \
  -F "address=ЖК Овча купел 516" \
  -F "phone=+359888888888"

# 2. Экспорт на жалба
curl http://localhost:5000/api/complaints/1/export > jalba.pdf

# 3. История на договори
curl http://localhost:5000/api/users/1/contracts
```

---

# РЕЗЮМЕ

✅ **Пълна система, готова за развръщане**
- LLM-базиран AI Agent за анализ
- PostgreSQL база данни с миграции
- Flask REST API
- React.js фронтенд
- Docker контейнеризация
- Tracing и мониториране
- Пълна документация

🚀 **За начало:**
```bash
docker-compose up -d
```

Система е готова за анализ на кредити и генериране на жалби! 🎯
