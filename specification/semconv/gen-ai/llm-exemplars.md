cat > specification/semconv/gen-ai/llm-exemplars.md << 'EOF'
---
status: non-normative
title: LLM Metrics Exemplars
---

# LLM Metrics Exemplars

**Status**: Non-normative (examples)

## Overview

Exemplars enable correlating `gen_ai.server.time_per_output_token` metric spikes to specific inference traces.

## vLLM Python Example

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.metrics import Exemplar

meter = metrics.get_meter("vllm")
latency = meter.create_histogram("gen_ai.server.time_per_output_token")

tracer = trace.get_tracer("vllm")

# Record latency WITH exemplar
with tracer.start_as_current_span("llm.inference") as span:
    result = llm.generate(prompt)  # vLLM call
    
    exemplar = Exemplar(
        value=result.time_per_token_ms,
        filtered_attributes={"gen_ai.provider.name": "vllm"},
        span_id=span.context.span_id,
        trace_id=span.context.trace_id
    )
    
    latency.record(
        result.time_per_token_ms,
        exemplars=[exemplar]
    )
