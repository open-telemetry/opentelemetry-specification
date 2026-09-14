# LLM Semantic Conventions for OpenTelemetry

**Author:** Open-source community  
**Date:** 2026-09-14  
**Status:** Proposal for standardization

## Overview

This document proposes standardized semantic conventions for telemetry data emitted by Large Language Model (LLM) applications and services. These conventions enable:

- **Cost tracking**: Attribution of LLM usage costs per request/user/service
- **Performance monitoring**: Latency, throughput, and efficiency metrics
- **Observability**: Trace correlation for multi-step LLM workflows (agents, RAG, etc.)
- **Compliance**: Audit trails for regulated industries using LLMs

## LLM Request Attributes

All LLM API calls SHOULD include:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `gen_ai.system` | string | LLM system/provider | "openai", "anthropic", "llama" |
| `gen_ai.request.model` | string | Model identifier | "gpt-4", "claude-3-opus" |
| `gen_ai.request.max_tokens` | int | Max completion tokens | 256 |
| `gen_ai.request.temperature` | double | Sampling temperature | 0.7 |
| `gen_ai.request.top_p` | double | Nucleus sampling parameter | 0.9 |

## LLM Usage Attributes

Track token consumption for cost attribution:

| Attribute | Type | Description |
|-----------|------|-------------|
| `gen_ai.usage.input_tokens` | int | Tokens in prompt |
| `gen_ai.usage.output_tokens` | int | Tokens in completion |
| `gen_ai.usage.cache_read_tokens` | int | Tokens read from cache |
| `gen_ai.usage.cache_creation_tokens` | int | Tokens written to cache |

## Cost Attribution

Enable financial tracking:

| Attribute | Type | Description | Example |
|-----------|------|-------------|---------|
| `gen_ai.cost.input_price_per_token` | double | Input token price | 0.000003 |
| `gen_ai.cost.output_price_per_token` | double | Output token price | 0.000006 |
| `gen_ai.cost.total_request_cost` | double | Total request cost | 0.00042 |
| `gen_ai.cost.currency` | string | Currency code | "USD" |

## Agent-Specific Attributes

For multi-step LLM workflows (agents, RAG, retrieval):

| Attribute | Type | Description |
|-----------|------|-------------|
| `agent.name` | string | Agent identifier |
| `agent.run.id` | string | Execution run ID |
| `agent.step.id` | string | Step within run |
| `agent.tool.name` | string | Tool invoked by agent |
| `agent.tool.duration_ms` | int | Tool execution time |
| `agent.tool.error` | string | Error if tool failed |

## Usage Example

```python
from opentelemetry import trace, metrics

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

with tracer.start_as_current_span("llm_request") as span:
    # Set request attributes
    span.set_attribute("gen_ai.system", "openai")
    span.set_attribute("gen_ai.request.model", "gpt-4")
    span.set_attribute("gen_ai.request.max_tokens", 256)
    
    # Make LLM call
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=256
    )
    
    # Set usage attributes
    span.set_attribute("gen_ai.usage.input_tokens", response.usage.prompt_tokens)
    span.set_attribute("gen_ai.usage.output_tokens", response.usage.completion_tokens)
    span.set_attribute("gen_ai.cost.total_request_cost", calculate_cost(response))
```

## Benefits

1. **Standardization**: Consistent telemetry across LLM libraries and frameworks
2. **Cost Control**: Track and optimize LLM spending
3. **Performance**: Monitor latency, throughput, and efficiency
4. **Debugging**: Trace issues across multi-step LLM workflows
5. **Compliance**: Audit trail for regulated use cases

## Next Steps

- Community review and feedback
- Integration into OpenTelemetry specification
- Support in major LLM client libraries
- Best practices documentation
