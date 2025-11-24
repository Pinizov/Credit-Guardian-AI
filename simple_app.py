"""Simplified Flask app for Credit Guardian - Works with Python 3.13"""
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import sqlite3
from pathlib import Path
import os

app = Flask(__name__)
CORS(app)

DB_PATH = Path(__file__).parent / "credit_guardian.db"


def get_db():
    return sqlite3.connect(str(DB_PATH))


@app.route('/')
def root():
    return jsonify({
        "service": "Credit Guardian API",
        "version": "1.0-simple",
        "endpoints": ["/health", "/stats", "/creditor/<name>", "/legal/search"]
    })


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "credit-guardian-api"})


@app.route('/stats')
def stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM legal_documents")
    docs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM legal_articles")
    articles = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM legal_article_tags")
    tags = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM article_embeddings")
    embeddings = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "documents": docs,
        "articles": articles,
        "tags": tags,
        "embeddings": embeddings
    })


@app.route('/creditor/<name>')
def creditor(name):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, type, violations_count, risk_score, is_blacklisted
        FROM creditors WHERE name LIKE ?
    """, (f"%{name}%",))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Creditor not found"}), 404
    
    cid, cname, ctype, violations, risk, blacklisted = row
    
    cursor.execute("""
        SELECT violation_type, decision_date, authority, penalty_amount, severity
        FROM violations WHERE creditor_id = ?
    """, (cid,))
    
    violations_list = [
        {
            "type": v[0],
            "date": v[1],
            "authority": v[2],
            "penalty": v[3],
            "severity": v[4]
        }
        for v in cursor.fetchall()
    ]
    
    conn.close()
    
    return jsonify({
        "name": cname,
        "type": ctype,
        "violations_count": violations,
        "risk_score": risk,
        "blacklisted": bool(blacklisted),
        "violations": violations_list
    })


@app.route('/legal/search')
def legal_search():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({"error": "Query parameter 'q' required"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Simple text search in articles
    cursor.execute("""
        SELECT la.id, la.article_number, la.content, ld.title
        FROM legal_articles la
        JOIN legal_documents ld ON la.document_id = ld.id
        WHERE la.content LIKE ? OR ld.title LIKE ?
        LIMIT ?
    """, (f"%{query}%", f"%{query}%", limit))
    
    results = [
        {
            "article_id": r[0],
            "article_number": r[1],
            "content": r[2][:200] + "..." if len(r[2]) > 200 else r[2],
            "document": r[3]
        }
        for r in cursor.fetchall()
    ]
    
    conn.close()
    
    return jsonify({
        "query": query,
        "results": results,
        "count": len(results)
    })


@app.route('/gpr/calculate', methods=['POST'])
def calculate_gpr():
    data = request.get_json()
    amount = data.get('amount', 0)
    total_repayment = data.get('total_repayment', 0)
    term_months = data.get('term_months', 1)
    
    # Simple APR calculation
    if amount == 0 or term_months == 0:
        return jsonify({"error": "Invalid parameters"}), 400
    
    interest = total_repayment - amount
    monthly_rate = (interest / amount) / term_months
    apr = monthly_rate * 12 * 100
    
    return jsonify({
        "amount": amount,
        "total_repayment": total_repayment,
        "term_months": term_months,
        "interest": interest,
        "apr": round(apr, 2)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Credit Guardian API on port {port}")
    print(f"Database: {DB_PATH}")
    print(f"Open: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
