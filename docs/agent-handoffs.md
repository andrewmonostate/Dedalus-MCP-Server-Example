# Agent Handoffs and Multi-Model Routing

Agent handoffs enable sophisticated multi-model workflows where different AI models handle different parts of a task based on their strengths.

## Understanding Agent Handoffs

Agent handoffs allow you to:
- Route tasks to specialized models
- Chain multiple models for complex workflows
- Optimize for cost and performance
- Create collaborative agent systems

## Basic Handoff Pattern

```python
import os
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()

async def basic_handoff():
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    # Define multiple models for handoff
    result = await runner.run(
        input="Research latest AI developments, then handoff to Claude to write a technical summary",
        model=["openai/gpt-4", "claude-3-5-sonnet-20241022"],
        mcp_servers=["dedalus-labs/brave-search-mcp"],
        stream=False
    )
    
    return result.final_output
```

## Task-Based Model Selection

Different models excel at different tasks:

```python
async def intelligent_routing(task_type: str, content: str):
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    # Model selection based on task
    model_mapping = {
        "code_generation": "claude-3-5-sonnet-20241022",
        "data_analysis": "openai/gpt-4",
        "creative_writing": "claude-3-opus-20240229",
        "quick_answers": "openai/gpt-4o-mini",
        "research": "openai/gpt-4.1"
    }
    
    selected_model = model_mapping.get(task_type, "openai/gpt-4")
    
    result = await runner.run(
        input=content,
        model=selected_model,
        stream=False
    )
    
    return result
```

## Complex Multi-Stage Workflows

```python
async def multi_stage_analysis(topic: str):
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    
    # Stage 1: Research
    research_result = await runner.run(
        input=f"Research the latest information about {topic}",
        model="openai/gpt-4.1",
        mcp_servers=["dedalus-labs/brave-search-mcp"],
        stream=False
    )
    
    # Stage 2: Analysis
    analysis_result = await runner.run(
        input=f"Analyze this research and identify key insights: {research_result.final_output}",
        model="claude-3-5-sonnet-20241022",
        stream=False
    )
    
    # Stage 3: Report Generation
    report_result = await runner.run(
        input=f"Create a comprehensive report based on this analysis: {analysis_result.final_output}",
        model="claude-3-opus-20240229",
        stream=False
    )
    
    return {
        "research": research_result.final_output,
        "analysis": analysis_result.final_output,
        "report": report_result.final_output
    }
```

## MCP Server with Handoff Support

Build your MCP server to support agent handoffs:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Handoff-Enabled Server")

@mcp.tool()
def prepare_handoff(
    task: str,
    current_context: dict,
    target_model: str,
    handoff_instructions: str
) -> dict:
    """Prepare context for agent handoff"""
    
    # Structure the handoff package
    handoff_package = {
        "original_task": task,
        "context": current_context,
        "target_model": target_model,
        "instructions": handoff_instructions,
        "timestamp": datetime.now().isoformat(),
        "handoff_metadata": {
            "suggested_parameters": get_model_params(target_model),
            "expected_output_format": determine_output_format(task),
            "validation_criteria": get_validation_criteria(task)
        }
    }
    
    return handoff_package

@mcp.tool()
def route_to_specialist(
    content: str,
    analysis_type: str
) -> dict:
    """Route content to specialized model based on analysis type"""
    
    routing_rules = {
        "code_review": {
            "model": "claude-3-5-sonnet-20241022",
            "prompt_style": "technical",
            "focus": "bugs, performance, best practices"
        },
        "creative_expansion": {
            "model": "claude-3-opus-20240229",
            "prompt_style": "creative",
            "focus": "narrative, engagement, originality"
        },
        "fact_checking": {
            "model": "openai/gpt-4.1",
            "prompt_style": "analytical",
            "focus": "accuracy, sources, verification"
        },
        "summarization": {
            "model": "openai/gpt-4o-mini",
            "prompt_style": "concise",
            "focus": "key points, brevity, clarity"
        }
    }
    
    route = routing_rules.get(analysis_type, routing_rules["summarization"])
    
    return {
        "content": content,
        "routing": route,
        "ready_for_handoff": True
    }
```

## Collaborative Agent Patterns

### Sequential Processing
```python
async def sequential_processing(data: str):
    """Each agent processes and passes to the next"""
    
    # Agent 1: Parse and structure
    structured = await runner.run(
        input=f"Parse and structure this data: {data}",
        model="openai/gpt-4o-mini"
    )
    
    # Agent 2: Analyze patterns
    patterns = await runner.run(
        input=f"Analyze patterns in: {structured.final_output}",
        model="claude-3-5-sonnet-20241022"
    )
    
    # Agent 3: Generate insights
    insights = await runner.run(
        input=f"Generate insights from: {patterns.final_output}",
        model="openai/gpt-4"
    )
    
    return insights
```

### Parallel Processing
```python
async def parallel_analysis(content: str):
    """Multiple agents analyze simultaneously"""
    
    tasks = [
        runner.run(input=f"Technical analysis: {content}", model="claude-3-5-sonnet"),
        runner.run(input=f"Business implications: {content}", model="openai/gpt-4"),
        runner.run(input=f"Risk assessment: {content}", model="claude-3-opus")
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Synthesize results
    synthesis = await runner.run(
        input=f"Synthesize these analyses: {[r.final_output for r in results]}",
        model="openai/gpt-4"
    )
    
    return synthesis
```

### Voting/Consensus Pattern
```python
async def consensus_decision(question: str):
    """Multiple agents vote on best answer"""
    
    models = [
        "claude-3-5-sonnet-20241022",
        "openai/gpt-4",
        "claude-3-opus-20240229"
    ]
    
    responses = []
    for model in models:
        result = await runner.run(
            input=question,
            model=model
        )
        responses.append({
            "model": model,
            "response": result.final_output
        })
    
    # Have a judge model evaluate responses
    judge_result = await runner.run(
        input=f"Evaluate these responses and determine the best answer: {responses}",
        model="openai/gpt-4"
    )
    
    return judge_result
```

## Best Practices for Handoffs

1. **Clear Context Transfer**: Ensure all necessary context is passed between agents
2. **Model Strengths**: Choose models based on their proven strengths
3. **Error Handling**: Handle failures gracefully with fallback models
4. **Cost Optimization**: Balance model capabilities with cost
5. **Latency Management**: Consider parallel processing for speed
6. **Result Validation**: Validate outputs before passing to next agent
7. **Audit Trail**: Log all handoffs for debugging and compliance

## Advanced Handoff Strategies

### Dynamic Model Selection
```python
@mcp.tool()
def select_optimal_model(
    task: str,
    constraints: dict
) -> str:
    """Dynamically select best model based on task and constraints"""
    
    # Evaluate task complexity
    complexity = assess_complexity(task)
    
    # Check constraints
    max_cost = constraints.get("max_cost", float("inf"))
    max_latency = constraints.get("max_latency", float("inf"))
    required_capabilities = constraints.get("capabilities", [])
    
    # Model selection logic
    if complexity == "simple" and max_cost < 0.01:
        return "openai/gpt-4o-mini"
    elif "code" in required_capabilities:
        return "claude-3-5-sonnet-20241022"
    elif "creative" in required_capabilities:
        return "claude-3-opus-20240229"
    else:
        return "openai/gpt-4"
```

## Next Steps

- [Performance Optimization](./performance.md)
- [Deployment Guide](./deployment.md)
- [Security Best Practices](./security.md)