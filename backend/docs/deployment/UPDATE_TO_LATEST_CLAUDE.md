# 🚀 Update to Latest Claude 3.5 Sonnet

## Current vs Latest Models

### What You Have:
- **Claude Model**: `claude-3-sonnet-20240229` (Older version)
- **OpenAI Model**: `gpt-4` (Good, but consider gpt-4-turbo)

### Latest Available:
- **Claude 3.5 Sonnet**: `claude-3-5-sonnet-20241022` (Latest, most capable)
- **Claude 3.5 Haiku**: `claude-3-5-haiku-20241022` (Faster, cheaper)
- **OpenAI**: `gpt-4-turbo-preview` or `gpt-4o` (Latest)

---

## Step 1: Update AI Service with Latest Models

```python
# services/ai_service.py - Updated version

class AIService:
    """Service for AI-powered content generation with latest models"""
    
    # Model configurations with latest versions
    MODELS = {
        'anthropic': {
            'premium': 'claude-3-5-sonnet-20241022',  # Best quality
            'standard': 'claude-3-5-haiku-20241022',   # Fast & cheap
            'legacy': 'claude-3-sonnet-20240229'       # Fallback
        },
        'openai': {
            'premium': 'gpt-4-turbo-preview',  # Latest GPT-4
            'standard': 'gpt-3.5-turbo',       # Fast & cheap
            'vision': 'gpt-4-vision-preview'   # For image analysis
        }
    }
    
    def __init__(self):
        # Initialize API clients
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.default_provider = os.getenv('AI_PROVIDER', 'anthropic')  # Prefer Claude
        self.model_tier = os.getenv('AI_MODEL_TIER', 'premium')  # premium or standard
        
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            
        if self.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
            
        # Log active configuration
        logger.info(f"AI Service initialized with provider: {self.default_provider}, tier: {self.model_tier}")
        
    def _get_model_name(self, provider: str, tier: str = None) -> str:
        """Get appropriate model based on provider and tier"""
        tier = tier or self.model_tier
        return self.MODELS.get(provider, {}).get(tier, 'claude-3-5-sonnet-20241022')
    
    def _generate_with_claude(self, system_prompt: str, user_prompt: str, model_override: str = None) -> str:
        """Generate content using latest Claude models"""
        model = model_override or self._get_model_name('anthropic')
        
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=2000,  # Increased for better responses
                temperature=0.8,  # Good for creative content
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            # Claude 3.5 returns content differently
            if hasattr(response.content[0], 'text'):
                return response.content[0].text.strip()
            else:
                return str(response.content[0]).strip()
                
        except Exception as e:
            logger.error(f"Claude generation error with {model}: {str(e)}")
            # Fallback to legacy model if needed
            if model != self.MODELS['anthropic']['legacy']:
                logger.info("Falling back to legacy Claude model")
                return self._generate_with_claude(system_prompt, user_prompt, 
                                                self.MODELS['anthropic']['legacy'])
            raise
    
    def _generate_with_openai(self, system_prompt: str, user_prompt: str, model_override: str = None) -> str:
        """Generate content using latest OpenAI models"""
        model = model_override or self._get_model_name('openai')
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
```

---

## Step 2: Update Environment Variables

```bash
# .env file updates

# AI Configuration
AI_PROVIDER=anthropic  # Prefer Claude for better quality
AI_MODEL_TIER=premium  # Use best models for production

# API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...  # Your Anthropic key
OPENAI_API_KEY=sk-proj-...          # Your OpenAI key

# Model Selection (optional overrides)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4-turbo-preview
```

---

## Step 3: Enhanced F&B Content with Claude 3.5

```python
# services/ai_service.py - F&B optimized prompts for Claude 3.5

def _build_system_prompt(self, platform: str, tone: str, business_type: Optional[str]) -> str:
    """Build system prompt optimized for Claude 3.5 Sonnet"""
    
    # Claude 3.5 responds better to structured prompts
    base_prompt = f"""<role>
You are a social media content expert specializing in Kuwait's F&B market.
You create content for {platform} that drives engagement and orders.
</role>

<context>
- Location: Kuwait (GMT+3)
- Currency: KWD (Kuwaiti Dinar)
- Languages: Arabic (primary), English (widely spoken)
- Culture: Islamic, family-oriented, food-loving
- Business days: Sunday-Thursday
- Weekend: Friday-Saturday
</context>

<tone>{tone}</tone>

<requirements>
1. ALWAYS mention "100% HALAL" prominently
2. Emphasize family-friendly atmosphere
3. Highlight delivery options (Talabat, Deliveroo)
4. Include price in KWD when relevant
5. Respect prayer times and cultural values
6. Use appropriate emojis for visual appeal
"""

    # Add F&B specific guidelines for Claude 3.5
    if business_type in F_B_BUSINESS_TYPES:
        base_prompt += f"""
<f_and_b_guidelines>
- Cuisine type: {business_type}
- Focus on: Taste, quality, freshness, ambiance
- Mention: Air conditioning, parking, family sections
- Popular times: {KUWAIT_MEAL_TIMES}
- Use food emojis: {F_B_EMOJIS}
- Include trending hashtags: {F_B_HASHTAGS}
</f_and_b_guidelines>
"""
    
    return base_prompt
```

---

## Step 4: Test the New Models

```python
# test_latest_claude.py

import os
from dotenv import load_dotenv
from services import get_ai_service

load_dotenv()

# Test latest Claude 3.5 Sonnet
ai_service = get_ai_service()

# Test 1: F&B Content Generation
result = ai_service.generate_content(
    prompt="Create a weekend special post for grilled seafood platter",
    platform="instagram",
    tone="enthusiastic",
    business_type="restaurant",
    include_arabic=True,
    include_hashtags=True
)

print("Claude 3.5 Sonnet Generated:")
print("=" * 50)
print(f"Content: {result['content'][:200]}...")
print(f"Character count: {result['character_count']}")
print(f"Hashtags: {result['hashtags'][:5]}")

# Test 2: Compare speeds
import time

# Premium model (Claude 3.5 Sonnet)
start = time.time()
premium_result = ai_service.generate_content("Quick lunch special", platform="instagram")
premium_time = time.time() - start

# Switch to standard model (Claude 3.5 Haiku)
ai_service.model_tier = 'standard'
start = time.time()
standard_result = ai_service.generate_content("Quick lunch special", platform="instagram")
standard_time = time.time() - start

print(f"\nSpeed Comparison:")
print(f"Claude 3.5 Sonnet: {premium_time:.2f}s")
print(f"Claude 3.5 Haiku: {standard_time:.2f}s (Faster!)")
```

---

## Step 5: Model Selection Strategy

```python
# services/ai_service.py - Smart model selection

def select_best_model(self, request_type: str, priority: str = 'quality') -> str:
    """Select best model based on use case"""
    
    model_selection = {
        # High quality needed
        'campaign_creation': 'claude-3-5-sonnet-20241022',
        'brand_voice': 'claude-3-5-sonnet-20241022',
        'complex_content': 'claude-3-5-sonnet-20241022',
        
        # Speed priority
        'simple_post': 'claude-3-5-haiku-20241022',
        'translation': 'claude-3-5-haiku-20241022',
        'hashtag_generation': 'claude-3-5-haiku-20241022',
        
        # Special cases
        'image_analysis': 'gpt-4-vision-preview',
        'code_generation': 'claude-3-5-sonnet-20241022'
    }
    
    return model_selection.get(request_type, self._get_model_name('anthropic'))

# Usage in generation
def generate_content(self, prompt: str, **kwargs) -> Dict:
    # Smart model selection
    if 'campaign' in prompt.lower():
        model = self.select_best_model('campaign_creation')
    elif kwargs.get('quick_response'):
        model = self.select_best_model('simple_post')
    else:
        model = None  # Use default
    
    # Generate with selected model
    if self.default_provider == 'anthropic':
        content = self._generate_with_claude(system_prompt, user_prompt, model)
```

---

## Benefits of Claude 3.5 Sonnet

### 1. **Superior Quality**
- Better understanding of context and nuance
- More creative and engaging content
- Better at following complex instructions

### 2. **Kuwait F&B Optimization**
- Understands cultural sensitivities better
- Generates more authentic local content
- Better Arabic language handling

### 3. **Cost Efficiency**
- Use Claude 3.5 Haiku for simple tasks (80% cheaper)
- Reserve Claude 3.5 Sonnet for complex content
- Smart routing saves money

### 4. **Speed Options**
- Sonnet: Best quality (1-2 seconds)
- Haiku: Super fast (0.3-0.5 seconds)

---

## Migration Checklist

- [ ] Update `ai_service.py` with new model names
- [ ] Test with your API keys
- [ ] Update environment variables
- [ ] Test F&B content generation
- [ ] Monitor performance and costs
- [ ] Update documentation

---

## Quick Implementation

```python
# Minimal change to use latest Claude
# In services/ai_service.py, just update this line:

def _generate_with_claude(self, system_prompt: str, user_prompt: str) -> str:
    """Generate content using Claude"""
    response = self.anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Update this line!
        max_tokens=2000,
        temperature=0.8,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return response.content[0].text.strip()
```

That's it! You're now using the latest and most capable Claude model! 🚀