"""
Bitbucket MCP Server - Tutorial Edition

A Model Context Protocol (MCP) server that provides tools and resources for interacting
with Bitbucket repositories, pull requests, and code review workflows.

🎯 TUTORIAL GOALS:
This server demonstrates how to:
1. Build an MCP server using the FastMCP framework
2. Create tools that external AI assistants can use
3. Integrate with REST APIs (Bitbucket API)
4. Handle authentication and error management
5. Provide both tools (actions) and resources (data access)

🔧 WHAT THIS SERVER PROVIDES:
- 11 Tools: For repository and pull request management
- 4 Resources: For accessing repository data
- Integration: Works with Claude Desktop, Cursor, and other MCP clients

🚀 AI ASSISTANT CAPABILITIES:
This server enables AI assistants like Cursor to:
- Browse repositories and their details
- List and review pull requests
- Access code diffs and file contents
- Manage code review workflows (approve, comment, merge)
- Participate in collaborative development processes

📚 LEARNING NOTES:
- Tools (@mcp.tool): Functions that AI can call to perform actions
- Resources (@mcp.resource): Data that AI can read and analyze
- FastMCP: Framework that handles MCP protocol details
- Async/Await: Required for handling concurrent API requests
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from dotenv import load_dotenv

# Import our Bitbucket API client
# (This file should be in the same directory as this server)
from bitbucket_client import BitbucketClient, create_client_from_env

# Load environment variables from .env file
# This is where we get Bitbucket credentials (workspace, username, app password)
load_dotenv()

# 🚀 CREATE THE MCP SERVER
# FastMCP handles all the protocol details - we just define tools and resources!
mcp = FastMCP(
    name="Bitbucket MCP Server",
    instructions="""
    This server provides access to Bitbucket repositories and pull requests.
    
    Use the repository tools to browse and analyze repositories.
    Use the pull request tools to review code changes and manage PR workflows.
    Use the resources to access repository data, PR details, and code diffs.
    
    Perfect for AI-assisted code review and repository management!
    """
)

# 🔧 GLOBAL CLIENT MANAGEMENT
# We maintain one Bitbucket API client for all operations
# This is more efficient than creating a new client for each request
_bitbucket_client: Optional[BitbucketClient] = None


def get_client() -> BitbucketClient:
    """
    Get the global Bitbucket client instance
    
    🎓 TUTORIAL NOTE: This pattern ensures we have one authenticated
    client that all our tools can use. It handles connection pooling
    and authentication automatically.
    """
    if _bitbucket_client is None:
        raise ToolError("Bitbucket client not initialized. Check your environment variables.")
    return _bitbucket_client


# =============================================================================
# 🛠️ MCP TOOLS - REPOSITORY OPERATIONS
# =============================================================================
# 🎓 TUTORIAL: Tools are functions that AI assistants can call to perform actions
# Each tool is decorated with @mcp.tool and becomes available to the AI

@mcp.tool
async def list_repositories(
    role: str = "member",
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    List repositories in the configured Bitbucket workspace.
    
    🎓 TUTORIAL NOTE: This is our first MCP tool! It demonstrates:
    - How to use @mcp.tool decorator to expose functions to AI
    - Parameter handling (role filter)
    - Async operations for API calls
    - Proper error handling with try/except
    
    Args:
        role: Filter by role (admin, contributor, member). Default: member
    
    Returns:
        List of repository information including name, description, and metadata
    """
    if ctx:
        await ctx.info(f"Fetching repositories with role: {role}")
    
    try:
        client = get_client()
        repositories = await client.list_repositories(role=role)
        
        # Convert to dictionaries for JSON serialization
        result = []
        for repo in repositories:
            result.append({
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "No description",
                "is_private": repo.is_private,
                "language": repo.language or "Unknown",
                "size": repo.size,
                "created_on": repo.created_on,
                "updated_on": repo.updated_on,
                "has_issues": repo.has_issues,
                "has_wiki": repo.has_wiki,
                "clone_urls": repo.clone_links
            })
        
        if ctx:
            await ctx.info(f"Found {len(result)} repositories")
        
        return result
    
    except Exception as e:
        error_msg = f"Failed to list repositories: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.tool
async def get_repository_info(
    repo_slug: str,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific repository.
    
    Args:
        repo_slug: The repository slug (name)
    
    Returns:
        Detailed repository information
    """
    if ctx:
        await ctx.info(f"Fetching details for repository: {repo_slug}")
    
    try:
        client = get_client()
        repo = await client.get_repository(repo_slug)
        
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description or "No description",
            "is_private": repo.is_private,
            "language": repo.language or "Unknown",
            "size": repo.size,
            "created_on": repo.created_on,
            "updated_on": repo.updated_on,
            "has_issues": repo.has_issues,
            "has_wiki": repo.has_wiki,
            "clone_urls": repo.clone_links
        }
    
    except Exception as e:
        error_msg = f"Failed to get repository info for '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


# =============================================================================
# PULL REQUEST TOOLS
# =============================================================================

@mcp.tool
async def list_pull_requests(
    repo_slug: str,
    state: str = "OPEN",
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    List pull requests for a repository.
    
    Args:
        repo_slug: The repository slug (name)
        state: PR state filter (OPEN, MERGED, DECLINED, SUPERSEDED). Default: OPEN
    
    Returns:
        List of pull request information
    """
    if ctx:
        await ctx.info(f"Fetching {state} pull requests for {repo_slug}")
    
    try:
        client = get_client()
        pull_requests = await client.list_pull_requests(repo_slug, state)
        
        # Convert to dictionaries for JSON serialization
        result = []
        for pr in pull_requests:
            result.append({
                "id": pr.id,
                "title": pr.title,
                "description": pr.description or "No description",
                "state": pr.state,
                "author": pr.author,
                "source_branch": pr.source_branch,
                "destination_branch": pr.destination_branch,
                "created_on": pr.created_on,
                "updated_on": pr.updated_on,
                "comment_count": pr.comment_count,
                "task_count": pr.task_count,
                "approval_count": pr.approval_count
            })
        
        if ctx:
            await ctx.info(f"Found {len(result)} {state.lower()} pull requests")
        
        return result
    
    except Exception as e:
        error_msg = f"Failed to list pull requests for '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.tool
async def get_pull_request_info(
    repo_slug: str,
    pr_id: int,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Get detailed information about a specific pull request.
    
    Args:
        repo_slug: The repository slug (name)
        pr_id: The pull request ID number
    
    Returns:
        Detailed pull request information
    """
    if ctx:
        await ctx.info(f"Fetching details for PR #{pr_id} in {repo_slug}")
    
    try:
        client = get_client()
        pr = await client.get_pull_request(repo_slug, pr_id)
        
        return {
            "id": pr.id,
            "title": pr.title,
            "description": pr.description or "No description",
            "state": pr.state,
            "author": pr.author,
            "source_branch": pr.source_branch,
            "destination_branch": pr.destination_branch,
            "created_on": pr.created_on,
            "updated_on": pr.updated_on,
            "comment_count": pr.comment_count,
            "task_count": pr.task_count,
            "approval_count": pr.approval_count
        }
    
    except Exception as e:
        error_msg = f"Failed to get PR info for #{pr_id} in '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.tool
async def get_pull_request_diff(
    repo_slug: str,
    pr_id: int,
    ctx: Context = None
) -> str:
    """
    Get the code diff for a pull request.
    
    This is essential for code review - it shows exactly what changes
    are being proposed in the pull request.
    
    Args:
        repo_slug: The repository slug (name)
        pr_id: The pull request ID number
    
    Returns:
        The raw diff content showing all changes in the PR
    """
    if ctx:
        await ctx.info(f"Fetching diff for PR #{pr_id} in {repo_slug}")
    
    try:
        client = get_client()
        diff = await client.get_pull_request_diff(repo_slug, pr_id)
        
        if ctx:
            await ctx.info(f"Retrieved diff with {len(diff.splitlines())} lines")
        
        return diff
    
    except Exception as e:
        error_msg = f"Failed to get diff for PR #{pr_id} in '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


# =============================================================================
# PR MANAGEMENT TOOLS - Actions for managing pull requests
# =============================================================================

@mcp.tool
async def add_pr_comment(
    repo_slug: str,
    pr_id: int,
    content: str,
    file_path: str = None,
    line_number: int = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Add a comment to a pull request.
    
    This tool is essential for code review workflows - it allows you to provide
    feedback, ask questions, or suggest improvements on pull requests.
    
    Args:
        repo_slug: The repository slug (name)
        pr_id: The pull request ID number
        content: Comment content (supports Markdown formatting)
        file_path: Optional file path for inline comments
        line_number: Optional line number for inline comments (requires file_path)
    
    Returns:
        Information about the created comment
    """
    if ctx:
        inline_msg = f" (inline on {file_path}:{line_number})" if file_path and line_number else ""
        await ctx.info(f"Adding comment to PR #{pr_id} in {repo_slug}{inline_msg}")
    
    try:
        client = get_client()
        
        # Prepare inline comment data if file path and line number are provided
        inline = None
        if file_path and line_number:
            inline = {
                "path": file_path,
                "to": line_number
            }
        
        result = await client.add_pull_request_comment(repo_slug, pr_id, content, inline)
        
        if ctx:
            await ctx.info("Comment added successfully")
        
        return {
            "id": result.get("id"),
            "content": content,
            "created_on": result.get("created_on"),
            "author": result.get("user", {}).get("display_name", "Unknown"),
            "inline": inline is not None
        }
    
    except Exception as e:
        error_msg = f"Failed to add comment to PR #{pr_id} in '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.tool
async def approve_pr(
    repo_slug: str,
    pr_id: int,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Approve a pull request.
    
    This indicates that you have reviewed the code and approve the changes
    for merging into the target branch.
    
    Args:
        repo_slug: The repository slug (name)
        pr_id: The pull request ID number
    
    Returns:
        Information about the approval
    """
    if ctx:
        await ctx.info(f"Approving PR #{pr_id} in {repo_slug}")
    
    try:
        client = get_client()
        result = await client.approve_pull_request(repo_slug, pr_id)
        
        if ctx:
            await ctx.info("Pull request approved successfully")
        
        return {
            "approved": True,
            "approved_on": result.get("date"),
            "approver": result.get("user", {}).get("display_name", "Unknown")
        }
    
    except Exception as e:
        error_msg = f"Failed to approve PR #{pr_id} in '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.tool
async def unapprove_pr(
    repo_slug: str,
    pr_id: int,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Remove approval from a pull request.
    
    This removes your previous approval of the pull request.
    
    Args:
        repo_slug: The repository slug (name)
        pr_id: The pull request ID number
    
    Returns:
        Confirmation of approval removal
    """
    if ctx:
        await ctx.info(f"Removing approval from PR #{pr_id} in {repo_slug}")
    
    try:
        client = get_client()
        await client.unapprove_pull_request(repo_slug, pr_id)
        
        if ctx:
            await ctx.info("Approval removed successfully")
        
        return {
            "approved": False,
            "message": "Approval removed"
        }
    
    except Exception as e:
        error_msg = f"Failed to remove approval for PR #{pr_id} in '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.tool
async def merge_pr(
    repo_slug: str,
    pr_id: int,
    merge_strategy: str = "merge_commit",
    close_source_branch: bool = False,
    message: str = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Merge a pull request.
    
    This merges the approved changes into the destination branch.
    Use with caution as this action cannot be easily undone.
    
    Args:
        repo_slug: The repository slug (name)
        pr_id: The pull request ID number
        merge_strategy: Merge strategy ('merge_commit', 'squash', 'fast_forward')
        close_source_branch: Whether to close the source branch after merge
        message: Optional custom merge commit message
    
    Returns:
        Information about the merge result
    """
    if ctx:
        await ctx.info(f"Merging PR #{pr_id} in {repo_slug} using {merge_strategy} strategy")
    
    try:
        client = get_client()
        result = await client.merge_pull_request(
            repo_slug, pr_id, merge_strategy, close_source_branch, message
        )
        
        if ctx:
            await ctx.info("Pull request merged successfully")
        
        return {
            "merged": True,
            "merge_commit": result.get("hash"),
            "strategy": merge_strategy,
            "closed_source_branch": close_source_branch
        }
    
    except Exception as e:
        error_msg = f"Failed to merge PR #{pr_id} in '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.tool
async def decline_pr(
    repo_slug: str,
    pr_id: int,
    reason: str = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Decline (reject) a pull request.
    
    This closes the pull request without merging the changes.
    
    Args:
        repo_slug: The repository slug (name)
        pr_id: The pull request ID number
        reason: Optional reason for declining the PR
    
    Returns:
        Information about the declined PR
    """
    if ctx:
        await ctx.info(f"Declining PR #{pr_id} in {repo_slug}")
    
    try:
        client = get_client()
        result = await client.decline_pull_request(repo_slug, pr_id, reason)
        
        if ctx:
            await ctx.info("Pull request declined successfully")
        
        return {
            "declined": True,
            "state": result.get("state"),
            "reason": reason
        }
    
    except Exception as e:
        error_msg = f"Failed to decline PR #{pr_id} in '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.tool
async def get_pr_comments(
    repo_slug: str,
    pr_id: int,
    ctx: Context = None
) -> List[Dict[str, Any]]:
    """
    Get all comments for a pull request.
    
    This retrieves all review comments, both general and inline comments,
    to understand the discussion around the code changes.
    
    Args:
        repo_slug: The repository slug (name)
        pr_id: The pull request ID number
    
    Returns:
        List of comments with their content and metadata
    """
    if ctx:
        await ctx.info(f"Fetching comments for PR #{pr_id} in {repo_slug}")
    
    try:
        client = get_client()
        comments = await client.get_pull_request_comments(repo_slug, pr_id)
        
        # Format comments for better readability
        formatted_comments = []
        for comment in comments:
            formatted_comment = {
                "id": comment.get("id"),
                "content": comment.get("content", {}).get("raw", ""),
                "author": comment.get("user", {}).get("display_name", "Unknown"),
                "created_on": comment.get("created_on"),
                "updated_on": comment.get("updated_on"),
                "is_inline": "inline" in comment,
                "file_path": comment.get("inline", {}).get("path") if "inline" in comment else None,
                "line_number": comment.get("inline", {}).get("to") if "inline" in comment else None
            }
            formatted_comments.append(formatted_comment)
        
        if ctx:
            await ctx.info(f"Retrieved {len(formatted_comments)} comments")
        
        return formatted_comments
    
    except Exception as e:
        error_msg = f"Failed to get comments for PR #{pr_id} in '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


# =============================================================================
# 📂 MCP RESOURCES - READ-ONLY DATA ACCESS  
# =============================================================================
# 🎓 TUTORIAL: Resources provide data that AI can read and analyze
# Unlike tools (which perform actions), resources give AI access to information
# They use URI patterns like "bitbucket://repositories" for addressing

@mcp.resource("bitbucket://repositories")
async def get_repositories_resource(ctx: Context = None) -> Dict[str, Any]:
    """
    Get a list of all repositories in the workspace.
    
    🎓 TUTORIAL NOTE: This resource demonstrates:
    - URI-based resource addressing (bitbucket://repositories)
    - Read-only data access pattern
    - Structured data return for AI analysis
    - Error handling in resource functions
    
    This resource provides read-only access to repository information.
    """
    if ctx:
        await ctx.info("Providing repositories resource")
    
    try:
        client = get_client()
        repositories = await client.list_repositories()
        
        # Convert to a structured format for resource consumption
        return {
            "workspace": client.workspace,
            "total_repositories": len(repositories),
            "repositories": [
                {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description or "No description",
                    "is_private": repo.is_private,
                    "language": repo.language or "Unknown",
                    "updated_on": repo.updated_on
                }
                for repo in repositories
            ]
        }
    
    except Exception as e:
        error_msg = f"Failed to provide repositories resource: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.resource("bitbucket://repo/{repo_slug}")
async def get_repository_resource(repo_slug: str, ctx: Context = None) -> Dict[str, Any]:
    """
    Get detailed information about a specific repository.
    This is a resource template that provides repository data.
    
    Args:
        repo_slug: The repository slug (name)
    """
    if ctx:
        await ctx.info(f"Providing repository resource for {repo_slug}")
    
    try:
        client = get_client()
        repo = await client.get_repository(repo_slug)
        
        return {
            "repository": {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "No description",
                "is_private": repo.is_private,
                "language": repo.language or "Unknown",
                "size": repo.size,
                "created_on": repo.created_on,
                "updated_on": repo.updated_on,
                "has_issues": repo.has_issues,
                "has_wiki": repo.has_wiki,
                "clone_urls": repo.clone_links
            }
        }
    
    except Exception as e:
        error_msg = f"Failed to provide repository resource for '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.resource("bitbucket://repo/{repo_slug}/pullrequests")
async def get_pull_requests_resource(repo_slug: str, ctx: Context = None) -> Dict[str, Any]:
    """
    Get pull requests for a specific repository.
    This resource template provides PR data for a repository.
    
    Args:
        repo_slug: The repository slug (name)
    """
    if ctx:
        await ctx.info(f"Providing pull requests resource for {repo_slug}")
    
    try:
        client = get_client()
        pull_requests = await client.list_pull_requests(repo_slug, "OPEN")
        
        return {
            "repository": repo_slug,
            "pull_requests": [
                {
                    "id": pr.id,
                    "title": pr.title,
                    "state": pr.state,
                    "author": pr.author,
                    "source_branch": pr.source_branch,
                    "destination_branch": pr.destination_branch,
                    "created_on": pr.created_on,
                    "comment_count": pr.comment_count
                }
                for pr in pull_requests
            ]
        }
    
    except Exception as e:
        error_msg = f"Failed to provide pull requests resource for '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


@mcp.resource("bitbucket://pr/{repo_slug}/{pr_id}/comments")
async def get_pr_comments_resource(repo_slug: str, pr_id: int, ctx: Context = None) -> Dict[str, Any]:
    """
    Get comments for a specific pull request.
    This resource template provides access to all comments and discussions on a PR.
    
    Args:
        repo_slug: The repository slug (name)
        pr_id: The pull request ID
    """
    if ctx:
        await ctx.info(f"Providing comments resource for PR #{pr_id} in {repo_slug}")
    
    try:
        client = get_client()
        comments = await client.get_pull_request_comments(repo_slug, pr_id)
        
        # Format for resource response
        formatted_comments = []
        for comment in comments:
            formatted_comment = {
                "id": comment.get("id"),
                "content": comment.get("content", {}).get("raw", ""),
                "content_html": comment.get("content", {}).get("html", ""),
                "author": comment.get("user", {}).get("display_name", "Unknown"),
                "author_uuid": comment.get("user", {}).get("uuid"),
                "created_on": comment.get("created_on"),
                "updated_on": comment.get("updated_on"),
                "is_inline": "inline" in comment,
                "inline_details": comment.get("inline") if "inline" in comment else None
            }
            formatted_comments.append(formatted_comment)
        
        return {
            "repository": repo_slug,
            "pull_request_id": pr_id,
            "comment_count": len(formatted_comments),
            "comments": formatted_comments
        }
    
    except Exception as e:
        error_msg = f"Failed to provide comments resource for PR #{pr_id} in '{repo_slug}': {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        raise ToolError(error_msg)


# =============================================================================
# SERVER LIFECYCLE
# =============================================================================

async def initialize_client():
    """Initialize the Bitbucket client"""
    global _bitbucket_client
    try:
        _bitbucket_client = create_client_from_env()
        print(f"✅ Bitbucket client initialized for workspace: {_bitbucket_client.workspace}")
    except Exception as e:
        print(f"❌ Failed to initialize Bitbucket client: {e}")
        print("\nMake sure you have set the following environment variables:")
        print("- BITBUCKET_USERNAME")
        print("- BITBUCKET_APP_PASSWORD")
        print("- BITBUCKET_WORKSPACE")
        raise


async def cleanup_client():
    """Clean up the Bitbucket client"""
    global _bitbucket_client
    if _bitbucket_client:
        await _bitbucket_client.close()
        print("✅ Bitbucket client closed")


def main():
    """
    Main entry point for the Bitbucket MCP server.
    
    This function initializes the Bitbucket client and starts the MCP server.
    """
    
    async def run_server():
        # Initialize the Bitbucket client
        await initialize_client()
        
        try:
            # Run the MCP server
            print("🚀 Starting Bitbucket MCP Server...")
            print("📡 Server will be available for MCP connections")
            print("🔗 Use this server with Cursor, Claude Desktop, or other MCP clients")
            print("")
            
            await mcp.run_async()
        finally:
            # Clean up
            await cleanup_client()
    
    # Run the server
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
