# Agentic Honeypot for Scam Detection

AI-powered honeypot system that detects scam messages and engages scammers using believable personas to extract intelligence.

## Features

- Advanced scam detection using Claude AI
- Multiple victim personas for realistic engagement
- Intelligence extraction (phone numbers, bank accounts, UPI IDs, URLs)
- Conversation memory and context tracking
- Secure API key authentication
- Real-time scam analysis

## API Endpoints

### `GET /test`
Test endpoint for validation
- **Headers**: `x-api-key: your_api_key`
- **Response**: Authentication confirmation

### `POST /api/honeypot/analyze`
Main analysis endpoint
- **Headers**: `x-api-key: your_api_key`
- **Body**:
```json
{
  "message": "Congratulations! You won $10000",
  "conversation_id": "conv_123"
}
```

## Environment Variables

- `ANTHROPIC_API_KEY`: Your Claude API key
- `HONEYPOT_API_KEY`: API key for authentication (default: hackathon_secret_key_12345)

## Local Development
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="your_key"
python main.py
```

## Deployment

Deploy to Render, Railway, or any Python hosting platform.