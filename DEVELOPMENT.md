# Development Guide

## Project Architecture

This project follows a modular architecture for clarity and maintainability:

### Module Dependency Graph

```
app.py (Streamlit UI)
  ├─ graph.py (Graph building)
  │  ├─ nodes.py (Node logic)
  │  │  ├─ llm.py (LLM instance)
  │  │  ├─ models.py (Type definitions)
  │  │  ├─ prompts.py (System prompts)
  │  │  └─ tools.py (Tool definitions)
  │  └─ models.py (Type definitions)
  ├─ config.py (Configuration)
  ├─ utils.py (Utility functions)
  └─ graph.py
```

### Module Responsibilities

- **app.py**: Streamlit UI, session state management, user interaction
- **graph.py**: LangGraph state machine construction and compilation
- **nodes.py**: Node implementations (agent, approval, routing logic)
- **llm.py**: LLM initialization with bound tools
- **tools.py**: Tool definitions with @tool decorators
- **prompts.py**: System prompts and instructions for Claude
- **config.py**: Environment variable loading and configuration
- **models.py**: Type definitions (MessagesState, etc.)
- **utils.py**: Helper functions (get_reply_text, etc.)

## Running the Application

### Development

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your actual credentials

# Run the app
streamlit run app.py
```

### Production Deployment

For production deployment on services like Streamlit Cloud, Railway, Hugging Face Spaces, etc.:

1. Push code to GitHub
2. Connect your repository to the deployment service
3. Set environment variables in the service's settings (don't commit .env)
4. The service will automatically run `pip install -r requirements.txt` and `streamlit run app.py`

### Persistent Checkpoints (Production)

For production, replace in-memory checkpointing with SQLite:

```python
# In graph.py
from langgraph.checkpoint.sqlite import SqliteSaver

# Replace: checkpointer = MemorySaver()
checkpointer = SqliteSaver("db.sqlite")
```

This ensures conversations survive app restarts.

## Testing

### Manual Testing Checklist

- [ ] User can input a request
- [ ] Claude responds appropriately
- [ ] Tool calls trigger approval prompt
- [ ] Approve button executes the tool
- [ ] Reject button prevents execution
- [ ] Conversation history persists
- [ ] Multiple turns work correctly
- [ ] SMTP is optional (works with warnings if not configured)

### Adding Unit Tests

Create `tests/test_tools.py`:

```python
import pytest
from tools import send_email, delete_file, make_purchase

def test_delete_file_returns_message():
    result = delete_file("test.txt")
    assert "deleted" in result.lower()

def test_make_purchase_formats_currency():
    result = make_purchase("Widget", 19.99)
    assert "$19.99" in result
```

Run tests:
```bash
pip install pytest
pytest tests/
```

## Adding New Tools

### Step 1: Define the Tool

In `tools.py`:

```python
@tool
def archive_files(folder: str) -> str:
    """Archive files in a folder. Requires approval."""
    # Implementation
    return f"✅ Archived {folder}"
```

### Step 2: Register the Tool

The tool is automatically registered when added to `ALL_TOOLS`:

```python
ALL_TOOLS = [send_email, delete_file, make_purchase, archive_files]
```

### Step 3: Update System Prompt (if needed)

In `prompts.py`, add specific instructions if the tool needs special handling:

```python
SYSTEM_PROMPT = """
...existing instructions...

For archive_files:
- Only archive if the user explicitly requests it.
- Confirm the folder path with the user first.
"""
```

## Debugging

### Check Graph Execution

Add debug logging to `nodes.py`:

```python
def agent_node(state: MessagesState):
    print(f"DEBUG: Agent received {len(state['messages'])} messages")
    response = llm.invoke(
        [{"role": "system", "content": SYSTEM_PROMPT}] + state["messages"]
    )
    print(f"DEBUG: Agent response type: {type(response)}")
    print(f"DEBUG: Tool calls: {getattr(response, 'tool_calls', None)}")
    return {"messages": [response]}
```

### Check State Between Reruns

In `app.py`, add debug output:

```python
if st.session_state.pending_action:
    st.write("DEBUG: Pending action =", st.session_state.pending_action)
    st.write("DEBUG: Thread ID =", st.session_state.thread_id)
```

### View LangGraph State

The graph state is a dict with `{"messages": [...]}`. Check it:

```python
def run_graph(graph_input):
    result = graph.invoke(graph_input, graph_config)
    st.write("DEBUG: Graph result keys =", list(result.keys()))
    st.write("DEBUG: Num messages =", len(result.get("messages", [])))
```

## Performance Considerations

1. **Graph Caching**: The graph is cached with `@st.cache_resource` - this is critical
2. **LLM Tokens**: Claude Haiku is fast and cheap; adjust `max_tokens=1000` if needed
3. **Checkpointer**: MemorySaver is fine for dev; use SqliteSaver for production with multiple users
4. **Streamlit Reruns**: Minimize expensive operations in callbacks

## Common Pitfalls

### Conversation Lost After Approval/Rejection

**Issue**: The graph state disappears when you click Approve/Reject.

**Cause**: `build_graph()` is not cached or `thread_id` is changing.

**Fix**:
- Ensure `build_graph()` is wrapped with `@st.cache_resource`
- Ensure `thread_id` is set once and never changes: `if "thread_id" not in st.session_state:`

### Approval Prompt Never Appears

**Issue**: Claude calls a tool, but no approval dialog shows.

**Cause**: `interrupt()` is not being called or result isn't checked for `__interrupt__`.

**Fix**:
- Verify `approval_node()` is being reached (add debug logging)
- Check that `run_graph()` checks for `__interrupt__` in result
- Ensure `route_after_agent()` correctly routes to "approval" node

### Email Doesn't Send

**Issue**: SMTP error or silent failure.

**Fixes**:
- Check `.env` for typos in SMTP credentials
- For Gmail: Use App Password, not regular password
- Verify firewall allows outbound SMTP (port 465)
- Check `send_email()` implementation handles errors

## Dependencies

- **langchain**: LLM framework
- **langgraph**: Graph orchestration with interrupts
- **langchain-anthropic**: Anthropic integration
- **streamlit**: Web UI framework
- **python-dotenv**: Environment variable loading

## Further Reading

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph Interrupts & Resume](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [Streamlit Caching](https://docs.streamlit.io/develop/concepts/architecture/caching)
- [Anthropic Claude API](https://docs.anthropic.com/)
