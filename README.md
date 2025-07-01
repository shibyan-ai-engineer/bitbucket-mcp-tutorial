# Bitbucket MCP Server Tutorial

A comprehensive tutorial for building a **Model Context Protocol (MCP) server** that connects AI assistants like Claude Desktop and Cursor to Bitbucket repositories for intelligent code review and repository management.

## 🎯 What You'll Learn

- **MCP Fundamentals**: Understand the Model Context Protocol and how it connects AI assistants to external tools
- **Server Development**: Build a production-ready MCP server using FastMCP framework
- **API Integration**: Connect to Bitbucket's REST API for repository operations
- **AI Assistant Integration**: Configure Claude Desktop and Cursor to use your MCP server

## 🚀 What This Server Does

This MCP server provides **11 powerful tools** and **4 data resources** that enable AI assistants to:

### 🔧 Repository Management
- List and explore Bitbucket repositories
- Get detailed repository information and metadata
- Access repository data through MCP resources

### 🔀 Pull Request Operations  
- List, review, and analyze pull requests
- Get detailed PR information and code diffs
- Manage PR workflows (approve, merge, decline)
- Add comments and participate in code reviews

### 💬 Code Review Features
- View and analyze code changes
- Add inline and general comments
- Participate in collaborative code review processes

## 📋 Prerequisites

- **Python 3.8+** (Python 3.9+ recommended)
- **Bitbucket Account** with API access
- **Basic Python Knowledge** (variables, functions, async/await)
- **Code Editor** (VS Code, Cursor, or similar)

## 🏗️ Project Structure (Tutorial-Ready)

```
bitbucket-mcp-tutorial/
├── README.md                    # This comprehensive guide
├── LICENSE                     # MIT license
├── mcp_server.py               # Main MCP server (simplified & commented)
├── bitbucket_client.py         # Bitbucket API client
├── test_mcp_server.py          # Test script to verify functionality
├── config_helper.py            # Helper for generating configurations
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── docs/
    └── ARCHITECTURE.md         # System design and data flow
```

## ⚡ Quick Start (5 Minutes)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd bitbucket-mcp-tutorial
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your Bitbucket credentials
```

### 3. Test the Server
```bash
python test_mcp_server.py --quick
```

### 4. Configure AI Assistants
```bash
python config_helper.py
```

## 🔧 Detailed Setup Guide

### Step 1: Python Environment Setup

**Option A: Using pip (Recommended for beginners)**
```bash
# Create project directory
mkdir bitbucket-mcp-tutorial
cd bitbucket-mcp-tutorial

# Install dependencies
pip install -r requirements.txt
```

**Option B: Using virtual environment (Recommended for production)**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Bitbucket API Configuration

1. **Create App Password**:
   - Go to Bitbucket → Settings → Personal settings → App passwords
   - Create new app password with: Repositories (Read, Write), Pull requests (Read, Write)
   - Save the generated password securely

2. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file:
   ```env
   BITBUCKET_WORKSPACE=your-workspace-name
   BITBUCKET_USERNAME=your-username
   BITBUCKET_APP_PASSWORD=your-app-password
   ```

### Step 3: Test Your Setup

**Quick Test** (30 seconds):
```bash
python test_mcp_server.py --quick
```

**Full Test** (2 minutes):
```bash
python test_mcp_server.py
```

Expected output:
```
✅ Successfully imported Bitbucket MCP server
✅ Connected successfully!
🔧 Available Tools (11): [list of all tools]
📂 Available Resources (4): [list of all resources]
✅ All tests completed successfully!
```

### Step 4: Configure AI Assistants

**For Claude Desktop**:
```bash
python config_helper.py --claude
```

**For Cursor**:
```bash
python config_helper.py --cursor
```

**Manual Configuration**:
The config helper will show you exactly what to add to your AI assistant's configuration files.

## 🎓 Understanding the Code

### Core Components

**1. MCP Server (`mcp_server.py`)**
- FastMCP framework setup
- 11 tools for Bitbucket operations
- 4 resources for data access
- Error handling and logging

**2. Bitbucket Client (`bitbucket_client.py`)**
- HTTP client for Bitbucket API
- Authentication handling
- Request/response processing

**3. Test Script (`test_mcp_server.py`)**
- Comprehensive functionality testing
- Performance benchmarking
- Integration verification

### Key Tools Explained

```python
# Tool 1: List Repositories
@mcp.tool
async def list_repositories(role: str = "member"):
    """List repositories by user role"""
    # Implementation details...

# Tool 2: Get Repository Info  
@mcp.tool
async def get_repository_info(repo_slug: str):
    """Get detailed repository information"""
    # Implementation details...

# Tool 3: List Pull Requests
@mcp.tool
async def list_pull_requests(repo_slug: str, state: str = "OPEN"):
    """List pull requests with filtering"""
    # Implementation details...
```

### Resources Explained

```python
# Resource 1: Repositories List
@mcp.resource("bitbucket://repositories")
async def get_repositories_resource():
    """Provide access to repositories data"""
    # Implementation details...

# Resource 2: Specific Repository
@mcp.resource("bitbucket://repo/{repo_slug}")
async def get_repository_resource(repo_slug: str):
    """Provide access to specific repository data"""
    # Implementation details...
```

## 🔗 Integration with AI Assistants

### Claude Desktop Integration

After running `python config_helper.py --claude`, add the generated configuration to:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`

Example configuration:
```json
{
  "mcpServers": {
    "bitbucket": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"],
      "env": {
        "BITBUCKET_WORKSPACE": "your-workspace",
        "BITBUCKET_USERNAME": "your-username", 
        "BITBUCKET_APP_PASSWORD": "your-app-password"
      }
    }
  }
}
```

### Cursor Integration

After running `python config_helper.py --cursor`, add the generated configuration to Cursor settings.

## 📊 Architectural Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │    │   MCP Server     │    │   Bitbucket     │
│                 │    │                  │    │                 │
│  Claude Desktop │◄──►│  11 Tools        │◄──►│  REST API       │
│     Cursor      │    │  4 Resources     │    │  Repositories   │
│                 │    │  FastMCP         │    │  Pull Requests  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Data Flow

1. **User Request**: "Review the latest PR in my repository"
2. **AI Assistant**: Parses request and calls MCP tools
3. **MCP Server**: Processes tool calls using Bitbucket API
4. **Bitbucket API**: Returns repository and PR data
5. **MCP Server**: Formats response for AI assistant
6. **AI Assistant**: Presents intelligent analysis to user

## 🛠️ Available Tools & Resources

### 🔧 Tools (11 total)

| Tool | Purpose | Parameters |
|------|---------|------------|
| `list_repositories` | List user repositories | `role` (admin/member/contributor) |
| `get_repository_info` | Get repo details | `repo_slug` |
| `list_pull_requests` | List PRs | `repo_slug`, `state` |
| `get_pull_request_info` | Get PR details | `repo_slug`, `pr_id` |
| `get_pull_request_diff` | Get PR code diff | `repo_slug`, `pr_id` |
| `add_pr_comment` | Add PR comment | `repo_slug`, `pr_id`, `content` |
| `approve_pr` | Approve PR | `repo_slug`, `pr_id` |
| `unapprove_pr` | Remove approval | `repo_slug`, `pr_id` |
| `merge_pr` | Merge PR | `repo_slug`, `pr_id`, `merge_strategy` |
| `decline_pr` | Decline PR | `repo_slug`, `pr_id`, `reason` |
| `get_pr_comments` | Get PR comments | `repo_slug`, `pr_id` |

### 📂 Resources (4 total)

| Resource | URI Pattern | Purpose |
|----------|-------------|---------|
| Repositories | `bitbucket://repositories` | List all repositories |
| Repository | `bitbucket://repo/{repo_slug}` | Specific repository data |
| Pull Requests | `bitbucket://repo/{repo_slug}/pullrequests` | Repository's PRs |
| PR Comments | `bitbucket://pr/{repo_slug}/{pr_id}/comments` | PR comments |

## 🎪 Live Demo Usage Examples

### Example 1: Repository Exploration
```
User: "What repositories do I have access to?"
AI: Uses list_repositories → Shows repository list with descriptions
```

### Example 2: Pull Request Review
```
User: "Review the latest PR in my-repo"
AI: Uses list_pull_requests + get_pull_request_diff → Analyzes code changes
```

### Example 3: Code Review Workflow
```
User: "Add a comment to PR #15 suggesting optimization"
AI: Uses add_pr_comment → Adds intelligent code review comment
```

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Error: ModuleNotFoundError: No module named 'fastmcp'
# Solution: Install dependencies
pip install -r requirements.txt
```

**2. Authentication Errors**
```bash
# Error: Unauthorized (401)
# Solution: Check .env file configuration
python config_helper.py --test-auth
```

**3. Server Connection Issues**
```bash
# Error: Connection refused
# Solution: Test server locally first
python test_mcp_server.py --quick
```

### Debug Mode

Run with debug logging:
```bash
FASTMCP_DEBUG=1 python mcp_server.py
```

Run tests with verbose output:
```bash
python test_mcp_server.py --verbose
```

## 📚 Learning Resources

### Next Steps
1. **Explore the Code**: Read through `mcp_server.py` with educational comments
2. **Try Live Examples**: Use your configured AI assistant to interact with repositories
3. **Extend Functionality**: Add new tools for issues, branches, or commits
4. **Build Your Own**: Create MCP servers for other APIs (GitHub, GitLab, etc.)

### Additional Documentation
- `docs/ARCHITECTURE.md` - Detailed system design and technical overview

### External Resources
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://fastmcp.ai/)
- [Bitbucket REST API Reference](https://developer.atlassian.com/cloud/bitbucket/rest/)

## 🤝 Contributing

This tutorial project welcomes improvements! Areas for contribution:
- Additional Bitbucket API integrations
- Enhanced error handling
- More comprehensive tests
- Documentation improvements
- Example use cases

## 📄 License

MIT License - Feel free to use this tutorial for learning and teaching!

---

**🎯 Ready to start building? Run `python test_mcp_server.py --quick` to verify everything works!**
