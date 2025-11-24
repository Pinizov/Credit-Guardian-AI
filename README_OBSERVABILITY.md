# Observability & Evaluation Guide

This guide covers the enhanced observability (tracing) and comprehensive evaluation framework added to the Credit Guardian AI Agent.

## Table of Contents

1. [Observability with OpenTelemetry](#observability-with-opentelemetry)
2. [Evaluation Framework](#evaluation-framework)
3. [Setup Instructions](#setup-instructions)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)

---

## Observability with OpenTelemetry

### Overview

The AI agent now includes comprehensive tracing using OpenTelemetry, providing:

- **LLM Call Tracking**: Automatic instrumentation of OpenAI API calls
- **Performance Monitoring**: Execution time and resource usage tracking
- **Error Tracking**: Detailed error capture and stack traces
- **Distributed Tracing**: Full request flow visibility

### Features

#### Automatic LLM Instrumentation
```python
from ai_agent.tracing import initialize_tracing

# Initialize tracing (done automatically on import)
initialize_tracing(
    service_name="credit-guardian-ai-agent",
    console_export=True  # Print traces to console for debugging
)
```

#### Manual Span Creation
```python
from ai_agent.tracing import trace_span, add_trace_event

with trace_span("custom_operation", attributes={"key": "value"}):
    # Your code here
    add_trace_event("checkpoint", {"status": "processing"})
```

#### Decorator-Based Tracing
```python
from ai_agent.tracing import trace

@trace("my_operation", trace_llm=True)
def my_function():
    # Function automatically traced
    pass
```

### Trace Export Options

#### 1. Console Export (Default)
Traces are printed to console for local debugging.

#### 2. OTLP Collector
Export to OpenTelemetry Collector or compatible backend:

```bash
# Set environment variable
$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

# Or in code
initialize_tracing(otlp_endpoint="http://localhost:4317")
```

#### 3. Popular Observability Platforms

**Jaeger:**
```bash
# Run Jaeger all-in-one
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest

# View UI at http://localhost:16686
```

**Grafana Tempo:**
```bash
# Set endpoint
$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://tempo-endpoint:4317"
```

### Viewing Traces

Traces include:
- Operation name and duration
- LLM model and parameters
- Token usage
- Input/output sizes
- Error details
- Custom events

Example trace output:
```json
{
  "name": "llm.analyze_contract",
  "attributes": {
    "model": "gpt-4",
    "text_length": 5000,
    "operation": "contract_analysis",
    "tokens_used": 1234
  },
  "duration_ms": 2543,
  "status": "ok"
}
```

---

## Evaluation Framework

### Overview

Comprehensive evaluation framework for measuring AI agent performance across multiple dimensions:

- **Accuracy Metrics**: Contract field extraction accuracy
- **Violation Detection**: Precision, recall, and F1 scores
- **GPR Calculation**: APR accuracy assessment
- **Complaint Quality**: Legal document generation quality
- **Performance**: Execution time and success rates

### Components

#### 1. Dataset Management (`evaluation/dataset.py`)

Create and manage test datasets:

```python
from evaluation.dataset import EvaluationDataset

# Create new dataset
dataset = EvaluationDataset()

# Add test case
dataset.add_test_case(
    test_id="test_001",
    pdf_path="tests/fixtures/contract.pdf",
    user_data={"name": "Test User", "address": "Sofia"},
    expected_analysis={
        "creditor": "Test Bank",
        "principal": 5000.0,
        "stated_apr": 12.5
    },
    expected_violations=["Hidden fee", "Unclear terms"],
    description="Standard consumer loan"
)

# Save dataset
dataset.save_dataset("evaluation/test_dataset.json")
```

#### 2. Agent Runner (`evaluation/runner.py`)

Execute agent on test cases:

```python
from evaluation.runner import AgentRunner
from ai_agent.agent_executor import AgentExecutor

# Initialize
agent = AgentExecutor()
runner = AgentRunner(agent, max_workers=4)

# Run tests
results = runner.run_batch(
    test_cases=dataset.test_cases,
    parallel=True,
    verbose=True
)

# Save results
runner.save_results("evaluation/results.json")
```

#### 3. Metrics Calculation (`evaluation/metrics.py`)

Comprehensive metrics:

```python
from evaluation.metrics import EvaluationMetrics

# Calculate accuracy
accuracy = EvaluationMetrics.calculate_accuracy(
    predicted=agent_output,
    expected=ground_truth
)

# Violation detection metrics
recall = EvaluationMetrics.calculate_violation_recall(
    predicted_violations,
    expected_violations
)
precision = EvaluationMetrics.calculate_violation_precision(
    predicted_violations,
    expected_violations
)
f1 = EvaluationMetrics.calculate_f1_score(precision, recall)

# Generate report
report = EvaluationMetrics.generate_report(
    results,
    output_path="evaluation/report.txt"
)
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
# Install tracing and evaluation packages
pip install -r requirements.txt
```

### 2. Create Sample Dataset

```bash
# Generate sample test dataset
python run_evaluation.py --create-sample --dataset evaluation/test_dataset.json
```

This creates a sample dataset with 3 test cases. Edit the file to add your own test cases.

### 3. Prepare Test Fixtures

Create test PDF files in `tests/fixtures/`:
- `sample_contract_001.pdf` - Standard loan with violations
- `sample_contract_002.pdf` - Payday loan with excessive APR
- `sample_contract_003.pdf` - Clean contract with no violations

### 4. Configure Environment

```bash
# Set OpenAI API key (required for agent)
$env:OPENAI_API_KEY="your-api-key-here"

# Optional: Set OTLP endpoint for trace export
$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
```

---

## Usage Examples

### Running Full Evaluation

```bash
# Run evaluation with default settings
python run_evaluation.py

# Run with custom paths
python run_evaluation.py \
    --dataset evaluation/my_dataset.json \
    --output evaluation/my_results.json \
    --report evaluation/my_report.txt

# Run in parallel with verbose output
python run_evaluation.py --parallel --workers 8 --verbose
```

### Evaluating Specific Test Cases

```python
from evaluation.dataset import EvaluationDataset
from evaluation.runner import AgentRunner
from ai_agent.agent_executor import AgentExecutor

# Load dataset and filter
dataset = EvaluationDataset("evaluation/test_dataset.json")
specific_cases = dataset.get_test_cases(filter_ids=["test_001", "test_002"])

# Run only specific cases
agent = AgentExecutor()
runner = AgentRunner(agent)
results = runner.run_batch(specific_cases)
```

### Custom Metrics

```python
from evaluation.metrics import EvaluationMetrics

# Define custom metric
def custom_metric(predicted, expected):
    # Your custom logic here
    return score

# Use with evaluation
results = runner.run_batch(test_cases)
for result in results:
    custom_score = custom_metric(
        result["prediction"],
        result["expected"]
    )
    result["metrics"]["custom"] = custom_score
```

### Monitoring with Traces

```python
from ai_agent.tracing import trace_span, add_trace_event

# Wrap your code with tracing
with trace_span("evaluation_run", attributes={"dataset_size": len(test_cases)}):
    for test_case in test_cases:
        add_trace_event("test_case_start", {"id": test_case["id"]})
        result = agent.process(test_case["input"])
        add_trace_event("test_case_complete", {"success": True})
```

---

## Best Practices

### Tracing

1. **Use Meaningful Names**: Choose descriptive span names
   ```python
   # Good
   with trace_span("contract_analysis_step1"):
   
   # Bad
   with trace_span("step1"):
   ```

2. **Add Context**: Include relevant attributes
   ```python
   trace_span("operation", attributes={
       "user_id": user_id,
       "contract_type": contract_type,
       "model": model_name
   })
   ```

3. **Event Markers**: Use events for checkpoints
   ```python
   add_trace_event("pdf_parsed", {"pages": num_pages})
   add_trace_event("llm_request_sent", {"tokens": token_count})
   ```

4. **Error Handling**: Traces automatically capture exceptions
   ```python
   with trace_span("risky_operation"):
       # Exceptions are automatically recorded in trace
       risky_function()
   ```

### Evaluation

1. **Representative Dataset**: Include diverse test cases
   - Various contract types
   - Different violation scenarios
   - Edge cases and corner cases

2. **Ground Truth Quality**: Ensure expected outputs are accurate
   - Manually review expected values
   - Get domain expert validation
   - Document any ambiguities

3. **Regular Evaluation**: Run evaluations frequently
   - Before major releases
   - After model changes
   - When updating prompts

4. **Track Metrics Over Time**: Monitor trends
   ```python
   # Save timestamped results
   timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
   runner.save_results(f"evaluation/results_{timestamp}.json")
   ```

5. **Parallel Execution**: Use for large datasets
   ```bash
   # Faster evaluation with parallel processing
   python run_evaluation.py --parallel --workers 8
   ```

### Performance Optimization

1. **Batch Processing**: Process multiple cases efficiently
2. **Caching**: Cache LLM responses for repeated evaluations
3. **Sampling**: Use representative samples for quick checks
4. **Profiling**: Use traces to identify bottlenecks

---

## Troubleshooting

### Tracing Issues

**Problem**: No traces appearing
```bash
# Check OpenTelemetry installation
pip list | grep opentelemetry

# Verify initialization
python -c "from ai_agent.tracing import initialize_tracing; initialize_tracing()"
```

**Problem**: OTLP export failing
```bash
# Check endpoint connectivity
curl http://localhost:4317

# Try console export instead
# Set console_export=True in initialization
```

### Evaluation Issues

**Problem**: No test cases found
```bash
# Create sample dataset
python run_evaluation.py --create-sample

# Verify dataset format
python -c "import json; print(json.load(open('evaluation/test_dataset.json')))"
```

**Problem**: Agent errors during evaluation
```bash
# Run with verbose mode
python run_evaluation.py --verbose

# Check OPENAI_API_KEY is set
echo $env:OPENAI_API_KEY
```

---

## Next Steps

1. **Create Your Dataset**: Add real test cases from your domain
2. **Set Up Monitoring**: Configure trace export to your observability platform
3. **Establish Baselines**: Run initial evaluation to establish performance baselines
4. **Continuous Evaluation**: Integrate evaluation into your CI/CD pipeline
5. **Monitor Production**: Use tracing to monitor production agent performance

For more information, see the code documentation in:
- `ai_agent/tracing.py` - Tracing implementation
- `evaluation/metrics.py` - Metric definitions
- `evaluation/runner.py` - Runner implementation
- `evaluation/dataset.py` - Dataset management
