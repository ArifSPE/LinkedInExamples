# Tools vs Skills in Agentic AI

I kept seeing the same confusion in AI conversations: people use "tools" and "skills" as if they mean the same thing.

They do not.

That single distinction changed how I think about building agent systems, and this notebook is my practical breakdown of it.

## The Simple Rule I Use

- **Tool = capability**
- **Skill = workflow**

Or in plain language:

- Tools do one action well
- Skills combine actions to achieve a business outcome

Another way to remember it:

- Skills decide **what** to do
- Tools execute **how** to do it

## Why I Built This Notebook

I wanted one place that shows both concept and implementation, from first principles to code.

This notebook walks through:

1. The conceptual difference between tools and skills
2. A LangChain example with atomic tool definitions and agent calls
3. A LangGraph skill workflow orchestrating those tools
4. Graph visualization (Mermaid/PNG)
5. Practical patterns like memory and multi-skill routing

## Notebook Locations

Primary notebook in this repo:
- `ToolsVsSkills_Examples.ipynb`

Agent pattern notebook suite index:
- `AIAgentDesignPatterns.ipynb`

New state-aggregation example notebook:
- `12_Annotated_State_Aggregation.ipynb`

Original/source notebook used for the post:
- `/Users/arifshaikh/Development/Coursera/notebooks/ToolsVsSkills_Examples.ipynb`

## Tools vs Skills at a Glance

| Aspect | Tools | Skills |
|---|---|---|
| Level | Low-level | High-level |
| Purpose | Do one thing | Achieve a goal |
| Logic | Minimal | Workflow + strategy |
| Composition | Independent | Built from tools |
| Reuse | Technical reuse | Business reuse |

## Why This Matters in Real Systems

When teams separate tools and skills clearly, they get better architecture outcomes:

- **Modularity**: swap tools without rebuilding the entire flow
- **Scalability**: add new skills as business scenarios grow
- **Maintainability**: cleaner ownership boundaries
- **Enterprise fit**: maps naturally to capability-based architecture

This is often the difference between:

- building isolated demos
- building a reusable agent platform

## Quick Start

Install dependencies:

```bash
pip install langchain langchain-core langchain-community langchain-ollama langgraph
```

Then run:

- `ToolsVsSkills_Examples.ipynb`

## Final Thought

I think of it this way:

- Tools are the building blocks
- Skills are the intelligence patterns built from those blocks

Once this clicks, agent design becomes clearer, more scalable, and far easier to evolve.
