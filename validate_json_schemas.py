#!/usr/bin/env python3
"""
Validate that agent outputs match strict JSON schemas
"""

import json
import sys

def validate_brief_json(output_text):
    """Validate brief_agent output contains required JSON fields"""
    required_fields = [
        "theme", "mood", "tone", "palette", 
        "visual_elements", "keywords", "original_input"
    ]
    
    # Try to extract JSON from output
    try:
        # Look for JSON block
        if "=== BRIEF JSON ===" in output_text:
            json_start = output_text.find("{", output_text.find("=== BRIEF JSON ==="))
            json_end = output_text.rfind("}") + 1
            json_str = output_text[json_start:json_end]
            data = json.loads(json_str)
        else:
            # Try parsing entire output as JSON
            data = json.loads(output_text)
        
        missing = [f for f in required_fields if f not in data]
        if missing:
            return False, f"Missing fields: {missing}"
        return True, "Valid brief JSON"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_art_direction_json(output_text):
    """Validate art_direction_agent output is strict JSON only"""
    required_fields = ["prompt", "negative_prompt", "aspect_ratio", "style"]
    
    # Art direction MUST be pure JSON, no prose
    try:
        # Try parsing entire output as JSON (should work if it's pure JSON)
        data = json.loads(output_text.strip())
        
        missing = [f for f in required_fields if f not in data]
        if missing:
            return False, f"Missing fields: {missing}"
        
        # Check for prose (if output contains non-JSON text, it's invalid)
        if len(output_text.strip()) > len(json.dumps(data, indent=2)) * 1.1:
            return False, "Output contains prose/text beyond JSON"
        
        return True, "Valid strict JSON"
    except json.JSONDecodeError as e:
        return False, f"Not valid JSON (must be strict JSON only): {e}"
    except Exception as e:
        return False, f"Error: {e}"

def validate_nb_image_output(output_text):
    """Validate nb_image_agent output contains image_url"""
    # Should contain image_url
    if "image_url" in output_text or "Image URL:" in output_text:
        return True, "Contains image URL"
    return False, "Missing image URL"

def validate_qa_output(output_text):
    """Validate qa_agent output"""
    # Should contain approved status
    if "approved" in output_text.lower() or "pass" in output_text.lower() or "retry" in output_text.lower():
        return True, "Contains validation status"
    return False, "Missing validation status"

def validate_export_output(output_text):
    """Validate export_agent output contains gdrive_url"""
    if "gdrive_url" in output_text or "gdrive" in output_text.lower() or "drive.google.com" in output_text:
        return True, "Contains Google Drive URL"
    return False, "Missing Google Drive URL"

if __name__ == "__main__":
    print("JSON Schema Validation")
    print("=" * 60)
    print("\nThis script validates that agent outputs match expected schemas.")
    print("Run this after testing the workflow to verify JSON compliance.\n")
    
    # Test with example outputs
    print("Testing schemas with example outputs...\n")
    
    brief_example = """
=== CREATIVE BRIEF ===
Theme: solitude
Mood: serene
=== BRIEF JSON ===
{"theme": "solitude", "mood": "serene", "tone": "meditative", "palette": "warm earth tones", "visual_elements": "lone figure", "keywords": "solitude, desert", "original_input": "test"}
"""
    
    art_dir_example_good = '{"prompt": "test", "negative_prompt": "test", "aspect_ratio": "4:5", "style": "cinematic-premium", "seed": null}'
    art_dir_example_bad = """
=== ART DIRECTION PROMPT ===
MAIN PROMPT: test
{"prompt": "test", "negative_prompt": "test", "aspect_ratio": "4:5", "style": "cinematic-premium"}
"""
    
    print("Brief Agent:")
    valid, msg = validate_brief_json(brief_example)
    print(f"  {'✓' if valid else '✗'} {msg}")
    
    print("\nArt Direction Agent (strict JSON):")
    valid, msg = validate_art_direction_json(art_dir_example_good)
    print(f"  {'✓' if valid else '✗'} {msg}")
    
    print("\nArt Direction Agent (with prose - should fail):")
    valid, msg = validate_art_direction_json(art_dir_example_bad)
    print(f"  {'✓' if valid else '✗'} {msg}")
    
    print("\n" + "=" * 60)
    print("Validation complete. Use this script to verify actual agent outputs.")
