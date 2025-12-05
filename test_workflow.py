#!/usr/bin/env python3
"""
Smoke test script for Athar Image Designer Swarm
Tests the entire workflow with JSON validation
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from shared.schemas import (
    CreativeBriefSchema,
    PromptPayloadSchema,
    ImageGenerationResultSchema,
)
from shared.workflow_guard import (
    guard_agent_output,
    WorkflowValidationError,
    fail_fast_payload,
)

# Load environment
load_dotenv()


def validate_output(agent_name, output_str, schema):
    """Validate output via strict JSON schema."""
    try:
        validated = guard_agent_output(agent_name, output_str, schema)
        print(f"✓ {agent_name}: Schema validated")
        return True, validated
    except WorkflowValidationError as err:
        print(f"✗ {agent_name}: validation failed")
        print(fail_fast_payload(err))
        return False, None

def test_brief_tool():
    """Test ExtractBriefTool returns JSON"""
    print("\n1. Testing Brief Agent Tool...")
    from brief_agent.tools.ExtractBriefTool import ExtractBriefTool
    
    tool = ExtractBriefTool(
        user_input="اقترب من ذاتك أكثر. Create a serene desert scene at sunset."
    )
    output = tool.run()
    is_valid, data = validate_output("brief_agent", output, CreativeBriefSchema)
    
    if is_valid:
        print(f"  - Theme: {data.get('theme', 'N/A')}")
        print(f"  - Mood: {data.get('mood', 'N/A')}")
    
    return is_valid

def test_art_direction_tool():
    """Test GeneratePromptTool returns JSON"""
    print("\n2. Testing Art Direction Agent Tool...")
    from art_direction_agent.tools.GeneratePromptTool import GeneratePromptTool
    
    tool = GeneratePromptTool(
        theme="solitude and contemplation",
        mood="serene, contemplative",
        palette="warm earth tones, soft golden light",
        aspect_ratio="4:5"
    )
    output = tool.run()
    is_valid, data = validate_output("art_direction_agent", output, PromptPayloadSchema)
    
    if is_valid:
        print(f"  - Has prompt: {'prompt' in data}")
        print(f"  - Has negative_prompt: {'negative_prompt' in data}")
        print(f"  - Aspect ratio: {data.get('aspect_ratio', 'N/A')}")
    
    return is_valid


def test_image_schema_sample():
    """Sanity-check image schema validation with sample payload."""
    print("\n3. Testing Image Result Schema (Sample Payload)...")
    sample = {
        "success": True,
        "image_url": "https://example.com/sample.png",
        "seed": "12345",
        "prompt_used": "Sample prompt",
        "aspect_ratio": "4:5",
        "num_images": 1,
        "all_image_urls": ["https://example.com/sample.png"],
    }
    output = json.dumps(sample)
    is_valid, _ = validate_output("nb_image_agent", output, ImageGenerationResultSchema)
    return is_valid

def test_kie_endpoint():
    """Test KIE API endpoint reachability"""
    print("\n4. Testing KIE API Endpoint...")
    import requests
    
    api_key = os.getenv("KIE_API_KEY")
    if not api_key:
        print("  ⚠ KIE_API_KEY not set - skipping")
        return True
    
    try:
        url = "https://api.kie.ai/api/v1/playground/recordInfo"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"taskId": "test_connectivity"}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code in [200, 400, 404]:  # Any response means reachable
            print(f"✓ KIE API reachable (status: {response.status_code})")
            return True
        else:
            print(f"⚠ KIE API returned unexpected status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ KIE API timeout")
        return False
    except Exception as e:
        print(f"✗ KIE API error: {e}")
        return False

def test_env_variables():
    """Check required environment variables"""
    print("\n5. Testing Environment Variables...")
    
    required_vars = {
        "OPENAI_API_KEY": "Required for agent orchestration",
        "KIE_API_KEY": "Required for image generation",
        "KIE_API_BASE": "Required for KIE API base URL",
        "GOOGLE_SERVICE_ACCOUNT_JSON": "Required for Google Drive upload",
        "GDRIVE_FOLDER_ID": "Required for Google Drive folder"
    }
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: Set")
        else:
            print(f"  ⚠ {var}: Not set - {description}")
            if var in ["OPENAI_API_KEY", "KIE_API_KEY"]:
                all_set = False
    
    return all_set

def main():
    print("=" * 70)
    print("ATHAR IMAGE DESIGNER SWARM - SMOKE TEST")
    print("=" * 70)
    
    tests = [
        ("Brief Tool JSON", test_brief_tool),
        ("Art Direction Tool JSON", test_art_direction_tool),
        ("Image Result Schema Sample", test_image_schema_sample),
        ("KIE Endpoint", test_kie_endpoint),
        ("Environment Variables", test_env_variables),
    ]

    results = {}
    for name, fn in tests:
        passed = fn()
        results[name] = passed
        if not passed:
            print("\nStopping smoke run due to failure above.")
            break
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values()) and len(results) == len(tests)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✨ ALL TESTS PASSED - Ready for deployment")
        print("\nNext Steps:")
        print("1. Add API keys to .env (if not already set)")
        print("2. Run full E2E test: python3 test_e2e.py")
        print("3. Or test via agency: python3 agency.py")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Please fix issues above")
        print("\nTo fix:")
        print("- Ensure .env file has all required API keys")
        print("- Check network connectivity for KIE API")
        return 1

if __name__ == "__main__":
    sys.exit(main())
