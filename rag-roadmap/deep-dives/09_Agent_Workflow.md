# Deep Dive: Agent Workflow System

> Alternative to: [[00_Closed_Loop_Search]] dialog flow — agents use a custom DAG of components

## What Happens

Instead of the linear chat flow, RAGFlow supports building **agent workflows** — directed acyclic graphs (DAGs) of components that can branch, loop, and combine multiple operations.

## Key Files

| File | Role |
|------|------|
| `agent/canvas.py` | Workflow execution engine (the DAG runner) |
| `agent/tools/retrieval.py` | Retrieval component for agents |
| `agent/component/` | All available components |
| `api/apps/restful_apis/agent_api.py` | Agent API endpoints |

## How It Differs from Dialog

```
Dialog Mode (simple):
  Query → Retrieval → LLM → Answer

Agent Mode (flexible DAG):
  Query → [Begin] → [Categorize] ─┬─ "tech" → [Retrieval] → [LLM] → [Answer]
                                   ├─ "general" → [LLM] → [Answer]
                                   └─ "sql" → [SQL Tool] → [Answer]
```

## DAG Execution: `canvas.py`

### Graph Definition (DSL)

```json
{
    "path": ["begin"],
    "components": {
        "begin": {
            "obj": {
                "component_name": "Begin",
                "params": {"prologue": "How can I help?"}
            },
            "downstream": ["categorize_0"]
        },
        "categorize_0": {
            "obj": {
                "component_name": "Categorize",
                "params": {
                    "llm_id": "gpt-4",
                    "category_description": {
                        "tech": "Technical questions about the product",
                        "general": "General questions",
                        "sql": "Database queries"
                    }
                }
            },
            "downstream": ["retrieval_0", "generate_0", "sql_0"]
        },
        "retrieval_0": {
            "obj": {
                "component_name": "Retrieval",
                "params": {
                    "dataset_ids": ["kb_abc"],
                    "similarity_threshold": 0.2,
                    "top_n": 6
                }
            },
            "downstream": ["generate_0"]
        },
        "generate_0": {
            "obj": {
                "component_name": "Generate",
                "params": {
                    "llm_id": "gpt-4",
                    "prompt": "Answer based on: {input}"
                }
            },
            "downstream": ["answer_0"]
        },
        "answer_0": {
            "obj": {"component_name": "Answer"},
            "downstream": []
        }
    }
}
```

### Execution Flow

```python
class Graph:
    async def run(self, **kwargs):
        """Execute the DAG starting from 'begin' node."""

        # 1. Start with begin component
        path = self.dsl["path"]  # ["begin"]

        # 2. Execute each component in BFS order
        while path:
            current = path.pop(0)
            component = self.components[current]

            # 3. Run component
            result = await component.run(self)

            # 4. Add downstream components to path
            for downstream in component.downstream:
                if downstream not in path:
                    path.append(downstream)

        # 5. Collect and stream results
        yield self.get_answer()
```

## Available Components

### Retrieval Component

```python
# agent/tools/retrieval.py
class Retrieval:
    async def _retrieve_kb(self, query, kb_ids):
        """
        Same hybrid search as dialog mode, but with extra features:
        - Variable substitution: kb_ids can reference canvas variables
        - Cross-language: auto-translate query for multilingual KBs
        - Metadata filtering: filter by document metadata
        """
        # Resolve variables
        kb_ids = [self._canvas.get_variable_value(id) for id in self._dataset_ids]

        # Cross-language enhancement
        if self._param.cross_languages:
            query = await cross_languages(tenant_id, None, query, languages)

        # Execute retrieval
        kbinfos = await retrievaler.retrieval(
            query, embd_mdl, tenant_ids, kb_ids,
            similarity_threshold=self._param.similarity_threshold,
            top_n=self._param.top_n,
            rerank_mdl=rerank_mdl,
        )

        # Store in canvas context
        self._canvas.add_reference(kbinfos["chunks"], kbinfos["doc_aggs"])
        return kbinfos
```

### Categorize Component

```python
# Uses LLM to classify the query into categories
# Each category routes to a different downstream component
async def classify(query, categories):
    prompt = f"Classify this query into one of: {list(categories.keys())}\nQuery: {query}"
    category = await llm.chat(prompt)
    return categories[category]  # Returns downstream component ID
```

### Generate Component

```python
# LLM generation with template variables
# Can reference: {input}, {sys.query}, retrieval results, etc.
async def generate(self, canvas):
    prompt = self._param.prompt
    # Replace variables
    prompt = prompt.replace("{input}", canvas.get_reference())
    prompt = prompt.replace("{sys.query}", canvas.get_variable_value("sys.query"))

    async for token in llm.async_chat_streamly_delta(system=prompt):
        yield token
```

### Other Components

| Component | Purpose |
|-----------|---------|
| **Begin** | Entry point, sets initial variables |
| **Answer** | Output node, streams to user |
| **Categorize** | Routes query to different paths |
| **Retrieval** | Search knowledge bases |
| **Generate** | LLM text generation |
| **Switch** | Conditional branching |
| **Loop** | Iterate over results |
| **Concentrator** | Merge multiple paths |
| **SQL** | Execute SQL queries |
| **Tavily** | Web search integration |
| **Wikipedia** | Wikipedia lookup |
| **ArXiv** | Paper search |
| **Email** | Send emails |
| **HTTP Request** | Call external APIs |

## Variable System

Components communicate through a shared variable namespace:

```python
# Built-in variables:
# sys.query      — the original user question
# sys.user_id    — current user ID
# sys.conversation_id — session ID

# Custom variables:
canvas.set_variable("retrieval_result", chunks)
canvas.get_variable("retrieval_result")

# Variable substitution syntax: {variable_name}
# In component params: "Answer based on {sys.query}"
```

## Example: Multi-Path Agent

```
User: "Compare the performance of method A vs method B"

DAG Execution:
1. Begin → receives query
2. Categorize → "technical comparison"
3. Retrieval_A → searches KB for "method A performance" → 5 chunks
4. Retrieval_B → searches KB for "method B performance" → 5 chunks
5. Concentrator → merges both retrieval results
6. Generate → "Based on the documentation, method A achieves X while method B achieves Y..."
7. Answer → streams to user with citations from both retrievals
```

## Connection to Main Loop

Agent mode is an **alternative execution path** for the same underlying components:
- Uses same `Dealer.retrieval()` for search → [[03_Hybrid_Search]]
- Uses same `LLMBundle` for generation → [[06_LLM_Generation]]
- Uses same `rerank_model.py` for reranking → [[04_Reranking]]
- Streams same SSE format → [[07_Response_Streaming]]

Back to [[00_Closed_Loop_Search]].
