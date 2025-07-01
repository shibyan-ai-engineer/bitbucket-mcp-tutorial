# Bitbucket MCP Server Architecture

A detailed technical overview of the Bitbucket MCP server architecture, data flow, and design decisions.

## 🏗️ System Overview

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│                     │    │                      │    │                     │
│   AI Assistants     │    │   MCP Server         │    │   Bitbucket API     │
│                     │    │                      │    │                     │
│  ┌─────────────────┐│    │  ┌─────────────────┐ │    │  ┌─────────────────┐│
│  │ Claude Desktop  ││◄──►│  │ FastMCP         │ │◄──►│  │ REST API        ││
│  └─────────────────┘│    │  │ Framework       │ │    │  │ v2.0            ││
│  ┌─────────────────┐│    │  └─────────────────┘ │    │  └─────────────────┘│
│  │ Cursor          ││    │  ┌─────────────────┐ │    │  ┌─────────────────┐│
│  └─────────────────┘│    │  │ 11 Tools        │ │    │  │ Repositories    ││
│  ┌─────────────────┐│    │  │ 4 Resources     │ │    │  │ Pull Requests   ││
│  │ Other MCP       ││    │  │ Client Manager  │ │    │  │ Comments        ││
│  │ Clients         ││    │  └─────────────────┘ │    │  └─────────────────┘│
│  └─────────────────┘│    │                      │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
```

## 🔄 Data Flow Architecture

### 1. Request Flow
```
User Query → AI Assistant → MCP Protocol → FastMCP → Tool/Resource → Bitbucket API → Response
```

### 2. Detailed Flow Diagram
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   User      │    │ AI Assistant│    │ MCP Server  │    │ Bitbucket   │    │ Response    │
│   Query     │    │ Processing  │    │ Processing  │    │ API Call    │    │ Handling    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │                   │                   │
       │ "Review PR #15"   │                   │                   │                   │
       ├──────────────────►│                   │                   │                   │
       │                   │ Parse & Plan      │                   │                   │
       │                   │ Tool Selection    │                   │                   │
       │                   ├──────────────────►│                   │                   │
       │                   │ get_pr_info(15)   │                   │                   │
       │                   │                   │ HTTP GET          │                   │
       │                   │                   ├──────────────────►│                   │
       │                   │                   │ PR Data           │                   │
       │                   │                   │◄──────────────────┤                   │
       │                   │                   │ get_pr_diff(15)   │                   │
       │                   │                   ├──────────────────►│                   │
       │                   │                   │ Diff Data         │                   │
       │                   │                   │◄──────────────────┤                   │
       │                   │ Structured Data   │                   │                   │
       │                   │◄──────────────────┤                   │                   │
       │ Intelligent       │                   │                   │                   │
       │ Analysis          │                   │                   │                   │
       │◄──────────────────┤                   │                   │                   │
```

## 🧩 Component Architecture

### Core Components

#### 1. FastMCP Server (`mcp_server.py`)
- **Purpose**: Main MCP protocol handler and tool/resource coordinator
- **Responsibilities**:
  - Handle MCP protocol communication
  - Route tool calls to appropriate functions
  - Manage resource access
  - Coordinate with Bitbucket client
  - Error handling and logging

#### 2. Bitbucket Client (`bitbucket_client.py`)
- **Purpose**: HTTP client for Bitbucket REST API
- **Responsibilities**:
  - Authenticate with Bitbucket API
  - Make HTTP requests with proper headers
  - Handle response parsing
  - Manage connection pooling
  - URL encoding and parameter handling

#### 3. Test Script (`test_mcp_server.py`)
- **Purpose**: Comprehensive functionality testing
- **Responsibilities**:
  - Verify tool functionality
  - Test resource access
  - Performance benchmarking
  - Integration validation

#### 4. Configuration Helper (`config_helper.py`)
- **Purpose**: Generate AI assistant configurations
- **Responsibilities**:
  - Create Claude Desktop configs
  - Generate Cursor settings
  - Validate environment setup

## 🛠️ Tool Architecture

### Tool Categories

#### Repository Tools
```
list_repositories()
├── Parameters: role (admin/contributor/member)
├── Returns: Array of repository objects
└── Use Case: Repository discovery and listing

get_repository_info(repo_slug)
├── Parameters: repo_slug (repository identifier)
├── Returns: Detailed repository object
└── Use Case: Deep repository analysis
```

#### Pull Request Tools
```
list_pull_requests(repo_slug, state)
├── Parameters: repo_slug, state (OPEN/MERGED/DECLINED)
├── Returns: Array of PR objects
└── Use Case: PR discovery and filtering

get_pull_request_info(repo_slug, pr_id)
├── Parameters: repo_slug, pr_id
├── Returns: Detailed PR object
└── Use Case: PR analysis and review

get_pull_request_diff(repo_slug, pr_id)
├── Parameters: repo_slug, pr_id
├── Returns: Raw diff content
└── Use Case: Code change analysis
```

#### Code Review Tools
```
add_pr_comment(repo_slug, pr_id, content, file_path?, line_number?)
├── Parameters: repo_slug, pr_id, content, optional file/line
├── Returns: Created comment object
└── Use Case: Code review feedback

approve_pr(repo_slug, pr_id)
├── Parameters: repo_slug, pr_id
├── Returns: Approval confirmation
└── Use Case: PR approval workflow

merge_pr(repo_slug, pr_id, strategy?, close_branch?, message?)
├── Parameters: repo_slug, pr_id, optional merge config
├── Returns: Merge result
└── Use Case: PR merge execution
```

### Tool Design Patterns

#### 1. Consistent Error Handling
```python
async def tool_function():
    try:
        client = get_client()
        result = await client.api_call()
        return formatted_result
    except Exception as e:
        raise ToolError(f"Operation failed: {str(e)}")
```

#### 2. Parameter Validation
```python
async def tool_function(repo_slug: str, optional_param: str = "default"):
    # Validate required parameters
    if not repo_slug:
        raise ToolError("repo_slug is required")
    # Process with defaults
```

#### 3. Response Formatting
```python
# Consistent response structure
return {
    "id": item["id"],
    "name": item["name"],
    "metadata": {...},
    "timestamps": {...}
}
```

## 📂 Resource Architecture

### Resource Types

#### 1. Repository List Resource
```
URI: bitbucket://repositories
Purpose: Provide searchable repository data
Format: JSON with repository array
Usage: AI can analyze all repositories at once
```

#### 2. Specific Repository Resource
```
URI: bitbucket://repo/{repo_slug}
Purpose: Detailed repository information
Format: JSON with full repository object
Usage: Deep repository analysis
```

#### 3. Pull Requests Resource
```
URI: bitbucket://repo/{repo_slug}/pullrequests
Purpose: All PRs for a repository
Format: JSON with PR array
Usage: PR trend analysis, bulk operations
```

#### 4. PR Comments Resource
```
URI: bitbucket://pr/{repo_slug}/{pr_id}/comments
Purpose: All comments for a specific PR
Format: JSON with comment thread
Usage: Code review analysis, discussion context
```

### Resource Design Patterns

#### 1. URI-based Addressing
```python
@mcp.resource("bitbucket://repo/{repo_slug}")
async def get_repository_resource(repo_slug: str):
    # Dynamic URI parameters
```

#### 2. Structured Data Format
```python
return {
    "uri": "bitbucket://repositories",
    "name": "Human-readable name",
    "description": "What this resource provides",
    "mimeType": "application/json",
    "data": {...}  # Actual data payload
}
```

## 🔐 Authentication Architecture

### Authentication Flow
```
Environment Variables → BasicAuth → httpx Client → Bitbucket API
```

### Security Considerations
- **App Passwords**: More secure than account passwords
- **Scoped Permissions**: Only request necessary permissions
- **Environment Variables**: Keep credentials out of code
- **Client Management**: Reuse connections efficiently

### Implementation
```python
class BitbucketClient:
    def __init__(self, username: str, app_password: str, workspace: str):
        self.client = httpx.AsyncClient(auth=(username, app_password))
```

## ⚡ Performance Architecture

### Optimization Strategies

#### 1. Connection Pooling
- Single httpx client for all requests
- Automatic connection reuse
- Proper client lifecycle management

#### 2. Async Operations
- Non-blocking API calls
- Concurrent request handling
- Efficient resource utilization

#### 3. Error Recovery
- Graceful degradation
- Meaningful error messages
- Retry strategies (future enhancement)

### Performance Characteristics
```
Typical Response Times:
├── Repository List: 200-500ms
├── PR Information: 300-700ms
├── PR Diff: 500-1500ms (depends on size)
└── Comments: 200-600ms
```

## 🔄 Integration Architecture

### MCP Client Integration
```
AI Assistant ← MCP Protocol → FastMCP Server → Bitbucket Client → API
```

### Configuration Architecture
```
Claude Desktop Config:
{
  "mcpServers": {
    "bitbucket": {
      "command": "python",
      "args": ["path/to/mcp_server.py"],
      "env": {...}
    }
  }
}
```

### Process Architecture
```
AI Assistant Process ← stdio/sse → MCP Server Process → HTTP → Bitbucket API
```

## 🎯 Design Decisions

### 1. FastMCP Framework Choice
- **Pro**: Handles MCP protocol complexity
- **Pro**: Simple decorator-based API
- **Pro**: Built-in error handling
- **Con**: Framework dependency

### 2. Async/Await Pattern
- **Pro**: Non-blocking operations
- **Pro**: Better performance under load
- **Pro**: Modern Python best practice
- **Con**: Slightly more complex for beginners

### 3. Single Client Instance
- **Pro**: Connection reuse and efficiency
- **Pro**: Simplified state management
- **Con**: Global state (acceptable for this use case)

### 4. Structured Tool Responses
- **Pro**: Consistent AI parsing
- **Pro**: Rich metadata for AI analysis
- **Con**: Slightly more verbose than raw API responses

## 📈 Scalability Considerations

### Current Architecture Limits
- Single workspace per server instance
- Synchronous tool execution
- Limited connection pooling

### Future Enhancements
- Multi-workspace support
- Tool execution parallelization
- Advanced caching strategies
- Rate limiting and quotas

## 🧪 Testing Architecture

### Test Categories
1. **Unit Tests**: Individual tool functionality
2. **Integration Tests**: Full API communication
3. **Performance Tests**: Response time benchmarks
4. **Configuration Tests**: AI assistant integration

### Test Structure
```
test_mcp_server.py
├── Connection Testing
├── Tool Functionality Testing
├── Resource Access Testing
├── Performance Benchmarking
└── Error Handling Validation
```

## 🔧 Development Workflow

### 1. Local Development
```bash
python test_mcp_server.py --quick  # Fast verification
python test_mcp_server.py          # Full test suite
```

### 2. AI Assistant Testing
```bash
python config_helper.py --claude    # Generate config
# Test with real AI assistant
```

### 3. Production Deployment
- Environment variable validation
- Performance monitoring
- Error logging and alerting

---

**🎯 This architecture provides a solid foundation for MCP server development while maintaining simplicity for educational purposes.**
