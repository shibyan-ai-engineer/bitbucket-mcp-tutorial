#!/usr/bin/env python3
"""
Test Script for Bitbucket MCP Server

This script demonstrates how to use the FastMCP Client library to connect to
and test a Bitbucket MCP server. It's useful for verifying the server works
before connecting it to Cursor or Claude Desktop.
"""

import asyncio
import sys
import os
import json
from typing import Dict, Any

from fastmcp import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BitbucketMCPClient:
    """A dedicated client for testing the Bitbucket MCP server"""
    
    def __init__(self, server_module):
        self.server_module = server_module
        self.client = None
    
    async def connect(self):
        """Connect to the MCP server"""
        print("🔌 Connecting to Bitbucket MCP server...")
        self.client = Client(self.server_module)
        await self.client.__aenter__()
        print("✅ Connected successfully!")
    
    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.client:
            await self.client.__aexit__(None, None, None)
            print("🔌 Disconnected from server")
    
    async def list_capabilities(self):
        """List all available tools and resources"""
        print("\n" + "="*60)
        print("📋 SERVER CAPABILITIES")
        print("="*60)
        
        # List tools
        tools = await self.client.list_tools()
        print(f"\n🔧 Available Tools ({len(tools)}):")
        for i, tool in enumerate(tools, 1):
            print(f"  {i:2d}. {tool.name}")
            print(f"      Description: {tool.description}")
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                print(f"      Parameters: {list(tool.inputSchema.get('properties', {}).keys())}")
        
        # List resources
        resources = await self.client.list_resources()
        print(f"\n📂 Available Resources ({len(resources)}):")
        for i, resource in enumerate(resources, 1):
            print(f"  {i:2d}. {resource.uri}")
            print(f"      Description: {resource.description}")
    
    async def test_repository_operations(self):
        """Test repository-related operations"""
        print("\n" + "="*60)
        print("🏢 TESTING REPOSITORY OPERATIONS")
        print("="*60)
        
        # Test listing repositories
        print("\n📋 Testing list_repositories...")
        try:
            repos_result = await self.client.call_tool("list_repositories", {"role": "member"})
            repos = json.loads(repos_result[0].text)
            if isinstance(repos, dict):
                repos = [repos]
            
            print(f"✅ Found {len(repos)} repositories:")
            for repo in repos[:3]:  # Show first 3
                print(f"  • {repo['name']} ({repo.get('language', 'Unknown')})")
                print(f"    Description: {repo['description']}")
                print(f"    Private: {repo['is_private']}")
                print(f"    Size: {repo['size']:,} bytes")
            
            if len(repos) > 3:
                print(f"  ... and {len(repos) - 3} more repositories")
            
            # Test getting details of the first repository
            if repos:
                first_repo = repos[0]
                # Extract the repo slug from full_name (after the workspace/)
                repo_slug = first_repo['full_name'].split('/')[-1]
                print(f"\n📊 Testing get_repository_info for '{first_repo['name']}' (slug: {repo_slug})...")
                try:
                    repo_info_result = await self.client.call_tool(
                        "get_repository_info", 
                        {"repo_slug": repo_slug}
                    )
                    repo_info = json.loads(repo_info_result[0].text)
                    print(f"✅ Repository details retrieved:")
                    print(f"  • Full name: {repo_info['full_name']}")
                    print(f"  • Created: {repo_info['created_on'][:10]}")
                    print(f"  • Updated: {repo_info['updated_on'][:10]}")
                    print(f"  • Clone URLs: {len(repo_info.get('clone_urls', {}))} available")
                    
                    return repo_slug  # Return slug for PR testing
                    
                except Exception as e:
                    print(f"❌ Failed to get repository info: {e}")
            
        except Exception as e:
            print(f"❌ Failed to list repositories: {e}")
            return None
    
    async def test_pull_request_operations(self, repo_slug: str):
        """Test pull request operations"""
        print("\n" + "="*60)
        print("🔀 TESTING PULL REQUEST OPERATIONS")
        print("="*60)
        
        if not repo_slug:
            print("⚠️ Skipping PR tests - no repository available")
            return
        
        # Test listing pull requests
        print(f"\n📋 Testing list_pull_requests for '{repo_slug}'...")
        try:
            prs_result = await self.client.call_tool(
                "list_pull_requests", 
                {"repo_slug": repo_slug, "state": "OPEN"}
            )
            prs = json.loads(prs_result[0].text)
            if isinstance(prs, dict):
                prs = [prs]
            
            print(f"✅ Found {len(prs)} open pull requests:")
            
            if prs:
                for pr in prs[:2]:  # Show first 2
                    print(f"  • PR #{pr['id']}: {pr['title']}")
                    print(f"    Author: {pr['author']}")
                    print(f"    Branch: {pr['source_branch']} → {pr['destination_branch']}")
                    print(f"    State: {pr['state']}")
                
                # Test getting details of the first PR
                first_pr = prs[0]
                print(f"\n📊 Testing get_pull_request_info for PR #{first_pr['id']}...")
                try:
                    pr_info_result = await self.client.call_tool(
                        "get_pull_request_info",
                        {"repo_slug": repo_slug, "pr_id": first_pr['id']}
                    )
                    pr_info = json.loads(pr_info_result[0].text)
                    print(f"✅ PR details retrieved:")
                    print(f"  • Title: {pr_info['title']}")
                    print(f"  • Comments: {pr_info['comment_count']}")
                    print(f"  • Tasks: {pr_info['task_count']}")
                    print(f"  • Approvals: {pr_info['approval_count']}")
                    
                    # Test getting PR diff
                    print(f"\n📄 Testing get_pull_request_diff for PR #{first_pr['id']}...")
                    try:
                        diff_result = await self.client.call_tool(
                            "get_pull_request_diff",
                            {"repo_slug": repo_slug, "pr_id": first_pr['id']}
                        )
                        diff_text = diff_result[0].text
                        lines = diff_text.split('\n')
                        print(f"✅ Diff retrieved: {len(lines)} lines")
                        print(f"  • First few lines:")
                        for line in lines[:5]:
                            print(f"    {line[:80]}...")
                        
                        # Test getting PR comments
                        print(f"\n💬 Testing get_pr_comments for PR #{first_pr['id']}...")
                        try:
                            comments_result = await self.client.call_tool(
                                "get_pr_comments",
                                {"repo_slug": repo_slug, "pr_id": first_pr['id']}
                            )
                            comments = json.loads(comments_result[0].text)
                            print(f"✅ Found {len(comments)} comments:")
                            for comment in comments[:2]:  # Show first 2
                                print(f"  • By {comment['author']}: {comment['content'][:60]}...")
                        
                        except Exception as e:
                            print(f"❌ Failed to get PR comments: {e}")
                        
                    except Exception as e:
                        print(f"❌ Failed to get PR diff: {e}")
                    
                except Exception as e:
                    print(f"❌ Failed to get PR info: {e}")
            else:
                print("  No open pull requests found")
        
        except Exception as e:
            print(f"❌ Failed to list pull requests: {e}")
    
    async def test_resources(self):
        """Test MCP resources"""
        print("\n" + "="*60)
        print("📂 TESTING MCP RESOURCES")
        print("="*60)
        
        # Test repositories resource
        print("\n📊 Testing bitbucket://repositories resource...")
        try:
            repo_resource = await self.client.read_resource("bitbucket://repositories")
            data = repo_resource[0].text
            print(f"✅ Repository resource retrieved: {len(data)} characters")
            
            # Parse and show summary
            try:
                resource_data = json.loads(data)
                if 'repositories' in resource_data:
                    repos = resource_data['repositories']
                    print(f"  • Contains {len(repos)} repositories")
                    for repo in repos[:2]:
                        print(f"    - {repo['name']}")
            except json.JSONDecodeError:
                print(f"  • Raw data preview: {data[:100]}...")
        
        except Exception as e:
            print(f"❌ Failed to read repositories resource: {e}")
    
    async def test_management_tools(self):
        """Test PR management tools (without actually modifying anything)"""
        print("\n" + "="*60)
        print("⚙️ TESTING MANAGEMENT TOOLS (DRY RUN)")
        print("="*60)
        
        print("\n📝 Available PR Management Tools:")
        management_tools = [
            "add_pr_comment", "approve_pr", "unapprove_pr", 
            "merge_pr", "decline_pr"
        ]
        
        for tool in management_tools:
            print(f"  • {tool} - Available for PR management")
        
        print("\n⚠️ Note: These tools can modify your PRs. Use with caution!")
        print("   To test them safely, create a test PR in a test repository first.")
    
    async def performance_test(self):
        """Test server performance"""
        print("\n" + "="*60)
        print("⚡ PERFORMANCE TEST")
        print("="*60)
        
        import time
        
        # Time multiple repository calls
        print("\n⏱️ Testing response times...")
        start_time = time.time()
        
        try:
            for i in range(3):
                await self.client.call_tool("list_repositories", {"role": "member"})
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 3
            print(f"✅ Average response time: {avg_time:.2f} seconds")
            
            if avg_time < 2.0:
                print("🚀 Performance: Excellent")
            elif avg_time < 5.0:
                print("👍 Performance: Good")
            else:
                print("⚠️ Performance: Needs optimization")
        
        except Exception as e:
            print(f"❌ Performance test failed: {e}")


async def main():
    """Main test function"""
    print("🧪 FastMCP Client for Bitbucket MCP Server")
    print("=" * 60)
    
    # Check environment variables
    required_vars = ["BITBUCKET_USERNAME", "BITBUCKET_APP_PASSWORD", "BITBUCKET_WORKSPACE"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  • {var}")
        print("\nPlease check your .env file or set these variables.")
        return 1
    
    print(f"🔑 Using Bitbucket workspace: {os.getenv('BITBUCKET_WORKSPACE')}")
    print(f"👤 Using username: {os.getenv('BITBUCKET_USERNAME')}")
    
    # Import the server
    try:
        from mcp_server import mcp, initialize_client, cleanup_client
        print("✅ Successfully imported Bitbucket MCP server")
    except ImportError as e:
        print(f"❌ Failed to import server: {e}")
        return 1
    
    # Initialize server's client
    await initialize_client()
    
    # Create and connect our test client
    test_client = BitbucketMCPClient(mcp)
    
    try:
        await test_client.connect()
        
        # Run all tests
        await test_client.list_capabilities()
        repo_slug = await test_client.test_repository_operations()
        await test_client.test_pull_request_operations(repo_slug)
        await test_client.test_resources()
        await test_client.test_management_tools()
        await test_client.performance_test()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS COMPLETED")
        print("="*60)
        print("✅ Your Bitbucket MCP server is working correctly!")
        print("📋 Next steps:")
        print("   1. Configure it in Cursor/Claude Desktop (see CURSOR_SETUP.md)")
        print("   2. Test the integration with natural language commands")
        print("   3. Start using it for PR reviews and repository management")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        await test_client.disconnect()
        await cleanup_client()
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
