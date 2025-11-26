# API Integration Guide - Bulgarian Financial Registers

## Overview

Credit Guardian now includes comprehensive integration with Bulgarian financial registers and APIs for real-time creditor data synchronization.

## Features

✅ **Multi-source Data Integration**
- BNB (Bulgarian National Bank) banks register
- FSC (Financial Supervision Commission) non-bank institutions
- Trade Register (registryagency.bg)
- APIS.bg consumer protection data
- Local register files (XLS, XLSX, DOC, DOCX)

✅ **Optimized Data Format**
- Standardized creditor records
- Automatic deduplication by BULSTAT
- Batch processing for performance
- Indexed database queries

✅ **Real-time Synchronization**
- REST API endpoint for on-demand sync
- Frontend sync button
- Automatic data enrichment with violations

✅ **Advanced Frontend Features**
- Pagination (50 records per page)
- Search by name or BULSTAT
- Filter by creditor type
- Sort by risk score, name, or violations
- Real-time sync from APIs

## Usage

### 1. Import Creditors from Local Files

```bash
python import_creditors_from_apis.py
```

This script will:
- Parse all register files in `legal data/` folder
- Extract creditors from:
  - `bs_ci_reg_bankslist_bg.doc` (BNB banks list)
  - `bs_fi_regintro_register_bg.xls` (FSC non-bank institutions)
  - Other register files (XLS, XLSX)
- Standardize and deduplicate data
- Enrich with violation data from APIS.bg
- Import to database with batch processing

### 2. Sync from APIs (Real-time)

**Via API Endpoint:**
```bash
POST /api/creditors/sync
```

**Via Frontend:**
- Click "🔄 Синхронизирай от API" button in CreditorList component
- System will fetch latest data from online sources

### 3. Query Creditors with Filters

**API Endpoint:**
```
GET /api/creditors?limit=50&offset=0&search=bank&creditor_type=bank&min_risk_score=5.0&sort_by=risk_score
```

**Parameters:**
- `limit`: Number of records per page (default: 50)
- `offset`: Pagination offset (default: 0)
- `search`: Search by name or BULSTAT
- `creditor_type`: Filter by type (bank, non-bank, unknown)
- `min_risk_score`: Minimum risk score filter
- `blacklisted_only`: Show only blacklisted creditors
- `sort_by`: Sort field (risk_score, name, violations_count)

**Response:**
```json
{
  "total": 150,
  "count": 50,
  "offset": 0,
  "limit": 50,
  "creditors": [
    {
      "id": 1,
      "name": "Банка Пример АД",
      "type": "bank",
      "bulstat": "123456789",
      "risk_score": 7.5,
      "violations_count": 3,
      "blacklisted": false,
      "license_number": "LIC-12345"
    }
  ]
}
```

## Data Sources

### 1. BNB Banks Register
- **Source**: https://www.bnb.bg
- **Type**: Banks
- **Update Frequency**: Monthly
- **Format**: HTML tables or downloadable files

### 2. FSC Non-Bank Institutions
- **Source**: https://www.fsc.bg
- **Type**: Non-bank financial institutions
- **Update Frequency**: Monthly
- **Format**: HTML tables

### 3. Trade Register
- **Source**: https://registryagency.bg
- **Type**: Company metadata
- **Update Frequency**: Real-time
- **Format**: REST API (may require authentication)

### 4. APIS.bg
- **Source**: https://www.apis.bg
- **Type**: Violations and blacklist
- **Update Frequency**: Weekly
- **Format**: HTML scraping

### 5. Local Register Files
- **Location**: `legal data/` folder
- **Supported Formats**: XLS, XLSX, DOC, DOCX
- **Files**:
  - `bs_ci_reg_bankslist_bg.doc` - BNB banks list
  - `bs_fi_regintro_register_bg.xls` - FSC non-bank register
  - `bs_ci_register_bg.xls` - Additional registers
  - `rs_lcbregisters_*.xlsx` - Licensed credit brokers
  - `rs_csrcreditservregister_bg.xlsx` - Credit service providers

## Data Standardization

All creditor records are standardized to this format:

```python
{
    'name': str,                    # Company name (required)
    'type': str,                    # 'bank', 'non-bank', or 'unknown'
    'bulstat': str,                 # BULSTAT/EIK number (9-13 digits)
    'license_number': str,          # License number if applicable
    'address': str,                 # Company address
    'violations_count': int,        # Number of violations (default: 0)
    'risk_score': float,            # Risk score 0-10 (default: 0.0)
    'is_blacklisted': bool,        # Blacklist status (default: False)
    'source': str,                  # Data source identifier
    'fetched_at': str,             # ISO timestamp
}
```

## Deduplication Logic

1. **Primary Key**: BULSTAT (if available)
   - Records with same BULSTAT are merged
   - Latest data takes precedence

2. **Secondary Key**: Normalized company name
   - Used when BULSTAT is missing
   - Case-insensitive matching

3. **Data Merging**:
   - Non-null values override null values
   - Multiple sources are combined

## Performance Optimization

### Database Indexes
- `ix_creditor_name` - Fast name searches
- `uq_creditor_bulstat` - Unique BULSTAT constraint
- Indexes on `type`, `risk_score`, `is_blacklisted`

### Batch Processing
- Default batch size: 100 records
- Commits after each batch
- Rollback on errors

### Query Optimization
- Pagination reduces memory usage
- Indexed columns for fast filtering
- Efficient sorting with database indexes

## Frontend Integration

### CreditorList Component

**Features:**
- ✅ Pagination (50 per page)
- ✅ Search by name or BULSTAT
- ✅ Filter by type
- ✅ Sort by risk score
- ✅ Real-time sync button
- ✅ Loading states
- ✅ Error handling

**Usage:**
```jsx
import CreditorList from './components/CreditorList';

<CreditorList />
```

## Error Handling

- **Network Errors**: Retry with exponential backoff
- **Parsing Errors**: Logged, skipped records
- **Database Errors**: Rollback batch, continue with next
- **API Rate Limits**: Automatic delay between requests

## Monitoring

Check import statistics:
```python
stats = {
    'total': 150,        # Total records processed
    'imported': 120,     # New records
    'updated': 30,       # Updated existing records
    'skipped': 0,        # Skipped (duplicates)
    'errors': 0          # Errors encountered
}
```

## Future Enhancements

- [ ] Scheduled automatic sync (cron job)
- [ ] Webhook notifications on updates
- [ ] API rate limit handling
- [ ] Caching layer for frequently accessed data
- [ ] Export to CSV/Excel
- [ ] Data validation rules
- [ ] Historical data tracking

## Troubleshooting

### Issue: No creditors imported
- Check file paths in `legal data/` folder
- Verify file formats are supported
- Check database connection

### Issue: API sync fails
- Verify network connectivity
- Check API endpoints are accessible
- Review rate limiting

### Issue: Slow queries
- Check database indexes exist
- Reduce page size
- Add more specific filters

## Support

For issues or questions:
1. Check logs in `backend.log`
2. Review error messages in API responses
3. Verify database schema is up to date

