"""
Bitbucket API Client

A simple, focused wrapper around the Bitbucket REST API v2.0 for MCP integration.
This client handles authentic            repositories.append(Repository(
                name=repo_data["name"],
                full_name=repo_data["full_name"],
                description=repo_data.get("description"),
                is_private=repo_data["is_private"],
                clone_links=repo_data["links"]["clone"],
                created_on=repo_data["created_on"],
                updated_on=repo_data["updated_on"],
                size=repo_data["size"],
                language=repo_data.get("language"),
                has_issues=repo_data.get("has_issues", False),
                has_wiki=repo_data.get("has_wiki", False)
            ))imiting, and provides typed responses
for the most common Bitbucket operations needed for code review workflows.
"""

import os
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote


@dataclass
class Repository:
    """Represents a Bitbucket repository"""
    name: str
    full_name: str
    description: Optional[str]
    is_private: bool
    clone_links: Dict[str, str]
    created_on: str
    updated_on: str
    size: int
    language: Optional[str]
    has_issues: bool
    has_wiki: bool


@dataclass
class PullRequest:
    """Represents a Bitbucket pull request"""
    id: int
    title: str
    description: Optional[str]
    state: str  # OPEN, MERGED, DECLINED, SUPERSEDED
    author: str
    source_branch: str
    destination_branch: str
    created_on: str
    updated_on: str
    comment_count: int
    task_count: int
    approval_count: int


class BitbucketClient:
    """
    Simple Bitbucket API client for MCP integration.
    
    Handles authentication using Bitbucket App Passwords and provides
    methods for the most common operations needed for code review workflows.
    """
    
    def __init__(
        self, 
        username: str, 
        app_password: str, 
        workspace: str,
        base_url: str = "https://api.bitbucket.org/2.0"
    ):
        self.username = username
        self.workspace = workspace
        self.base_url = base_url
        
        # Create HTTP client with authentication
        self.client = httpx.AsyncClient(
            auth=(username, app_password),
            timeout=30.0,
            follow_redirects=True,  # Follow redirects for diff endpoints
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def _encode_repo_slug(self, repo_slug: str) -> str:
        """URL encode repository slug to handle spaces and special characters"""
        return quote(repo_slug, safe='')
    
    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to the Bitbucket API"""
        # Handle full URLs (for pagination) vs relative endpoints
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def _post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request to the Bitbucket API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        kwargs = {"json": data} if data else {}
        response = await self.client.post(url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    async def _put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a PUT request to the Bitbucket API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = await self.client.put(url, json=data)
        response.raise_for_status()
        return response.json()
    
    async def _delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request to the Bitbucket API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = await self.client.delete(url)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    # Repository Operations
    async def list_repositories(self, role: str = "member") -> List[Repository]:
        """
        List repositories in the workspace.
        
        Args:
            role: Filter by role (admin, contributor, member)
        """
        repositories = []
        url = f"/repositories/{self.workspace}"
        params = {
            "sort": "-updated_on",
            "pagelen": 50
        }
        
        # Only add role filter if specified and not "member" (which can be restrictive)
        if role and role != "member":
            params["role"] = role
        
        while url:
            data = await self._get(url, params)
            
            # Process repositories from current page
            for repo_data in data.get("values", []):
                # Extract clone links
                clone_links = {}
                for link in repo_data.get("links", {}).get("clone", []):
                    clone_links[link["name"]] = link["href"]
                
                repositories.append(Repository(
                    name=repo_data["name"],
                    full_name=repo_data["full_name"],
                    description=repo_data.get("description"),
                    is_private=repo_data["is_private"],
                    clone_links=clone_links,
                    created_on=repo_data["created_on"],
                    updated_on=repo_data["updated_on"],
                    size=repo_data["size"],
                    language=repo_data.get("language"),
                    has_issues=repo_data.get("has_issues", False),
                    has_wiki=repo_data.get("has_wiki", False)
                ))
            
            # Check for next page
            url = data.get("next")
            if url:
                # Next URL is complete, don't add params again
                params = None
        
        return repositories
    
    async def get_repository(self, repo_slug: str) -> Repository:
        """Get detailed information about a specific repository"""
        encoded_slug = self._encode_repo_slug(repo_slug)
        data = await self._get(f"/repositories/{self.workspace}/{encoded_slug}")
        
        # Extract clone links
        clone_links = {}
        for link in data.get("links", {}).get("clone", []):
            clone_links[link["name"]] = link["href"]
        
        return Repository(
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            is_private=data["is_private"],
            clone_links=clone_links,
            created_on=data["created_on"],
            updated_on=data["updated_on"],
            size=data["size"],
            language=data.get("language"),
            has_issues=data.get("has_issues", False),
            has_wiki=data.get("has_wiki", False)
        )
    
    # Pull Request Operations
    async def list_pull_requests(
        self, 
        repo_slug: str, 
        state: str = "OPEN"
    ) -> List[PullRequest]:
        """
        List pull requests for a repository.
        
        Args:
            repo_slug: Repository slug
            state: PR state (OPEN, MERGED, DECLINED, SUPERSEDED)
        """
        data = await self._get(
            f"/repositories/{self.workspace}/{self._encode_repo_slug(repo_slug)}/pullrequests",
            {"state": state, "sort": "-updated_on", "pagelen": 50}
        )
        
        pull_requests = []
        for pr_data in data.get("values", []):
            pull_requests.append(PullRequest(
                id=pr_data["id"],
                title=pr_data["title"],
                description=pr_data.get("description"),
                state=pr_data["state"],
                author=pr_data["author"]["display_name"],
                source_branch=pr_data["source"]["branch"]["name"],
                destination_branch=pr_data["destination"]["branch"]["name"],
                created_on=pr_data["created_on"],
                updated_on=pr_data["updated_on"],
                comment_count=pr_data["comment_count"],
                task_count=pr_data["task_count"],
                approval_count=0  # We'll calculate this separately if needed
            ))
        
        return pull_requests
    
    async def get_pull_request(self, repo_slug: str, pr_id: int) -> PullRequest:
        """Get detailed information about a specific pull request"""
        data = await self._get(
            f"/repositories/{self.workspace}/{self._encode_repo_slug(repo_slug)}/pullrequests/{pr_id}"
        )
        
        return PullRequest(
            id=data["id"],
            title=data["title"],
            description=data.get("description"),
            state=data["state"],
            author=data["author"]["display_name"],
            source_branch=data["source"]["branch"]["name"],
            destination_branch=data["destination"]["branch"]["name"],
            created_on=data["created_on"],
            updated_on=data["updated_on"],
            comment_count=data["comment_count"],
            task_count=data["task_count"],
            approval_count=0  # We'll calculate this separately if needed
        )
    
    async def get_pull_request_diff(self, repo_slug: str, pr_id: int) -> str:
        """Get the raw diff for a pull request"""
        url = f"{self.base_url}/repositories/{self.workspace}/{self._encode_repo_slug(repo_slug)}/pullrequests/{pr_id}/diff"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.text

    async def add_pull_request_comment(
        self, 
        repo_slug: str, 
        pr_id: int, 
        content: str,
        inline: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a comment to a pull request.
        
        Args:
            repo_slug: Repository slug
            pr_id: Pull request ID
            content: Comment content (supports Markdown)
            inline: Optional inline comment data with file path and line number
            
        Returns:
            Created comment data
        """
        comment_data = {
            "content": {
                "raw": content
            }
        }
        
        # Add inline comment positioning if provided
        if inline:
            comment_data["inline"] = inline
            
        return await self._post(
            f"/repositories/{self.workspace}/{self._encode_repo_slug(repo_slug)}/pullrequests/{pr_id}/comments",
            comment_data
        )
    
    async def approve_pull_request(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """
        Approve a pull request.
        
        Args:
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            Approval data
        """
        return await self._post(
            f"/repositories/{self.workspace}/{self._encode_repo_slug(repo_slug)}/pullrequests/{pr_id}/approve"
        )
    
    async def unapprove_pull_request(self, repo_slug: str, pr_id: int) -> Dict[str, Any]:
        """
        Remove approval from a pull request.
        
        Args:
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            Response data
        """
        return await self._delete(
            f"/repositories/{self.workspace}/{self._encode_repo_slug(repo_slug)}/pullrequests/{pr_id}/approve"
        )
    
    async def merge_pull_request(
        self, 
        repo_slug: str, 
        pr_id: int,
        merge_strategy: str = "merge_commit",
        close_source_branch: bool = False,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Merge a pull request.
        
        Args:
            repo_slug: Repository slug
            pr_id: Pull request ID
            merge_strategy: Strategy to use ('merge_commit', 'squash', 'fast_forward')
            close_source_branch: Whether to close the source branch after merge
            message: Optional merge commit message
            
        Returns:
            Merge result data
        """
        merge_data = {
            "type": merge_strategy,
            "close_source_branch": close_source_branch
        }
        
        if message:
            merge_data["message"] = message
            
        return await self._post(
            f"/repositories/{self.workspace}/{self._encode_repo_slug(repo_slug)}/pullrequests/{pr_id}/merge",
            merge_data
        )
    
    async def decline_pull_request(
        self, 
        repo_slug: str, 
        pr_id: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decline (reject) a pull request.
        
        Args:
            repo_slug: Repository slug
            pr_id: Pull request ID
            reason: Optional reason for declining
            
        Returns:
            Updated pull request data
        """
        decline_data = {}
        if reason:
            decline_data["reason"] = reason
            
        return await self._post(
            f"/repositories/{self.workspace}/{self._encode_repo_slug(repo_slug)}/pullrequests/{pr_id}/decline",
            decline_data
        )

    async def get_pull_request_comments(
        self, 
        repo_slug: str, 
        pr_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get all comments for a pull request.
        
        Args:
            repo_slug: Repository slug
            pr_id: Pull request ID
            
        Returns:
            List of comment data
        """
        data = await self._get(
            f"/repositories/{self.workspace}/{self._encode_repo_slug(repo_slug)}/pullrequests/{pr_id}/comments"
        )
        return data.get("values", [])


def create_client_from_env() -> BitbucketClient:
    """
    Create a Bitbucket client from environment variables.
    
    Required environment variables:
    - BITBUCKET_USERNAME
    - BITBUCKET_APP_PASSWORD
    - BITBUCKET_WORKSPACE
    
    Optional:
    - BITBUCKET_API_BASE_URL (defaults to https://api.bitbucket.org/2.0)
    """
    username = os.getenv("BITBUCKET_USERNAME")
    app_password = os.getenv("BITBUCKET_APP_PASSWORD")
    workspace = os.getenv("BITBUCKET_WORKSPACE")
    base_url = os.getenv("BITBUCKET_API_BASE_URL", "https://api.bitbucket.org/2.0")
    
    if not username:
        raise ValueError("BITBUCKET_USERNAME environment variable is required")
    if not app_password:
        raise ValueError("BITBUCKET_APP_PASSWORD environment variable is required")
    if not workspace:
        raise ValueError("BITBUCKET_WORKSPACE environment variable is required")
    
    return BitbucketClient(
        username=username,
        app_password=app_password,
        workspace=workspace,
        base_url=base_url
    )
