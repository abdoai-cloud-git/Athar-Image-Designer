#!/usr/bin/env python3
"""
Test script for Athar Image Generation Workflow
Runs the complete workflow with a test input
"""
import asyncio
import json
import sys
from dotenv import load_dotenv

load_dotenv()

from agency import create_agency


async def test_workflow(input_json_str):
    """Run the workflow with the given input JSON string"""
    print("=" * 60)
    print("ATHAR IMAGE GENERATION WORKFLOW TEST")
    print("=" * 60)
    
    # Parse input
    try:
        input_data = json.loads(input_json_str)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON input: {e}")
        return 1
    
    print(f"\n📥 Input:")
    print(json.dumps(input_data, indent=2, ensure_ascii=False))
    
    # Construct message for brief_agent
    text = input_data.get("text", "")
    aspect_ratio = input_data.get("aspect_ratio", "16:9")
    style = input_data.get("style", "cinematic-premium")
    
    message = f"""Generate an image with the following specifications:
Text: {text}
Aspect Ratio: {aspect_ratio}
Style: {style}

Please extract the creative brief and proceed with the full workflow."""
    
    print(f"\n📤 Sending message to brief_agent...")
    print(f"Message: {message[:100]}...")
    
    # Create agency and run
    try:
        agency = create_agency()
        print(f"\n✅ Agency created: {agency.name}")
        if hasattr(agency, 'agents'):
            if isinstance(agency.agents, dict):
                print(f"✅ Agents: {list(agency.agents.keys())}")
            else:
                print(f"✅ Agents: {[getattr(a, 'name', str(a)) for a in agency.agents]}")
        
        print("\n🔄 Running workflow...")
        print("-" * 60)
        
        response = await agency.get_response(message)
        
        print("-" * 60)
        print("\n📥 Final Response:")
        print(response)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during workflow execution:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_json = sys.argv[1]
    else:
        # Default test input
        input_json = '{"text":"اقترب من ذاتك أكثر.","aspect_ratio":"4:5","style":"cinematic-premium"}'
    
    exit_code = asyncio.run(test_workflow(input_json))
    sys.exit(exit_code)
