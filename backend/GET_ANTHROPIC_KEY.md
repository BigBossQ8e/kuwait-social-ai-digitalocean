# 🔑 How to Get Your Anthropic API Key

## Steps to Get Claude API Access:

### 1. Go to Anthropic Console
Visit: https://console.anthropic.com/

### 2. Sign Up or Log In
- Create an account if you don't have one
- Use your business email for better support

### 3. Get API Key
- Go to "API Keys" section
- Click "Create Key"
- Name it: "Kuwait Social AI Production"
- Copy the key (starts with `sk-ant-api03-...`)

### 4. Add Credits
- Go to "Billing"
- Add payment method
- Start with $20-50 for testing

### 5. Update Your .env File
Replace `YOUR_ANTHROPIC_API_KEY_HERE` with your actual key:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

## Pricing (as of 2024):
- Claude 3.5 Sonnet: $3 per million input tokens
- Claude 3.5 Haiku: $0.25 per million input tokens
- Average social media post: ~500-1000 tokens

## Security Tips:
- Never commit API keys to git
- Use different keys for dev/prod
- Set spending limits in console
- Monitor usage regularly

Once you have your key, update the .env file and continue with testing!