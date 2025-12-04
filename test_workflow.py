#!/usr/bin/env python3
"""
Test script for Athar Image Generation Workflow
Runs a smoke test with the provided input
"""

import asyncio
import json
import sys
from dotenv import load_dotenv
from agency import create_agency

load_dotenv()

async def test_workflow(input_text, aspect_ratio="4:5", style="cinematic-premium"):
    """
    Test the complete workflow with given input
    """
    print("=" * 60)
    print("ATHAR IMAGE GENERATION WORKFLOW - SMOKE TEST")
    print("=" * 60)
    print(f"\nInput: {input_text}")
    print(f"Aspect Ratio: {aspect_ratio}")
    print(f"Style: {style}\n")
    
    # Create agency
    try:
        agency = create_agency()
        print(f"✓ Agency created: {agency.name}")
        print(f"✓ Agents: {len(agency.agents)}\n")
    except Exception as e:
        print(f"✗ Failed to create agency: {e}")
        return False
    
    # Format input message
    input_message = f"Generate an image with the following text: '{input_text}'. Aspect ratio: {aspect_ratio}, Style: {style}"
    
    # Run workflow
    print("Starting workflow...")
    print("-" * 60)
    try:
        response = await agency.get_response(input_message)
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETED")
        print("=" * 60)
        print("\nFinal Response:")
        print(response)
        return True
    except Exception as e:
        print(f"\n✗ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Default test input
    test_input = "اقترب من ذاتك أكثر."
    test_aspect_ratio = "4:5"
    test_style = "cinematic-premium"
    
    # Allow override via command line
    if len(sys.argv) > 1:
        try:
            input_json = json.loads(sys.argv[1])
            test_input = input_json.get("text", test_input)
            test_aspect_ratio = input_json.get("aspect_ratio", test_aspect_ratio)
            test_style = input_json.get("style", test_style)
        except json.JSONDecodeError:
            print("Error: Invalid JSON input. Using defaults.")
    
    success = asyncio.run(test_workflow(test_input, test_aspect_ratio, test_style))
    sys.exit(0 if success else 1)
