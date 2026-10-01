# Project Structure Reference

## File Organization

```
Email/
├── Core Application Files
│   ├── app.py                    # Main Streamlit UI & entry point
│   ├── graph.py                  # LangGraph state machine builder
│   ├── nodes.py                  # Agent/approval/routing logic
│   ├── llm.py                    # LLM initialization
│   ├── tools.py                  # Tool definitions (email, delete, purchase)
│   ├── prompts.py                # System prompts for Claude
│   ├── config.py                 # Configuration & environment variables
│   ├── models.py                 # Type definitions
│   └── utils.py                  # Helper functions
│
├── Configuration & Metadata
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example              # Example environment configuration
│   ├── .gitignore                # Git ignore patterns
│   ├── README.md                 # Quick start guide
│   ├── DEVELOPMENT.md            # Developer documentation
│   ├── STRUCTURE.md              # This file
│   └── run.py                    # Convenience runner script
│
└── Generated at Runtime (not committed)
    ├── .env                      # Actual environment variables
    ├── __pycache__/              # Python cache
    ├── .streamlit/               # Streamlit configuration
    └── db.sqlite                 # (Optional) Checkpoint database
```

## File Descriptions

### Core Application Files

#### `app.py`
**Purpose**: Main Streamlit application  
**Key Components**:
- Page configuration and UI setup
- Session state management (thread_id, chat_history, pending_action)
- Graph invocation and interrupt handling
- Chat rendering and approval UI
**Size**: ~120 lines  
**Dependencies**: streamlit, config, utils, graph

#### `graph.py`
**Purpose**: LangGraph state machine construction  
**Key Components**:
- `build_graph()`: Creates and compiles the state machine
- Adds nodes: "agent", "approval"
- Sets up routing between nodes
- Initializes MemorySaver checkpointer
**Size**: ~35 lines  
**Dependencies**: langgraph, models, nodes

#### `nodes.py`
**Purpose**: Graph node implementations  
**Key Components**:
- `agent_node()`: Calls Claude with conversation history
- `approval_node()`: Freezes graph, shows approval prompt
- `route_after_agent()`: Routes to approval if tool called
**Size**: ~45 lines  
**Dependencies**: langchain_core, langgraph, llm, prompts, tools, models

#### `llm.py`
**Purpose**: LLM instance initialization  
**Key Components**:
- Creates ChatAnthropic instance with MODEL and max_tokens
- Binds ALL_TOOLS to the LLM
**Size**: ~10 lines  
**Dependencies**: langchain_anthropic, config, tools

#### `tools.py`
**Purpose**: Risky tool definitions requiring approval  
**Key Components**:
- `@tool send_email()`: SMTP email sending
- `@tool delete_file()`: File deletion
- `@tool make_purchase()`: Purchase action
- `ALL_TOOLS` registry
- `TOOLS_BY_NAME` lookup dict
**Size**: ~50 lines  
**Dependencies**: smtplib, email.mime, langchain_core, config

#### `prompts.py`
**Purpose**: System prompts for Claude  
**Key Components**:
- `SYSTEM_PROMPT`: Instructions for Claude's behavior
- Email formatting guidelines
- Tool usage instructions
**Size**: ~20 lines  
**Dependencies**: None

#### `config.py`
**Purpose**: Configuration management  
**Key Components**:
- Loads environment variables with `load_dotenv()`
- MODEL, SMTP settings
- `is_smtp_configured()` validation function
**Size**: ~20 lines  
**Dependencies**: os, dotenv

#### `models.py`
**Purpose**: Type definitions and imports  
**Key Components**:
- Exports `MessagesState` from langgraph
**Size**: ~5 lines  
**Dependencies**: langgraph

#### `utils.py`
**Purpose**: Utility functions  
**Key Components**:
- `get_reply_text()`: Extracts text from Claude's response (string or content blocks)
**Size**: ~15 lines  
**Dependencies**: None

### Configuration & Metadata

#### `requirements.txt`
Lists all Python dependencies with versions:
- streamlit, anthropic, langchain, langgraph
- python-dotenv for .env loading

#### `.env.example`
Template for environment configuration:
- SMTP settings (HOST, PORT, USERNAME, PASSWORD, FROM)
- Optional checkpoint backend configuration
- Copy to `.env` and fill in actual values

#### `.gitignore`
Patterns to exclude from version control:
- `.env` (never commit secrets)
- `__pycache__/`, `*.pyc` (Python cache)
- `venv/`, `env/` (virtual environments)
- `.vscode/`, `.idea/` (IDE files)
- `db.sqlite` (checkpoints)

#### `README.md`
Quick start guide:
- Feature overview
- Project structure
- Setup instructions
- How it works (user flow)
- Extending the agent
- Troubleshooting

#### `DEVELOPMENT.md`
Developer documentation:
- Architecture and dependency graph
- Running in development
- Testing approach
- Adding new tools
- Debugging tips
- Performance considerations
- Common pitfalls

#### `STRUCTURE.md`
This file - detailed reference of all files and purposes

#### `run.py`
Convenience runner script:
- Checks dependencies
- Validates .env exists
- Starts Streamlit app

## Data Flow

```
User Input (Streamlit UI)
        ↓
  app.py → run_graph()
        ↓
   graph.invoke()
        ↓
  agent_node() [calls llm with tools]
        ↓
  Did Claude call a tool?
    ├─ NO → Return final reply to UI
    └─ YES → route_after_agent()
               ↓
          approval_node()
               ↓
          interrupt() [freeze execution]
               ↓
          Show approval prompt to user
               ↓
          User clicks Approve/Reject
               ↓
          resume() with decision
               ↓
          Execute tool (if approved)
               ↓
          Return ToolMessage
               ↓
          agent_node() [Claude responds to result]
               ↓
          Loop back to routing decision...
```

## State Management

### Streamlit Session State
```python
st.session_state = {
    "thread_id": str,           # Unique conversation identifier
    "chat_history": [dict],     # User-visible messages
    "pending_action": dict|None # Interrupted tool call awaiting decision
}
```

### Graph State (MessagesState)
```python
{
    "messages": [
        HumanMessage(...),      # User messages
        AIMessage(...),         # Claude responses
        ToolMessage(...)        # Tool results
    ]
}
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SMTP_HOST` | smtp.gmail.com | Email server hostname |
| `SMTP_PORT` | 465 | Email server port |
| `SMTP_USERNAME` | (required) | Email account username |
| `SMTP_PASSWORD` | (required) | Email account password |
| `SMTP_FROM` | SMTP_USERNAME | Sender email address |
| `ANTHROPIC_API_KEY` | (from OS env) | Claude API key |

## Runtime Artifacts

### Generated/Optional Files

- `.env` - Actual configuration (never commit)
- `__pycache__/` - Python bytecode cache (auto-generated)
- `.streamlit/` - Streamlit configuration directory
- `db.sqlite` - SQLite checkpoint database (if using SqliteSaver)

These are listed in `.gitignore` and should not be committed.

## Import Relationships

### Dependency Graph

```
app.py
  ├─ streamlit
  ├─ langchain_core.messages
  ├─ langgraph.types
  ├─ config
  ├─ utils
  └─ graph

graph.py
  ├─ langgraph.graph
  ├─ langgraph.checkpoint.memory
  ├─ models
  └─ nodes

nodes.py
  ├─ langchain_core.messages
  ├─ langgraph.types
  ├─ langgraph.graph (END)
  ├─ llm
  ├─ prompts
  ├─ tools
  └─ models

llm.py
  ├─ langchain_anthropic
  ├─ config
  └─ tools

tools.py
  ├─ smtplib
  ├─ email.mime.text
  ├─ langchain_core.tools
  └─ config

prompts.py
  └─ (no dependencies)

config.py
  ├─ os
  └─ dotenv

models.py
  └─ langgraph.graph

utils.py
  └─ (no dependencies)
```

Circular dependencies: None! ✓

## Extensibility Points

### Adding New Tools
1. Define in `tools.py` with `@tool` decorator
2. Add to `ALL_TOOLS` list
3. Update `SYSTEM_PROMPT` if needed

### Customizing Behavior
1. Edit `SYSTEM_PROMPT` in `prompts.py`
2. Modify `agent_node()` or `approval_node()` in `nodes.py`
3. Adjust `route_after_agent()` for different routing

### Using Different Models
1. Update `MODEL` in `config.py`
2. Adjust `max_tokens` in `llm.py`

### Persistent Storage
1. Replace `MemorySaver()` in `graph.py` with `SqliteSaver("db.sqlite")`
2. Update documentation

## Quick Reference

| Task | File |
|------|------|
| Change Claude's behavior | `prompts.py` |
| Add a new tool | `tools.py` |
| Modify approval logic | `nodes.py` |
| Change UI | `app.py` |
| Configure SMTP | `.env` |
| Add dependencies | `requirements.txt` |
