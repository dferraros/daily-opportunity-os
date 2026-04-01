# PREVIOUS COWORK SESSION - FULL EXTRACTION
Date: 2026-02-24
Session ID: aa354d00-f848-4558-a240-3a726a9507b0
Total messages: 10

====================================================================================================
# SESSION TRANSCRIPT
====================================================================================================
====================================================================================================
[USER] Line 2
====================================================================================================
help me design a speciallized agent. The idea is to have a dashboard for the A/B tests of the bit2me lifecycle

help me understand what do we need. I'm sending an example of one that a colleague built for brokerage

the idea is to have an agent that can analyze all the bit2me data, from product, clusters, retention, activation, countries, you name it

in which we can decide and create A/B tests, flows, feed data from qlik, clevertab, bitquery

I have no idea how to do this. Research the best anthropic tools for this, I can provide the data

====================================================================================================
[ASSISTANT] Line 3
====================================================================================================
[THINKING]
The user wants to design a specialized AI agent for managing A/B tests and lifecycle analytics at Bit2Me. They're showing me screenshots of an existing analytics tool called "Poly" that their colleague built for brokerage analytics. They want something similar but for lifecycle/product analytics with A/B testing capabilities.

Let me understand what they're asking:
1. A dashboard/agent for A/B tests of the Bit2Me lifecycle
2. Can analyze data from: product, clusters, retention, activation, countries
3. Can connect to: Qlik, Clever Tap, Bitquery
4. They want to understand what tools/approach to use


5. I'm looking at how Poly works as a reference—it's an AI analytics assistant built on BigQuery with natural language query capabilities, schema documentation, and data source syncing. I need to figure out the best approach for building something similar using Claude's tools, focusing on the A/B testing and lifecycle analytics angle.

====================================================================================================
[ASSISTANT] Line 4
====================================================================================================
[TOOL CALL: Task]
{
  "description": "Research Anthropic agent tools",
  "subagent_type": "claude-code-guide",
  "prompt": "Research and summarize the best Anthropic tools for building a specialized data analytics agent. Specifically:\n\n1. What is the Claude Agent SDK? How does it work? What can it do?\n2. What is the Model Context Protocol (MCP)? How do MCP servers work?\n3. How does Claude Code support building agents/plugins?\n4. What are \"Cowork plugins\" and how are they structured?\n5. How can external data sources (like BigQuery, Qlik, APIs) be connected to a Claude-powered agent?\n6. What is the best architecture for a specialized analytics agent that can: query data, run analyses, help design A/B tests, and connect to multiple data sources?\n\nSearch https://docs.claude.com and https://www.anthropic.com for relevant documentation. Be specific about capabilities, limitations, and recommended approaches."
}

====================================================================================================
[ASSISTANT] Line 5
====================================================================================================
[TOOL CALL: WebSearch]
{
  "query": "Anthropic Claude agent SDK MCP server analytics dashboard 2025 2026"
}

====================================================================================================
[USER] Line 7
====================================================================================================
[TOOL RESULT - toolu_01PhSyPCvexBnoTLAXnADWQ2]
Excellent. Now I have comprehensive information to provide a detailed summary. Let me compile this into a well-organized response.

## Comprehensive Research Summary: Building a Specialized Data Analytics Agent with Anthropic Tools

Based on my research of Anthropic's official documentation and current 2026 capabilities, here's a detailed breakdown of the best tools and architecture for building a specialized data analytics agent.

---

## 1. What is the Claude Agent SDK? How does it work? What can it do?

### Overview
The **Claude Agent SDK** is Anthropic's framework for building autonomous AI agents that can use tools, make decisions, and interact with external systems. It's available for both **Python** and **TypeScript** (with V2 preview).

### Key Capabilities
- **Autonomous tool use**: Agents can decide when and how to call tools
- **Multi-step planning and execution**: Plan and execute complex, multi-step tasks
- **State management**: Maintain conversation state and memory across sessions
- **Real-time streaming**: Stream responses for better user experience
- **Custom tool integration**: Define domain-specific tools (APIs, databases, etc.)
- **Secure deployment**: Handle permissions and security controls
- **Built-in tools**: Code execution, web search, computer use, bash, text editing

### Core Architecture

The SDK follows an **agentic loop pattern**:

1. **User Input** → Agent receives a task
2. **Planning** → Claude reasons about what tools to use
3. **Tool Calling** → Agent calls appropriate tools with parameters
4. **Tool Execution** → SDK executes tools and collects results
5. **Response Generation** → Claude processes results and generates final response
6. **Output** → Return results to user

### Example: Basic Setup
```python
from anthropic import Anthropic

client = Anthropic()

# Define tools your agent can use
tools = [
    {
        "name": "query_database",
        "description": "Execute SQL queries against your data warehouse",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SQL query to execute"}
            },
            "required": ["query"]
        }
    }
]

# Create agent with tool use
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's our top revenue-generating product?"}
    ]
)
```

### Best Models for Analytics Agents
- **Claude Opus 4.6** (Latest, most capable - recommended for complex analysis)
- **Claude Sonnet 4.6** (Balanced performance and speed)
- **Claude Haiku 4.5** (Fast and efficient for simple queries)

**Documentation**: https://platform.claude.com/docs/en/agent-sdk/quickstart.md

---

## 2. What is the Model Context Protocol (MCP)? How do MCP servers work?

### What is MCP?
The **Model Context Protocol (MCP)** is an open-source standard (introduced by Anthropic in November 2024) that standardizes how AI systems integrate with external data sources, tools, and systems. It's now a Linux Foundation project (Agentic AI Foundation).

### Current Status (2026)
- **10,000+ public MCP servers** across all major platforms
- **Industry adoption**: ChatGPT, Cursor, Gemini, Microsoft Copilot, VS Code all support MCP
- **Governance**: Donated to the Agentic AI Foundation (co-founded by Anthropic, Block, and OpenAI, with support from Google, Microsoft, AWS, Cloudflare, Bloomberg)

### How MCP Servers Work

MCP servers act as **bridges between Claude and external data sources**. They provide:

1. **Tools** - Functions Claude can call (e.g., query BigQuery, fetch data from Snowflake)
2. **Resources** - Data that Claude can reference
3. **Prompts** - Reusable instruction templates for specific tasks

### Three Ways to Connect MCP Servers

**Option 1: Remote HTTP Server**
```bash
claude --mcp add-http-server bigquery \
  --url https://mcp.example.com/bigquery
```

**Option 2: Remote SSE Server**
```bash
claude --mcp add-sse-server snowflake \
  --url https://mcp.example.com/snowflake
```

**Option 3: Local Stdio Server**
```bash
claude --mcp add-stdio-server postgres \
  --command "docker run my-postgres-mcp"
```

### MCP Configuration in Code
```json
.mcp.json
{
  "mcpServers": {
    "bigquery": {
      "command": "npx",
      "args": ["@anthropic-ai/bigquery-mcp"]
    }
  }
}
```

### How Claude Uses MCP Tools
MCP tool definitions use a similar schema format to Claude's tool format. The SDK automatically converts MCP tools:

```python
# Convert MCP tools to Claude format
mcp_tools = await mcp_session.list_tools()

claude_tools = []
for tool in mcp_tools.tools:
    claude_tools.append({
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": tool.inputSchema  # Rename to input_schema
    })

# Use with Claude API
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    tools=claude_tools,
    messages=[...]
)
```

### Advanced MCP Features
- **Tool Search**: For agents with hundreds of tools, optimizes which tools to expose without blowing up context
- **Programmatic Tool Calling**: Programmatically control which tools are available
- **MCP Resource References**: Claude can reference data from MCP resources
- **MCP Prompts as Commands**: Use MCP prompts as `/commands` in Claude Code

**Documentation**: https://code.claude.com/docs/en/mcp.md

---

## 3. How does Claude Code support building agents/plugins?

### Claude Code's Agent-Building Features

**Claude Code** (the CLI tool) provides multiple ways to build agents:

#### A. **Subagents** (Built-in Agent System)
Create specialized AI agents that handle specific tasks:
- **Automatic delegation**: Main thread can delegate to subagents
- **Parallel execution**: Run multiple subagents in background
- **Isolated context**: Each agent has its own memory and constraints
- **Tool restrictions**: Control what each agent can access

```markdown
agents/data-analyst.md
---
description: Analyzes data and generates insights
model: claude-opus-4-6
instructions: |
  You are a data analysis expert. Use SQL queries to explore datasets.
  Focus on statistical rigor and reproducibility.
tools:
  - postgres-query
  - python-execution
---

When analyzing data:
1. Explore the schema first
2. Run exploratory analysis
3. Test hypotheses statistically
4. Provide confidence intervals
```

#### B. **Agent Teams**
Orchestrate multiple agents working together:
- **Team coordination**: Agents collaborate on complex tasks
- **Competing hypotheses**: Run parallel investigations
- **Quality gates**: Enforce review steps with hooks
- **Task assignment**: Assign and claim tasks between agents

#### C. **Plugins** (Distribute & Share)
Package agents, skills, and tools as reusable plugins:
- **Namespace isolation**: Skills are prefixed (`/plugin-name:skill-name`)
- **Component bundling**: Combine skills, agents, hooks, and MCP servers
- **Distribution**: Share via plugin marketplaces
- **Versioning**: Semantic versioning for releases

### Plugin Structure for Analytics Agent

```
analytics-plugin/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── skills/
│   ├── query-data/
│   │   └── SKILL.md            # Query any data source
│   ├── statistical-test/
│   │   └── SKILL.md            # Run hypothesis tests
│   └── design-ab-test/
│       └── SKILL.md            # Design A/B tests
├── agents/
│   ├── data-analyst.md         # Main analytics agent
│   ├── statistician.md         # Statistical expert
│   └── business-analyst.md     # Business insights
├── hooks/
│   └── hooks.json              # Validation & automation
├── .mcp.json                   # MCP server configs
└── settings.json               # Default settings
```

### Example: Analytics Skill

```markdown
skills/query-data/SKILL.md
---
name: query-data
description: |
  Query any connected data source (BigQuery, Snowflake, etc.)
  Use when exploring data, answering business questions, or
  investigating metrics.
tools:
  - bigquery-mcp
  - snowflake-mcp
---

# Query Data Skill

When querying data:
1. Start by exploring the schema if unfamiliar with the data
2. Ask clarifying questions about what specific metrics or segments
3. Write efficient queries that minimize computation
4. Always show the raw query results before interpretation
5. Provide context about data freshness and quality
```

### Example: A/B Test Design Skill

```markdown
skills/design-ab-test/SKILL.md
---
name: design-ab-test
description: |
  Design rigorous A/B tests with proper sample sizing,
  statistical power, and success metrics.
  Use when planning experiments or validating hypotheses.
tools:
  - python-execution
  - research-tool
---

# A/B Test Design Skill

When designing an A/B test:
1. Define the hypothesis clearly
2. Determine success metrics (primary and secondary)
3. Calculate required sample size for desired power (80% typically)
4. Specify minimum detectable effect
5. Plan the test duration
6. Consider confounding variables and traffic allocation
7. Define guardrail metrics
```

**Documentation**: https://code.claude.com/docs/en/plugins.md

---

## 4. What are "Cowork plugins" and how are they structured?

### What is Cowork?

**Cowork** is Claude Code's collaborative mode where multiple agents work together on the same task. Cowork plugins enable team-based development patterns where:
- Multiple agents are spawned to tackle different aspects of a task
- Agents can communicate and build on each other's work
- Each agent has specialized skills and tools
- A lead agent coordinates the overall effort

### Cowork Plugin Structure

A Cowork plugin is essentially an **enhanced plugin with agent team coordination**:

```
analytics-cowork-plugin/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── lead-analyst.md        # Coordinates other agents
│   ├── data-engineer.md       # Data prep & query optimization
│   ├── statistician.md        # Statistical analysis & testing
│   └── business-analyst.md    # Business insights & recommendations
├── skills/
│   ├── explore-data/
│   ├── optimize-queries/
│   ├── statistical-tests/
│   └── generate-insights/
├── hooks/
│   └── hooks.json             # Quality gates between agents
├── .mcp.json                  # Data source connections
└── settings.json              # Enable agent teams
```

### Cowork Settings Configuration

```json
settings.json
{
  "agent": "lead-analyst",
  "agentTeams": {
    "enabled": true,
    "teammates": [
      "data-engineer",
      "statistician",
      "business-analyst"
    ]
  }
}
```

### How Cowork Works in Practice

1. **Lead agent** receives user request: "Analyze Q1 revenue by product category and recommend changes"
2. **Lead delegates**: Asks data-engineer to prepare optimized queries
3. **Agents work in parallel**: Statistician calculates trends, analyst researches context
4. **Results gathered**: Lead synthesizes findings into coherent analysis
5. **Quality gates**: Hooks validate analysis methodology and results

**Creating Cowork plugins**: Use `/cowork-plugin-management:create-cowork-plugin` skill

---

## 5. How can external data sources be connected to a Claude-powered agent?

### Connection Methods

There are three primary ways to connect external data sources:

#### Method 1: MCP Servers (Recommended)

**Pros**: Standardized, reusable, secure, runs on Claude Code and API
**Cons**: Requires MCP server implementation

**Supported Data Sources (2026)**:

| Source | MCP Server Status | Best For |
|--------|-------------------|----------|
| **BigQuery** | Official Google MCP server (managed & local) | Cloud-native analytics, integrated with GCP |
| **Snowflake** | Official Snowflake MCP server | Enterprise data warehouse, multi-cloud |
| **PostgreSQL** | Community & official MCP servers | Open-source database, self-hosted |
| **MySQL** | Community MCP servers | Web applications, MySQL-based systems |
| **Databricks** | Official Databricks MCP server | Lakehouse analytics, Apache Spark jobs |
| **DuckDB** | Community MCP servers | Local analytics, columnar processing |
| **ClickHouse** | Community MCP servers | Time-series and analytics workloads |
| **GitHub** | Official GitHub MCP server | Repository analysis, issue tracking |
| **Slack** | Official Slack MCP server | Channel analysis, conversation insights |

**How to Connect BigQuery via MCP**:
```json
.mcp.json
{
  "mcpServers": {
    "bigquery": {
      "command": "node",
      "args": ["./node_modules/@anthropic-ai/bigquery-mcp/index.js"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "~/.config/gcloud/application_default_credentials.json"
      }
    }
  }
}
```

**How to Connect Snowflake via MCP**:
```json
{
  "mcpServers": {
    "snowflake": {
      "command": "node",
      "args": ["./node_modules/snowflake-mcp/index.js"],
      "env": {
        "SNOWFLAKE_ACCOUNT": "xy12345.us-east-1",
        "SNOWFLAKE_USER": "analyst",
        "SNOWFLAKE_PASSWORD": "${SNOWFLAKE_PASSWORD}",
        "SNOWFLAKE_WAREHOUSE": "ANALYTICS"
      }
    }
  }
}
```

#### Method 2: Custom Tools (Agent SDK)

**Pros**: Full control, integrate any API or system
**Cons**: Must implement and maintain tool definitions

```python
# Define custom tool for your data source
tools = [
    {
        "name": "query_analytics_api",
        "description": "Query your custom analytics platform API",
        "input_schema": {
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "description": "Metric name (e.g., 'daily_active_users')"
                },
                "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                "segment": {"type": "string", "description": "Optional segment filter"}
            },
            "required": ["metric", "start_date", "end_date"]
        }
    }
]

# Claude will call this, and you execute it
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    tools=tools,
    messages=[{"role": "user", "content": "How many DAU in the last 30 days?"}]
)

# Handle tool use
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            tool_name = block.name
            tool_input = block.input
            # Execute tool: call your API
            result = query_analytics_api(**tool_input)
```

#### Method 3: CData Connect AI

**For BigQuery & Snowflake integration without MCP implementation**:
- CData Connect AI provides real-time connectors for Claude Agent SDK
- Works with BigQuery and Snowflake
- No need to build custom MCP servers
- Handles authentication and data transfer

**Documentation**:
- [BigQuery via CData](https://www.cdata.com/kb/tech/bigquery-cloud-claude-agent-sdk.rst)
- [Snowflake via CData](https://www.cdata.com/kb/tech/snowflake-cloud-claude-agent-sdk.rst)

### Authentication & Security Best Practices

1. **Use environment variables** for credentials
2. **Implement OAuth** for remote MCP servers
3. **Restrict tool access** with permissions rules
4. **Sandbox queries** to prevent unauthorized data access
5. **Audit tool use** with hooks and logging

---

## 6. Best Architecture for a Specialized Analytics Agent

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  Claude Code (CLI) / Web / VS Code / Slack / GitHub Actions  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              AGENT ORCHESTRATION LAYER                        │
│                                                                │
│  ┌─────────────────┐    ┌─────────────────┐                  │
│  │  Lead Analyst   │    │  Agent Teams    │                  │
│  │  (Coordinator)  │    │  (Parallel)     │                  │
│  └─────────────────┘    └─────────────────┘                  │
│         │                       │                              │
│    Delegates                Specialization                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              SPECIALIZED AGENTS LAYER                         │
│                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ Data Engineer    │  │ Statistician     │  │  Business  │ │
│  │ Agent            │  │ Agent            │  │  Analyst   │ │
│  │                  │  │                  │  │  Agent     │ │
│  │ ▪ Query Optimize │  │ ▪ A/B Test Design│  │ ▪ Insights │ │
│  │ ▪ Schema Explore │  │ ▪ Hypothesis Test│  │ ▪ Reports  │ │
│  │ ▪ Performance    │  │ ▪ Power Analysis │  │ ▪ Trends   │ │
│  └──────────────────┘  └──────────────────┘  └────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│               TOOLS & SKILLS LAYER                            │
│                                                                │
│  ┌────────────────┐  ┌───────────────┐  ┌────────────────┐  │
│  │ Query Skills   │  │ Analysis      │  │ Visualization  │  │
│  │                │  │ Skills        │  │ Skills         │  │
│  │ ▪ sql-query    │  │               │  │                │  │
│  │ ▪ raw-query    │  │ ▪ stat-test   │  │ ▪ create-chart │  │
│  │ ▪ explore-data │  │ ▪ correlation │  │ ▪ summary-table│  │
│  └────────────────┘  │ ▪ distribution│  │ ▪ ppt-slide    │  │
│                      │ ▪ ab-test     │  │                │  │
│                      └───────────────┘  └────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              MCP SERVERS & DATA SOURCES                       │
│                                                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  BigQuery MCP   │  │ Snowflake MCP   │  │ PostgreSQL   │ │
│  │  Server         │  │ Server          │  │ MCP Server   │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬───────┘ │
│           │                    │                  │            │
│  ┌────────▼────────┐  ┌────────▼────────┐  ┌─────▼───────┐  │
│  │ BigQuery        │  │ Snowflake       │  │ PostgreSQL  │  │
│  │ Data Warehouse  │  │ Lakehouse       │  │ Database    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Recommended Stack

#### Frontend: Claude Code + Web Interface
- **Claude Code**: Interactive development, real-time analysis
- **Claude.ai Web**: Share insights with non-technical users
- **Slack integration**: Quick queries from team chat
- **GitHub Actions**: Automated scheduled reports

#### Core Agent (Claude Opus 4.6)
- **Model**: Claude Opus 4.6 (most capable, best for complex analysis)
- **Max tokens**: 4096-8192 (higher for large result sets)
- **Extended thinking**: Enable for complex statistical problems

#### Specialized Sub-Agents
1. **Data Engineer Agent** (Claude Sonnet 4.6)
   - Explores schemas
   - Optimizes queries
   - Validates data quality
   
2. **Statistician Agent** (Claude Opus 4.6)
   - Designs A/B tests with power analysis
   - Performs hypothesis testing
   - Calculates confidence intervals
   
3. **Business Analyst Agent** (Claude Sonnet 4.6)
   - Interprets findings
   - Generates business recommendations
   - Creates executive summaries

#### Tools & Skills

**Query Skills**:
- `sql-query`: Execute SQL queries (with optimization hints)
- `explore-data`: Run exploratory analysis (cardinality, distributions)
- `inspect-schema`: Understand table/column definitions

**Analysis Skills**:
- `statistical-test`: T-tests, chi-square, ANOVA
- `ab-test-design`: Sample sizing, power analysis, MDE calculation
- `correlation-analysis`: Find relationships in data
- `time-series-analysis`: Trends, seasonality, forecasting

**Visualization Skills**:
- `create-chart`: Line, bar, scatter plots with Python
- `create-dashboard`: Interactive HTML dashboards
- `generate-report`: PowerPoint slides or PDF reports

#### MCP Connections

**Priority 1 (Essential)**:
- BigQuery MCP Server (Google Cloud official)
- Snowflake MCP Server (official)

**Priority 2 (Recommended)**:
- PostgreSQL MCP Server (for backup/reference data)
- GitHub MCP Server (for code-related analytics)

**Priority 3 (Optional)**:
- Slack MCP Server (for usage analytics)
- Custom internal APIs via CData or local MCP servers

### Example: Complete Analytics Plugin

```
analytics-plugin/
├── .claude-plugin/
│   └── plugin.json
│
├── agents/
│   ├── lead-analyst.md
│   │   └── Coordinates other agents, synthesizes findings
│   ├── data-engineer.md
│   │   └── Query optimization, schema exploration
│   ├── statistician.md
│   │   └── A/B testing, hypothesis testing
│   └── business-analyst.md
│       └── Insights, recommendations, reporting
│
├── skills/
│   ├── query-data/
│   │   ├── SKILL.md
│   │   └── schema-samples.md (reference)
│   ├── statistical-test/
│   │   ├── SKILL.md
│   │   └── test-reference.md
│   ├── design-ab-test/
│   │   ├── SKILL.md
│   │   └── power-analysis.md
│   ├── explore-data/
│   │   └── SKILL.md
│   ├── create-visualization/
│   │   └── SKILL.md
│   └── generate-report/
│       └── SKILL.md
│
├── hooks/
│   └── hooks.json
│       ├── PostToolUse: Validate SQL queries
│       ├── PostToolUse: Check statistical assumptions
│       └── Stop: Ensure recommendations are evidence-based
│
├── .mcp.json
│   ├── bigquery MCP server
│   └── snowflake MCP server
│
├── settings.json
│   └── Agent team config
│
└── README.md
    └── Setup & usage instructions
```

### Deployment Options

**Option 1: Claude Code (Development & Ad-hoc)**
- Best for: Exploratory analysis, one-off questions
- Cost: Per-request pricing
- Latency: Real-time
- Hosting: Local machine or cloud

**Option 2: Claude Code Web (Team Sharing)**
- Best for: Sharing analyses with non-technical stakeholders
- Cost: Claude.ai pro/teams subscription
- Latency: Real-time
- Hosting: Claude.ai cloud

**Option 3: Agent SDK + Custom App**
- Best for: Embedded analytics, production systems
- Cost: Claude API usage (bulk pricing available)
- Latency: Real-time with streaming
- Hosting: Your infrastructure (AWS, GCP, Azure, on-prem)

**Option 4: Scheduled Reports (GitHub Actions)**
- Best for: Daily/weekly reports, dashboards
- Cost: Claude API per execution
- Latency: Batch processing (runs on schedule)
- Hosting: GitHub Actions or other CI/CD

---

## Key Capabilities for Analytics Agents

### Data Querying
- Execute SQL against BigQuery, Snowflake, PostgreSQL
- Explore schemas and understand data quality
- Optimize queries for performance
- Handle large result sets (100K+ rows)

### Statistical Analysis
- Hypothesis testing (t-tests, chi-square, ANOVA)
- Confidence intervals and margin of error
- Correlation and regression analysis
- Time-series decomposition (trend, seasonality)

### A/B Testing
- Sample size calculation with power analysis
- Minimum detectable effect (MDE) determination
- Test duration planning
- Statistical significance assessment
- Multiple comparison corrections

### Visualization & Reporting
- Interactive dashboards (HTML/JS)
- Publication-quality charts (matplotlib/seaborn/plotly)
- PowerPoint slides
- PDF reports with formatted tables and charts

### Quality Assurance
- Data validation and anomaly detection
- Query performance monitoring
- Statistical assumption checking
- Methodology documentation

---

## Limitations & Considerations

1. **Context Window**: Large result sets consume tokens quickly
   - Solution: Stream results, use pagination, pre-aggregate

2. **Cost**: Complex agents with multiple model calls add up
   - Solution: Use Sonnet for simpler tasks, Opus only for complex analysis

3. **Data Latency**: MCP servers query live data
   - Solution: Cache results, use snapshots for large analyses

4. **Statistical Rigor**: Agents should validate assumptions
   - Solution: Implement hooks that check statistical assumptions

5. **Explainability**: Important for business decisions
   - Solution: Require agents to show raw queries, test statistics, and confidence intervals

---

## Getting Started

### Step 1: Choose Your Primary Data Source
- BigQuery (Google Cloud)
- Snowflake (cloud data warehouse)
- PostgreSQL (self-hosted)

### Step 2: Set Up MCP Server
```bash
# Example: BigQuery MCP
npm install @anthropic-ai/bigquery-mcp
claude --mcp add-stdio-server bigquery \
  --command "node ./node_modules/@anthropic-ai/bigquery-mcp/index.js"
```

### Step 3: Create Analytics Plugin
```bash
mkdir analytics-plugin
cd analytics-plugin
mkdir -p .claude-plugin/agents/skills/hooks
```

### Step 4: Define Core Agent
```markdown
agents/lead-analyst.md
---
name: lead-analyst
description: Coordinates data analysis across team
model: claude-opus-4-6
tools:
  - bigquery-mcp
  - python-execution
---

You are a senior data analyst. Coordinate analysis across team...
```

### Step 5: Test & Deploy
```bash
claude --plugin-dir ./analytics-plugin
# Test in interactive Claude Code session
```

---

## Recommended Resources

- **Claude Agent SDK**: https://platform.claude.com/docs/en/agent-sdk/quickstart.md
- **Tool Use Guide**: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview.md
- **Claude Code Plugins**: https://code.claude.com/docs/en/plugins.md
- **MCP Specification**: https://modelcontextprotocol.io/specification/2025-11-25
- **BigQuery MCP**: https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp
- **Snowflake MCP**: https://www.snowflake.com/en/blog/mcp-servers-unify-extend-data-agents/

---

Sources:
- [Anthropic Agent SDK Quickstart](https://platform.claude.com/docs/en/agent-sdk/quickstart.md)
- [Claude Tool Use Overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview.md)
- [Claude Code Plugin Documentation](https://code.claude.com/docs/en/plugins.md)
- [Claude Code MCP Guide](https://code.claude.com/docs/en/mcp.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol)
- [Model Context Protocol Donation](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)
- [BigQuery MCP Server Documentation](https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp)
- [Google Cloud BigQuery Connector](https://claude.com/connectors/bigquery)
- [Integrating BigQuery with Claude](https://cloud.google.com/blog/products/data-analytics/integrating-bigquery-with-anthropics-claude)
- [BigQuery via CData Connect AI](https://www.cdata.com/kb/tech/bigquery-cloud-claude-agent-sdk.rst)
- [Snowflake via CData Connect AI](https://www.cdata.com/kb/tech/snowflake-cloud-claude-agent-sdk.rst)
- [Snowflake MCP Servers & Data Agents](https://www.snowflake.com/en/blog/mcp-servers-unify-extend-data-agents/)
- [Using Fully Managed BigQuery MCP Server](https://cloud.google.com/blog/products/data-analytics/using-the-fully-managed-remote-bigquery-mcp-server-to-build-data-ai-agents)
- [Announcing Official MCP Support for Google Services](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services)
- [Claude Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic Engineering: Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

[TOOL RESULT - toolu_01PhSyPCvexBnoTLAXnADWQ2]
agentId: a0bb373 (for resuming to continue this agent's work if needed)
<usage>total_tokens: 58342
tool_uses: 9
duration_ms: 107044</usage>

====================================================================================================
[ASSISTANT] Line 8
====================================================================================================
[THINKING]
Now I have comprehensive research. Let me synthesize this into a clear, actionable plan for Daniel about building a Bit2Me lifecycle analytics agent with A/B testing capabilities.

Looking at the screenshots he shared:
- They show an analytics tool called "Poly" built by a colleague for brokerage
- It has natural language querying ("Ask Poly anything...")
- It connects to BigQuery data
- It has a Data Explorer with schema documentation
- Shows tables for funding & wallets data

What Daniel wants for Bit2Me lifecycle:
- A/B test dashboard and analysis
- Analyze product data, user clusters, retention, activation, countries


- Connect to Qlik, CleverTap, and Bitquery for business intelligence, user engagement tracking, and on-chain crypto data respectively

The strategy is to build a Cowork plugin that uses MCP servers to integrate these data sources, then design specialized agents to handle different analytical tasks.

For Bit2Me, I can leverage the REST APIs from CleverTap and Qlik, plus Bitquery's GraphQL endpoint, to create a natural language interface similar to what "Poly" does for BigQuery—but tailored for lifecycle management and A/B testing across multiple platforms.

====================================================================================================
[ASSISTANT] Line 9
====================================================================================================
Great research. Now let me give you a clear picture of what this would look like and how to build it.

====================================================================================================
[ASSISTANT] Line 10
====================================================================================================
[TOOL CALL: TodoWrite]
{
  "todos": [
    {
      "content": "Research Anthropic tools and architecture options",
      "status": "completed",
      "activeForm": "Researching Anthropic tools and architecture options"
    },
    {
      "content": "Design the Bit2Me lifecycle agent architecture",
      "status": "in_progress",
      "activeForm": "Designing the Bit2Me lifecycle agent architecture"
    },
    {
      "content": "Create a detailed technical blueprint document",
      "status": "pending",
      "activeForm": "Creating a detailed technical blueprint document"
    }
  ]
}

====================================================================================================
[ASSISTANT] Line 12
====================================================================================================
Here's the full picture.

**What you saw in Poly is exactly the model.** It's a natural language interface sitting on top of BigQuery data. Claude reads the schema, understands the tables, and lets anyone query in plain English. What you want is the same pattern, but purpose-built for lifecycle and A/B testing, and connected to three data sources: Qlik, CleverTap, and Bitquery.

**The core building blocks are:**

**1. MCP Servers (the data bridges).** Anthropic's Model Context Protocol is the standard way to connect Claude to external systems. For each of your data sources, you'd need an MCP server. Think of it as a plugin that teaches Claude how to talk to that system. CleverTap has a REST API. Qlik has its Engine API. Bitquery uses GraphQL. Each becomes an MCP server that Claude can query in real time. There's no MCP server for Qlik or CleverTap yet, so someone would need to build them. For Bitquery there are community ones starting to appear.

**2. A Cowork Plugin (the agent itself).** Since you're using Cowork, you'd package everything as a Cowork plugin. Inside it you'd define specialized agents: one that handles data exploration and queries, one that designs A/B tests with proper statistical rigor (sample sizes, power analysis, minimum detectable effect), one that interprets lifecycle data (retention curves, activation funnels, cluster behavior by country), and a lead agent that coordinates everything.

**3. Skills (the specialized behaviors).** These are instruction sets that teach the agent how to do specific things well. For example, a "design A/B test" skill that forces the agent to always calculate sample size, define guardrail metrics, and specify test duration before running anything.

**What it would look like in practice:**

You open Cowork and type: "Analyze retention for users in Spain who went through the crypto purchase flow last month and suggest where to run an A/B test." The agent queries CleverTap for lifecycle events, pulls user cluster data from your internal database, checks Bitquery for on-chain behavior, and returns a full analysis with a proposed test design, sample size, and expected duration to reach significance.

**The data sources you mentioned and how they connect:**

Qlik is your BI layer, likely sitting on top of your internal database. The cleanest approach is to bypass Qlik and connect directly to the underlying database (BigQuery, Snowflake, or Postgres depending on your stack), then use Qlik only as a reference for which tables matter. CleverTap is the most important one for lifecycle since it holds your event data, funnels, and segments. It has a good API. Bitquery gives you on-chain data which is critical for a crypto product. You can query wallet behavior, transaction patterns, and chain activity.

**What you need to provide to get started:**

Before building anything, the key questions are: where does your core user and event data live (BigQuery? Postgres? directly in CleverTap?)? Do you have a data analyst or engineer who can build the MCP servers? And what are the top 5 questions your lifecycle team asks most often? Those become the first skills.

**The honest assessment of complexity:**

The conversational layer (the agent itself) is the easy part. Anthropic handles all of that. The hard part is the data plumbing: building reliable MCP servers for CleverTap and Qlik, cleaning up your schema documentation so Claude can navigate your tables, and deciding which source is the truth for each metric. That's 80% of the work.

If you can connect me to the data (share schemas, API docs, or sample exports), I can start designing the agent architecture in detail, write the skill definitions, and help spec out the MCP servers. What does your current data setup look like?

====================================================================================================
[ASSISTANT] Line 13
====================================================================================================
[TOOL CALL: TodoWrite]
{
  "todos": [
    {
      "content": "Research Anthropic tools and architecture options",
      "status": "completed",
      "activeForm": "Researching Anthropic tools and architecture options"
    },
    {
      "content": "Design the Bit2Me lifecycle agent architecture",
      "status": "completed",
      "activeForm": "Designing the Bit2Me lifecycle agent architecture"
    },
    {
      "content": "Create a detailed technical blueprint document",
      "status": "pending",
      "activeForm": "Creating a detailed technical blueprint document"
    }
  ]
}