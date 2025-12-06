# Troubleshooting Guide - Content Automation Studio

## Common Issues and Solutions

### ✅ FIXED: Import Error - Literal from pydantic

**Error:**
```
ImportError: cannot import name 'Literal' from 'pydantic'
```

**Solution:**
This has been fixed in `workflow/contracts.py`. The `Literal` type is now correctly imported from `typing` instead of `pydantic`.

**Status:** ✅ Resolved in current version

---

## Installation Issues

### Issue: Missing Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'agency_swarm'
```

**Solution:**
```bash
pip install -r requirements.txt
```

If you're using a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: OpenAI API Key Not Found

**Error:**
```
OPENAI_API_KEY not found in environment
```

**Solution:**
1. Copy the template:
   ```bash
   cp .env.template .env
   ```

2. Edit `.env` and add your key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

3. Get your key from: https://platform.openai.com/api-keys

---

## Runtime Issues

### Issue: Agency Won't Start

**Symptoms:**
- Agency fails to initialize
- Import errors
- Module not found errors

**Solutions:**

1. **Verify Python version:**
   ```bash
   python3 --version  # Should be 3.12 or higher
   ```

2. **Reinstall dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Check agency import:**
   ```bash
   python3 -c "from agency import create_agency; print('OK')"
   ```

### Issue: Tools Failing

**Symptoms:**
- Tools return errors
- AttributeError with context
- Tools can't access shared state

**Solution:**
Tools only work when run within the agency, not standalone. This is expected behavior. The agency context is only available during agent execution.

**To test tools:**
Run the full agency and test through the workflow, not individual tool files.

---

## Quality Issues

### Issue: Content Quality Below Expectations

**Symptoms:**
- Quality score below 8.0/10
- Content doesn't match requirements
- Tone is incorrect

**Solutions:**

1. **Provide more detailed requirements:**
   ```
   Instead of: "Create an article about AI"
   
   Use: "Create a professional 1500-word article about AI trends in 2025
         for business executives. Tone should be authoritative but accessible.
         Include statistics and real-world examples."
   ```

2. **Include brand guidelines:**
   - Brand voice
   - Style preferences
   - Prohibited words/phrases
   - Must-include elements

3. **Provide examples:**
   - Share reference content you like
   - Include competitor examples
   - Specify what NOT to do

### Issue: Too Many Revisions

**Symptoms:**
- Content goes through multiple revision loops
- Reviewer keeps rejecting content
- Quality score stuck below threshold

**Solutions:**

1. **Check brief completeness:**
   - All required fields filled
   - Clear success criteria
   - Specific constraints

2. **Lower quality threshold (if appropriate):**
   Edit `strategy_agent/tools/QualityStandardsTool.py`:
   ```python
   "minimum_score": 7.5  # Lower from 8.0 if needed
   ```

3. **Review reviewer feedback:**
   - Check what specific issues are found
   - Adjust brief to address common issues
   - Update brand guidelines if needed

---

## Performance Issues

### Issue: Workflow Takes Too Long

**Symptoms:**
- Content creation takes 20+ minutes
- Agents seem stuck
- No progress updates

**Solutions:**

1. **Enable parallel execution:**
   The system automatically runs independent tasks in parallel. Ensure your strategy plan enables this.

2. **Reduce content length:**
   ```
   Instead of: 3000 words
   Try: 1500 words
   ```

3. **Simplify technical requirements:**
   - Avoid complex formatting if not needed
   - Use standard formats (markdown, PDF)
   - Minimize custom styling

4. **Check API rate limits:**
   Verify your OpenAI API plan supports your usage rate.

### Issue: Memory or Context Issues

**Symptoms:**
- Agents lose track of previous steps
- Context data missing
- Inconsistent outputs

**Solutions:**

1. **Verify agency context is being used:**
   Check that tools use `self._context.get()` and `self._context.set()`

2. **Restart the agency:**
   Context is reset on each new session, which is expected behavior.

3. **For persistent storage needs:**
   Add custom tools that save to files or databases.

---

## Agent-Specific Issues

### Orchestrator Issues

**Problem:** Tasks not delegating properly

**Solution:**
- Verify DelegateTaskTool parameters are correct
- Check workflow state with WorkflowStateTool
- Review delegation logs in context

### Intake Issues

**Problem:** Missing requirements not detected

**Solution:**
- Use ValidateRequirementsTool in strict mode
- Enable ClarifyQuestionTool for missing fields
- Review brief structure

### Strategy Issues

**Problem:** Unrealistic timeline estimates

**Solution:**
- Adjust time estimates in WorkBreakdownTool
- Build in more buffer for revisions
- Account for complexity

### Creator Issues

**Problem:** Content doesn't match tone

**Solution:**
- Use BrandVoiceTool explicitly
- Include tone examples in brief
- Specify tone in multiple places

### Reviewer Issues

**Problem:** Too strict or too lenient

**Solution:**
- Adjust quality threshold in QualityStandardsTool
- Modify acceptance criteria
- Update brand compliance rules

### Delivery Issues

**Problem:** Files not accessible

**Solution:**
- Check URL generation
- Verify file paths
- Test export formats

---

## Debugging Tips

### Enable Verbose Logging

Add logging to tools:
```python
def run(self):
    print(f"[DEBUG] Tool executing: {self.__class__.__name__}")
    print(f"[DEBUG] Parameters: {self.__dict__}")
    # ... rest of tool code
```

### Check Agency Context

Use WorkflowStateTool to inspect current state:
```python
from orchestrator_agent.tools import WorkflowStateTool

tool = WorkflowStateTool(action="get_status")
print(tool.run())
```

### Review Error Logs

Check ConflictResolutionTool logs:
```python
from orchestrator_agent.tools import ConflictResolutionTool

tool = ConflictResolutionTool(action="get_conflicts")
print(tool.run())
```

### Test Individual Agents

Test agent communication:
```bash
python3 -c "from intake_agent import intake_agent; print(intake_agent.name)"
```

---

## Environment Issues

### Issue: PATH Not Set Correctly

**Solution:**
```bash
export PATH="/home/ubuntu/.local/bin:$PATH"
```

Add to `~/.bashrc` or `~/.zshrc` for persistence.

### Issue: Python Version Mismatch

**Error:**
```
SyntaxError: invalid syntax (type hints)
```

**Solution:**
Ensure Python 3.12+ is being used:
```bash
python3 --version
```

If older version, install Python 3.12+:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12

# macOS
brew install python@3.12
```

---

## Still Having Issues?

### 1. Check Documentation

- `README.md` - Complete user guide
- `SYSTEM_SUMMARY.md` - Architecture overview
- `prd.txt` - Technical specifications
- `shared_instructions.md` - Agent guidelines

### 2. Verify Installation

```bash
# Check all dependencies
pip list | grep -E "agency-swarm|openai|pydantic"

# Verify agency loads
python3 -c "from agency import create_agency; create_agency(); print('OK')"

# Check for syntax errors
python3 -m py_compile agency.py
```

### 3. Test Minimal Example

```python
import asyncio
from agency import create_agency

async def test():
    agency = create_agency()
    response = await agency.get_response("Hello")
    print(response)

asyncio.run(test())
```

### 4. Common Solutions Checklist

- [ ] Python 3.12+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with `OPENAI_API_KEY`
- [ ] Agency imports successfully
- [ ] No syntax errors in custom code
- [ ] Virtual environment activated (if using)
- [ ] Correct PATH set for agency-swarm CLI

---

## Getting Help

If you're still experiencing issues after trying these solutions:

1. **Check Agency Swarm Documentation:**
   https://agency-swarm.ai

2. **Review Error Messages:**
   - Copy full error traceback
   - Note which agent/tool is failing
   - Check what operation was being performed

3. **Provide Debug Info:**
   - Python version: `python3 --version`
   - Agency Swarm version: `pip show agency-swarm`
   - Error message and full traceback
   - Steps to reproduce

---

## Quick Reference

### Verify Installation
```bash
python3 -c "from agency import create_agency; create_agency(); print('✓ OK')"
```

### Reset Environment
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Test Agency
```bash
python3 agency.py
# Then type: "test"
```

### Check Logs
```bash
# Enable debug output
export AGENCY_DEBUG=1
python3 agency.py
```

---

**Last Updated:** December 5, 2025
**Version:** 1.0.0
