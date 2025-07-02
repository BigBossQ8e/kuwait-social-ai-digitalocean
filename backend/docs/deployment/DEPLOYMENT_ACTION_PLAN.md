# 🚀 Kuwait Social AI - Deployment Action Plan & Verification

## 📋 Required Actions Checklist

### 1. ✅ **Python Version Upgrade** (Production)
**Current**: Unknown (likely 3.9.x based on venv_old_py39)  
**Target**: Python 3.11.10  
**Status**: ❓ Needs verification

```bash
# SSH to production and check
python3 --version

# If not 3.11.10, upgrade:
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

### 2. 📦 **Update Production Packages**
**Critical Package Updates Needed**:

| Package | Local | Production | Action |
|---------|-------|------------|--------|
| CrewAI | 0.100.0 | 0.1.0/0.5.0 | `pip install crewai==0.100.0` |
| langchain | 0.3.26 | 0.1.0 | `pip install langchain==0.3.26` |
| langchain-openai | 0.3.27 | 0.0.5 | `pip install langchain-openai==0.3.27` |
| langchain-anthropic | 0.3.16 | 0.1.1 | `pip install langchain-anthropic==0.3.16` |
| anthropic | 0.55.0 | Not installed | `pip install anthropic==0.55.0` |
| python-telegram-bot | 22.2 | 20.5 | `pip install python-telegram-bot==22.2` |

**Production Update Script**:
```bash
# Create backup first
cp requirements.txt requirements.backup.$(date +%Y%m%d)

# Update all packages
pip install -r requirements.txt --upgrade
```

### 3. 🤖 **Fix Telegram Bot**
**Issues**:
- API version mismatch (v20.5 → v22.2)
- No bot token configured
- Major breaking changes in API

**Actions**:
```python
# Update telegram_service.py for v22.2 API
# Key changes:
# - Update import statements
# - Fix async/await patterns
# - Update message handling
# - Configure bot token in .env
```

### 4. 📁 **Handle Untracked Files**
**Currently Untracked** (from git status):
```
backend/routes/ai_agents.py
backend/services/ai_agents/
backend/AI_AGENTS_IMPLEMENTATION_COMPLETE.md
backend/requirements-agents.txt
# ... and many more
```

**Decision Required**:
- **Option A**: Commit AI agent implementation
- **Option B**: Remove if not ready
- **Option C**: Add to .gitignore temporarily

### 5. 🧪 **Staging Environment Setup**
```bash
# Create staging subdomain
staging.kwtsocial.com

# Clone production environment
# Test all updates before production deployment
```

### 6. 📊 **Single Source of Truth**
Create `DEPLOYMENT_STATUS.json`:
```json
{
  "production": {
    "url": "kwtsocial.com",
    "python_version": "3.11.10",
    "last_deployment": "2024-01-20",
    "commit": "f38c41c",
    "features": {
      "ai_agents": true,
      "anthropic_api": true,
      "telegram_bot": false
    }
  },
  "local": {
    "python_version": "3.11.10",
    "commit": "latest",
    "features": {
      "ai_agents": true,
      "anthropic_api": true,
      "telegram_bot": false
    }
  }
}
```

## 🔍 Verification Checklist

### 1. **Verify ANTHROPIC_API_KEY in Production**
```bash
# SSH to production server
ssh user@kwtsocial.com

# Check if key exists
cd /var/www/kuwait-social-ai/backend
grep ANTHROPIC_API_KEY .env

# If missing, add:
echo "ANTHROPIC_API_KEY=sk-ant-api03-..." >> .env
```

### 2. **Verify Anthropic Package Installation**
```bash
# On production server
source venv/bin/activate
pip show anthropic

# If not installed:
pip install anthropic==0.55.0
```

### 3. **Update content_generator.py**
The file needs updating to use Anthropic. Current implementation only uses OpenAI.

**Required Changes**:
```python
# Add Anthropic support to content_generator.py
from anthropic import Anthropic

class ContentGenerator:
    def __init__(self):
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        # ... existing OpenAI client
    
    def generate_content_anthropic(self, prompt):
        response = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

## 🚦 Deployment Steps (In Order)

### Phase 1: Preparation (Local)
1. ✅ Review all untracked files
2. ✅ Decide what to commit/remove
3. ✅ Update content_generator.py for Anthropic
4. ✅ Fix Telegram bot for API v22.2
5. ✅ Run full test suite locally

### Phase 2: Staging Testing
1. 🔄 Set up staging environment
2. 🔄 Deploy current code to staging
3. 🔄 Test all features thoroughly
4. 🔄 Fix any issues found

### Phase 3: Production Preparation
1. 📋 Backup production database
2. 📋 Backup current code
3. 📋 Document rollback procedure

### Phase 4: Production Deployment
1. 🚀 Update Python to 3.11.10
2. 🚀 Update all packages
3. 🚀 Deploy new code
4. 🚀 Run migrations
5. 🚀 Restart services
6. 🚀 Verify all features

## ⚠️ Critical Checks Before Deployment

1. **CrewAI Compatibility**
   - Local uses @tool decorator (new)
   - Production uses @StructuredTool (old)
   - **MUST update production CrewAI first**

2. **Telegram Bot**
   - Currently broken in both environments
   - Either fix completely or disable

3. **Database Migrations**
   - Check for pending migrations
   - Run on staging first

4. **Environment Variables**
   - Ensure all .env variables match
   - Add ANTHROPIC_API_KEY to production

## 📝 Quick Verification Commands

```bash
# Run on production server
cd /var/www/kuwait-social-ai/backend
source venv/bin/activate

# Check Python version
python --version

# Check key packages
pip show crewai langchain anthropic python-telegram-bot

# Check environment variables
grep -E "(ANTHROPIC_API_KEY|AI_PROVIDER)" .env

# Test AI service
python test_ai_capabilities.py
```

## 🎯 Success Criteria

- [ ] Python 3.11.10 on production
- [ ] All packages match local versions
- [ ] ANTHROPIC_API_KEY configured
- [ ] AI services work with both providers
- [ ] Telegram bot fixed or properly disabled
- [ ] All tests pass in staging
- [ ] Zero downtime deployment
- [ ] Rollback plan ready

---

**Note**: This plan ensures safe deployment with minimal risk to production.