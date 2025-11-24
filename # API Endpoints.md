# API Endpoints
POST /api/analyze-contract
  Form Data: name, email, phone, address, egn + PDF file
  Response: contract_id, complaint_id, analysis, violations, financial_summary

GET /api/users/{id}/contracts - User's contract list
GET /api/contracts/{id} - Full contract details + analysis
GET /api/complaints/{id} - Complaint text
GET /api/complaints/{id}/export - Download PDF complaint

GET /api/legal/search?q=договор&limit=10 - Full-text search
GET /api/legal/article/{id} - Article details + tags
GET /api/legal/similar/{id}&top_k=5 - Semantic similarity search
GET /api/legal/documents - List all laws
GET /api/legal/stats - Database metrics