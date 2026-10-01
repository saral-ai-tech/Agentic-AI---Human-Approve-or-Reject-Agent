# Human-in-the-Loop Agent

A Streamlit application that demonstrates human approval workflows for sensitive AI actions using LangGraph's interrupt/resume mechanism.

## Features

- **Human Approval System**: AI pauses before executing sensitive actions (send email, delete file, make purchase)
- **Interrupt/Resume**: Uses LangGraph's `interrupt()` to freeze execution and wait for user decision
- **Conversation Memory**: Maintains chat history with checkpoint persistence
- **Multi-turn Conversations**: Supports complex multi-step interactions with built-in context

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── config.py             # Configuration & environment variables
├── tools.py              # Tool definitions (send_email, delete_file, make_purchase)
├── prompts.py            # System prompts for Claude
├── nodes.py              # Graph nodes (agent, approval, routing logic)
├── graph.py              # LangGraph state machine builder
├── llm.py                # LLM initialization with tools
├── models.py             # Type definitions
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment variables
└── README.md             # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file by copying `.env.example`:

```bash
cp .env.example .env
```

Then update with your actual credentials:

```
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_FROM=your-email@gmail.com
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## How It Works

1. **User Input**: Type a message requesting an action (e.g., "send an email to my boss saying I'll be late")

2. **AI Processing**: Claude processes your request and decides if a tool call is needed

3. **Approval Gate**: If Claude wants to execute a risky tool:
   - The graph pauses using `interrupt()`
   - An approval dialog appears showing what Claude wants to do
   - You can **Approve** or **Reject** the action

4. **Execution/Feedback**: 
   - If approved: Tool executes and Claude reports the result
   - If rejected: Claude is informed the action was declined

5. **Conversation Continues**: Claude can ask follow-up questions or provide further assistance

## Key Design Decisions

### Modular Architecture
- Each concern (tools, nodes, graph, UI) is in its own module
- Easy to test, maintain, and extend

### Cached Graph
- `build_graph()` is called once and cached with `@st.cache_resource`
- This preserves the graph state and checkpointer across Streamlit reruns
- Critical for the interrupt/resume mechanism to work

### Tool Registry
- `TOOLS_BY_NAME` dict maps tool names to executables
- Used to invoke tools after user approval

### State Management
- `thread_id`: Unique identifier for each conversation (used by checkpointer)
- `chat_history`: User-visible conversation history
- `pending_action`: Holds interrupted tool call awaiting decision

## Extending the Agent

### Adding a New Tool

1. Add the tool function to `tools.py`:

```python
@tool
def new_action(param: str) -> str:
    """Description of the action. This requires approval."""
    # Implementation
    return f"Result: {param}"
```

2. Add it to `ALL_TOOLS` list at the bottom of `tools.py`

3. Update `SYSTEM_PROMPT` in `prompts.py` if special instructions are needed

### Customizing the System Prompt

Edit `prompts.py` to change Claude's behavior and instructions.

### Using a Different Checkpointer

By default, `MemorySaver()` stores checkpoints in memory. To persist across restarts:

```python
# In graph.py, replace:
# checkpointer = MemorySaver()
# With:
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver("db.sqlite")
```

## Troubleshooting

### Graph state is lost on Streamlit rerun
- Ensure `build_graph()` is decorated with `@st.cache_resource`
- Check that `graph_config` includes `thread_id`

### Email not sending
- Verify SMTP credentials are correct
- Check that `SMTP_USERNAME` and `SMTP_PASSWORD` are set in `.env`
- For Gmail: Use an App Password, not your regular password
- Check firewall/network allows SMTP connections to your mail server

### Approval prompt doesn't appear
- Check browser console for JavaScript errors
- Ensure `interrupt()` is being called in `approval_node()`
- Verify `__interrupt__` key is in graph result

## API Keys & Secrets

- Requires an **Anthropic API key** (set via environment or `.env`)
- Optional SMTP credentials for email functionality
- No keys are hardcoded; all config via environment variables

## License

MIT
