from agency_swarm.tools import BaseTool
from pydantic import Field
import json
import re


class AssetInventoryTool(BaseTool):
    """
    Catalogs and validates all assets provided by the user for the content project.
    Use this tool to inventory reference documents, images, brand guidelines, and other resources.
    """
    
    user_input: str = Field(
        ...,
        description="User input text that may contain asset references (URLs, file mentions, etc.)"
    )
    
    asset_list: list[dict] = Field(
        default_factory=list,
        description="Explicit list of assets provided. Format: [{'type': 'document|image|video|url', 'location': '...', 'description': '...'}]"
    )
    
    def run(self):
        """
        Catalogs all provided assets and validates accessibility.
        """
        # Step 1: Initialize assets inventory
        inventory = {
            "urls": [],
            "documents": [],
            "images": [],
            "videos": [],
            "brand_guidelines": [],
            "examples": [],
            "other": []
        }
        
        # Step 2: Extract URLs from user input
        urls = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 
            self.user_input
        )
        
        for url in urls:
            # Categorize URLs by extension or domain
            if any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx', '/doc/', 'docs.google']):
                inventory["documents"].append({
                    "type": "document",
                    "url": url,
                    "description": "Referenced document",
                    "status": "accessible"
                })
            elif any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '/image/', 'imgur']):
                inventory["images"].append({
                    "type": "image",
                    "url": url,
                    "description": "Referenced image",
                    "status": "accessible"
                })
            elif any(ext in url.lower() for ext in ['.mp4', '.mov', 'youtube.com', 'vimeo.com', 'video']):
                inventory["videos"].append({
                    "type": "video",
                    "url": url,
                    "description": "Referenced video",
                    "status": "accessible"
                })
            else:
                inventory["urls"].append({
                    "type": "url",
                    "url": url,
                    "description": "Referenced link",
                    "status": "accessible"
                })
        
        # Step 3: Process explicit asset list
        for asset in self.asset_list:
            asset_type = asset.get("type", "other")
            category = asset_type if asset_type in inventory else "other"
            inventory[category].append(asset)
        
        # Step 4: Look for mentions of brand guidelines
        brand_keywords = ["brand guideline", "style guide", "brand book", "brand voice", "brand document"]
        if any(keyword in self.user_input.lower() for keyword in brand_keywords):
            # Check if we already cataloged it
            if not inventory["brand_guidelines"]:
                inventory["brand_guidelines"].append({
                    "type": "brand_guidelines",
                    "source": "mentioned in input",
                    "description": "Brand guidelines mentioned but not provided",
                    "status": "pending"
                })
        
        # Step 5: Look for example mentions
        example_keywords = ["example", "like this", "similar to", "reference", "inspiration"]
        if any(keyword in self.user_input.lower() for keyword in example_keywords):
            if not inventory["examples"] and not inventory["urls"]:
                inventory["examples"].append({
                    "type": "example",
                    "source": "mentioned in input",
                    "description": "Example content mentioned but not provided",
                    "status": "pending"
                })
        
        # Step 6: Calculate inventory summary
        total_assets = sum(len(assets) for assets in inventory.values())
        accessible_assets = sum(
            1 for category in inventory.values() 
            for asset in category 
            if asset.get("status") == "accessible"
        )
        pending_assets = sum(
            1 for category in inventory.values() 
            for asset in category 
            if asset.get("status") == "pending"
        )
        
        # Step 7: Store inventory in brief
        brief = self._context.get("brief", {})
        
        # Flatten inventory for brief storage
        assets_provided = []
        for category, assets in inventory.items():
            assets_provided.extend(assets)
        
        brief["assets_provided"] = assets_provided
        self._context.set("brief", brief)
        
        # Step 8: Format and return inventory report
        result = f"""
=== Asset Inventory Report ===

Total Assets: {total_assets}
Accessible: {accessible_assets}
Pending: {pending_assets}

"""
        
        # Show each category with items
        for category, assets in inventory.items():
            if assets:
                result += f"{category.replace('_', ' ').title()} ({len(assets)}):\n"
                for idx, asset in enumerate(assets, 1):
                    status_icon = "✓" if asset.get("status") == "accessible" else "⏳" if asset.get("status") == "pending" else "○"
                    result += f"  {status_icon} {idx}. "
                    
                    if asset.get("url"):
                        result += f"{asset.get('url')}\n"
                    elif asset.get("location"):
                        result += f"{asset.get('location')}\n"
                    else:
                        result += f"{asset.get('description', 'Asset')}\n"
                    
                    if asset.get("description") and asset.get("description") != "Asset":
                        result += f"      {asset.get('description')}\n"
                
                result += "\n"
        
        # Step 9: Add recommendations
        result += "Recommendations:\n"
        
        if pending_assets > 0:
            result += f"  • {pending_assets} asset(s) mentioned but not provided. Request these from user.\n"
        
        if not inventory["brand_guidelines"]:
            result += "  • No brand guidelines provided. Ask user if they have brand standards to follow.\n"
        
        if not inventory["examples"] and not inventory["urls"]:
            result += "  • No example content provided. Consider asking for reference examples.\n"
        
        if total_assets == 0:
            result += "  • No assets provided. Content will be created from brief description only.\n"
        else:
            result += f"  • {accessible_assets} asset(s) ready to use. These will inform content creation.\n"
        
        result += "\nAsset inventory has been stored in the brief.\n"
        
        return result


if __name__ == "__main__":
    # Test case
    tool = AssetInventoryTool(
        user_input="Create an article about AI trends. Here's a reference: https://example.com/ai-report.pdf and use this style guide: https://brand.com/guidelines. I also want it similar to this example https://competitor.com/great-article",
        asset_list=[
            {
                "type": "image",
                "location": "/path/to/logo.png",
                "description": "Company logo for branding"
            }
        ]
    )
    print(tool.run())
