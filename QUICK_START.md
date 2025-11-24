# Quick Start - Observability & Evaluation

## Current Status

✅ **Tracing System**: OPERATIONAL (Core functionality)
✅ **Evaluation Framework**: READY
⚠️ **Full OpenTelemetry**: Partially installed (core features working)

## What's Working

### Tracing (Core Features)
- ✅ Basic trace spans
- ✅ Trace events
- ✅ Nested spans
- ✅ Console export
- ✅ Performance tracking
- ⚠️ OTLP export (requires additional package)
- ⚠️ OpenAI instrumentation (requires openai package)

### Evaluation Framework
- ✅ Dataset management
- ✅ Metrics calculation
- ✅ Agent runner
- ✅ Report generation
- ⚠️ Full agent testing (requires OpenAI API key)

## Installation

### Option 1: Install Everything (Recommended)
```powershell
# Activate your virtual environment first
cd c:\credit-guardian
.\.venv\Scripts\Activate.ps1

# Install all dependencies
pip install -r requirements.txt
```

### Option 2: Install Core Only (Current Status)
```powershell
# You already have:
- opentelemetry-api
- opentelemetry-sdk
- Basic tracing functionality

# To add full features:
pip install openai opentelemetry-exporter-otlp
```

## Quick Test

### Test Tracing
```powershell
python -c "from ai_agent.tracing import trace_span; import time; print('Testing...'); exec(\"with trace_span('test'): time.sleep(0.1)\"); print('✓ Tracing works!')"
```

### Test Evaluation Framework
```powershell
# Create sample dataset
python run_evaluation.py --create-sample

# View the dataset
python -c "import json; print(json.dumps(json.load(open('evaluation/test_dataset.json')), indent=2)[:500])"
```

## Usage Examples

### 1. Using Tracing in Your Code
```python
from ai_agent.tracing import trace_span, add_trace_event

# Wrap operations with trace spans
with trace_span('my_operation', attributes={'user_id': '123'}):
    # Your code here
    add_trace_event('processing_started')
    # ... do work ...
    add_trace_event('processing_completed')
```

### 2. Using the Evaluation Framework
```python
from evaluation.dataset import EvaluationDataset
from evaluation.metrics import EvaluationMetrics

# Create dataset
dataset = EvaluationDataset()
dataset.create_sample_dataset()
dataset.save_dataset('evaluation/test_dataset.json')

# Calculate metrics
accuracy = EvaluationMetrics.calculate_accuracy(
    predicted={'creditor': 'Bank A', 'principal': 5000},
    expected={'creditor': 'Bank A', 'principal': 5000}
)
print(f'Accuracy: {accuracy:.2%}')
```

## Next Steps

1. **Install Full Dependencies** (if not already done)
   ```powershell
   pip install openai opentelemetry-exporter-otlp
   ```

2. **Set OpenAI API Key** (for agent testing)
   ```powershell
   $env:OPENAI_API_KEY = "your-api-key-here"
   ```

3. **Create Test Dataset**
   ```powershell
   python run_evaluation.py --create-sample
   ```

4. **Run Demo**
   ```powershell
   python demo_features.py
   ```

5. **Run Full Evaluation** (with API key)
   ```powershell
   python run_evaluation.py --verbose
   ```

## Troubleshooting

### Issue: Unicode errors on Windows
✅ **Fixed** - All Unicode characters removed from output

### Issue: OpenTelemetry not detected
**Solution**: The tracing system now works with partial installations:
- Core features work with just `opentelemetry-api` and `opentelemetry-sdk`
- OTLP export requires `opentelemetry-exporter-otlp`
- OpenAI instrumentation requires `openai` package

### Issue: Venv creation failed
**Solution**: Dependencies have been corrected in `requirements.txt`:
- Changed `opentelemetry-instrumentation-openai==0.21.0` to `==0.1.5`
- Made OTLP and OpenAI packages optional in code

## Features Overview

### Observability (Tracing)
- Track AI agent operations
- Monitor LLM calls
- Measure performance
- Debug issues
- Export to monitoring platforms

### Evaluation Framework
- Test agent on datasets
- Calculate accuracy metrics
- Measure violation detection
- Generate reports
- Track performance over time

## Documentation

- **Full Guide**: `README_OBSERVABILITY.md`
- **Quick Reference**: `OBSERVABILITY_SUMMARY.md`
- **Implementation Details**: `IMPLEMENTATION_CHECKLIST.md`

## Current System Status

```
Tracing Components:
  ✅ OpenTelemetry Core (installed)
  ✅ Trace spans (working)
  ✅ Trace events (working)
  ✅ Console export (working)
  ⚠️  OTLP export (install opentelemetry-exporter-otlp)
  ⚠️  OpenAI instrumentation (install openai)

Evaluation Components:
  ✅ Dataset management (ready)
  ✅ Metrics calculation (ready)
  ✅ Agent runner (ready)
  ✅ Report generation (ready)
  ⚠️  Full testing (requires OpenAI API key)
```

## Support

The system is designed to degrade gracefully:
- ✅ Works with partial installations
- ✅ Falls back to in-memory tracing if needed
- ✅ Evaluation framework works independently
- ✅ No breaking errors if packages missing

To get full functionality, simply install the remaining packages:
```powershell
pip install openai opentelemetry-exporter-otlp
```

---

**Version**: 1.1  
**Status**: ✅ Core features operational  
**Last Updated**: 2025-11-24
