import arxiv
import os
import json
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP
from IPython.display import IFrame

# Configuration
PAPER_DIR = "papers"
DEFAULT_MAX_RESULTS = 5

# Initialize FastMCP server
mcp = FastMCP("research")

@mcp.tool()
def search_papers(topic: str, max_results: int = DEFAULT_MAX_RESULTS) -> List[str]:
    """
    Search for papers on ArXiv based on a topic.
    
    Args:
        topic: The research topic to search for
        max_results: Maximum number of papers to retrieve (default: 5)
    
    Returns:
        List of paper IDs that were found and saved
    """
    try:
        # Input validation
        if not topic or not topic.strip():
            return ["Error: Topic cannot be empty"]
        
        if max_results <= 0 or max_results > 50:
            max_results = DEFAULT_MAX_RESULTS
        
        client = arxiv.Client()
        
        search = arxiv.Search(
            query=topic.strip(),
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = client.results(search)
        
        # Create directory structure
        topic_dir = topic.lower().replace(" ", "_").replace("/", "_")
        path = os.path.join(PAPER_DIR, topic_dir)
        os.makedirs(path, exist_ok=True)
        
        # Load existing papers info
        file_path = os.path.join(path, "papers_info.json")
        
        try:
            with open(file_path, "r", encoding='utf-8') as file:
                papers_info = json.load(file)
        except FileNotFoundError:
            papers_info = {}
        except json.JSONDecodeError as e:
            print(f"Warning: Corrupted JSON file {file_path}, creating new one. Error: {e}")
            papers_info = {}
        
        paper_ids = []
        new_papers_count = 0
        
        for paper in papers:
            paper_id = paper.entry_id.split("/")[-1]
            paper_ids.append(paper_id)
            
            # Skip if paper already exists
            if paper_id in papers_info:
                continue
            
            # Extract paper information
            papers_info[paper_id] = {
                "title": paper.title.strip(),
                "summary": paper.summary.strip(),
                "published": paper.published.isoformat() if paper.published else None,
                "authors": [author.name for author in paper.authors],
                "pdf_url": paper.pdf_url,
                "doi": paper.doi,
                "topic_searched": topic,
                "arxiv_url": f"https://arxiv.org/abs/{paper_id}"
            }
            new_papers_count += 1
        
        # Save updated papers info
        with open(file_path, "w", encoding='utf-8') as file:
            json.dump(papers_info, file, indent=4, ensure_ascii=False)
        
        result_message = f"Search completed. Found {len(paper_ids)} papers for topic '{topic}'. "
        result_message += f"{new_papers_count} new papers saved to {file_path}"
        print(result_message)
        
        return paper_ids
        
    except Exception as e:
        error_msg = f"Error searching papers: {str(e)}"
        print(error_msg)
        return [error_msg]

@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Extract information for a specific paper ID from saved papers.
    
    Args:
        paper_id: The ArXiv paper ID (e.g., "2301.00001")
    
    Returns:
        JSON string with paper information or error message
    """
    try:
        # Input validation
        if not paper_id or not paper_id.strip():
            return "Error: Paper ID cannot be empty"
        
        paper_id = paper_id.strip()
        
        # Check if papers directory exists
        if not os.path.exists(PAPER_DIR):
            return f"No papers directory found. Please search for papers first."
        
        # Search across all topic directories
        for item in os.listdir(PAPER_DIR):
            item_path = os.path.join(PAPER_DIR, item)
            if os.path.isdir(item_path):
                file_path = os.path.join(item_path, "papers_info.json")
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding='utf-8') as json_file:
                            papers_info = json.load(json_file)
                            if paper_id in papers_info:
                                return json.dumps(papers_info[paper_id], indent=2, ensure_ascii=False)
                    except (FileNotFoundError, json.JSONDecodeError) as e:
                        print(f"Warning: Error reading {file_path}: {str(e)}")
                        continue
        
        return f"No information found for paper ID: {paper_id}. Please search for papers containing this ID first."
        
    except Exception as e:
        error_msg = f"Error extracting paper info: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool()
def list_saved_papers(topic: Optional[str] = None) -> str:
    """
    List all saved papers, optionally filtered by topic.
    
    Args:
        topic: Optional topic to filter by
    
    Returns:
        JSON string with list of saved papers
    """
    try:
        if not os.path.exists(PAPER_DIR):
            return "No papers directory found. Please search for papers first."
        
        all_papers = {}
        
        for item in os.listdir(PAPER_DIR):
            # Filter by topic if specified
            if topic and topic.lower().replace(" ", "_") != item.lower():
                continue
                
            item_path = os.path.join(PAPER_DIR, item)
            if os.path.isdir(item_path):
                file_path = os.path.join(item_path, "papers_info.json")
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding='utf-8') as json_file:
                            papers_info = json.load(json_file)
                            for paper_id, paper_data in papers_info.items():
                                all_papers[paper_id] = {
                                    "title": paper_data.get("title", "Unknown"),
                                    "authors": paper_data.get("authors", []),
                                    "published": paper_data.get("published", "Unknown"),
                                    "topic_searched": paper_data.get("topic_searched", item.replace("_", " ")),
                                    "arxiv_url": paper_data.get("arxiv_url", f"https://arxiv.org/abs/{paper_id}")
                                }
                    except (FileNotFoundError, json.JSONDecodeError) as e:
                        print(f"Warning: Error reading {file_path}: {str(e)}")
                        continue
        
        if not all_papers:
            filter_msg = f" for topic '{topic}'" if topic else ""
            return f"No saved papers found{filter_msg}."
        
        return json.dumps({
            "total_papers": len(all_papers),
            "papers": all_papers
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Error listing papers: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool()
def get_paper_summary(paper_id: str) -> str:
    """
    Get just the summary/abstract of a specific paper.
    
    Args:
        paper_id: The ArXiv paper ID
    
    Returns:
        The paper's summary or error message
    """
    try:
        paper_info = extract_info(paper_id)
        
        # Check if it's an error message
        if paper_info.startswith("Error:") or paper_info.startswith("No information"):
            return paper_info
        
        # Parse the JSON and extract summary
        paper_data = json.loads(paper_info)
        summary = paper_data.get("summary", "No summary available")
        title = paper_data.get("title", "Unknown Title")
        
        return f"Title: {title}\n\nSummary: {summary}"
        
    except json.JSONDecodeError:
        return "Error: Invalid paper information format"
    except Exception as e:
        return f"Error retrieving summary: {str(e)}"

if __name__ == "__main__":
    print("Starting ArXiv Research MCP Server...")
    
    # Get base URL from environment
    base_url = os.environ.get('DLAI_LOCAL_URL', 'http://localhost:{port}')
    
    # Display terminal interface
    terminal_url = base_url.format(port=8888) + "terminals/1"
    print(f"Terminal available at: {terminal_url}")
    IFrame(terminal_url, width=600, height=768)
    
    # Inspector URLs to try
    inspector_urls = [
        base_url.format(port=3001),
        base_url.format(port=8888) + "inspector",
        "http://localhost:3001"
    ]
    
    print("\nInspector might be available at:")
    for url in inspector_urls:
        print(f"  - {url}")
    
    print("\nServer tools available:")
    print("  - search_papers(topic, max_results=5)")
    print("  - extract_info(paper_id)")
    print("  - list_saved_papers(topic=None)")
    print("  - get_paper_summary(paper_id)")
    
    # Run the MCP server with inspector enabled
    try:
        mcp.run(transport='stdio', inspector=True)
    except Exception as e:
        print(f"Error running server: {e}")
        # Fallback without inspector
        mcp.run(transport='stdio')