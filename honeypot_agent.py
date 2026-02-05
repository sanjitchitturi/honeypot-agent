import anthropic
import json
import re
from typing import Dict, List, Tuple
from config import *

class HoneypotAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    def analyze_message(self, message: str, conversation_id: str = None) -> Dict:
        """
        Main analysis function - detects scams and generates responses
        """
        # Step 1: Detect if it's a scam
        is_scam, confidence, scam_type, reasoning = self._detect_scam(message)
        
        # Step 2: Extract intelligence from the message
        extracted_intel = self._extract_intelligence(message)
        
        # Step 3: Generate believable response if it's a scam
        ai_response = ""
        persona_used = None
        
        if is_scam and confidence >= SCAM_CONFIDENCE_THRESHOLD:
            ai_response, persona_used = self._generate_victim_response(
                message, 
                scam_type, 
                conversation_id
            )
        
        # Step 4: Store conversation history
        if conversation_id:
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []
            
            self.conversation_history[conversation_id].append({
                "scammer_message": message,
                "our_response": ai_response,
                "intelligence": extracted_intel
            })
        
        return {
            "is_scam": is_scam,
            "confidence": round(confidence, 2),
            "scam_type": scam_type,
            "ai_response": ai_response,
            "persona_used": persona_used,
            "extracted_intelligence": extracted_intel,
            "reasoning": reasoning,
            "conversation_turn": len(self.conversation_history.get(conversation_id, [])),
            "total_intelligence_collected": self._aggregate_intelligence(conversation_id)
        }
    
    def _detect_scam(self, message: str) -> Tuple[bool, float, str, str]:
        """
        Uses Claude to detect if message is a scam
        """
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=800,
                temperature=0.3,  # Lower temperature for more consistent detection
                messages=[{
                    "role": "user",
                    "content": f"""You are an expert scam detection system. Analyze this message:

MESSAGE: "{message}"

Determine:
1. Is this a scam/phishing/fraud attempt?
2. What type of scam is it?
3. Confidence level (0.0 to 1.0)

Common scam types:
- phishing (fake links, credential theft)
- prize_scam (fake lottery, rewards)
- impersonation (pretending to be bank, government, company)
- investment_fraud (fake investments, crypto scams)
- romance_scam (fake relationships for money)
- tech_support_scam (fake technical issues)
- job_scam (fake job offers requiring payment)
- donation_scam (fake charity)

Respond ONLY in this JSON format:
{{
    "is_scam": true/false,
    "confidence": 0.0-1.0,
    "scam_type": "type_from_list_above",
    "reasoning": "brief explanation of why this is/isn't a scam"
}}"""
                }]
            )
            
            response_text = response.content[0].text
            result = self._extract_json(response_text)
            
            return (
                result.get("is_scam", False),
                float(result.get("confidence", 0.5)),
                result.get("scam_type", "unknown"),
                result.get("reasoning", "Analysis completed")
            )
            
        except Exception as e:
            print(f"Error in scam detection: {e}")
            return False, 0.0, "error", f"Detection failed: {str(e)}"
    
    def _generate_victim_response(self, message: str, scam_type: str, conversation_id: str) -> Tuple[str, str]:
        """
        Generates a believable victim response to engage the scammer
        """
        # Select appropriate persona based on scam type
        if scam_type in ["prize_scam", "investment_fraud"]:
            persona_key = "desperate"
        elif scam_type in ["tech_support_scam", "phishing"]:
            persona_key = "elderly"
        else:
            persona_key = "young_professional"
        
        persona = VICTIM_PERSONAS[persona_key]
        
        # Get conversation history for context
        history = self.conversation_history.get(conversation_id, [])
        context = ""
        if history:
            context = f"\n\nPrevious conversation:\n"
            for turn in history[-3:]:  # Last 3 turns for context
                context += f"Scammer: {turn['scammer_message']}\n"
                context += f"You: {turn['our_response']}\n"
        
        try:
            response = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                messages=[{
                    "role": "user",
                    "content": f"""You are roleplaying as a potential scam victim to extract information from scammers.

PERSONA:
- Name: {persona['name']}
- Age: {persona['age']}
- Traits: {persona['traits']}
- Communication style: {persona['style']}

SCAM TYPE: {scam_type}

SCAMMER'S MESSAGE: "{message}"{context}

YOUR GOAL:
1. Respond as {persona['name']} would - stay IN CHARACTER
2. Show interest to keep the scammer engaged
3. Ask questions that might reveal: bank details, UPI IDs, phone numbers, links, payment methods
4. Sound believable - not too eager, show some natural hesitation
5. DO NOT reveal you know it's a scam
6. Gradually increase trust to extract more information

Example approaches:
- Ask how the process works
- Express concern about security (to get them to "reassure" you with details)
- Ask for verification (might reveal fake credentials)
- Mention you need to check with someone (buys time, tests their urgency)

Respond ONLY with the message you would send (no JSON, no explanation, just the response as {persona['name']})."""
                }]
            )
            
            victim_response = response.content[0].text.strip()
            return victim_response, persona_key
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "That sounds interesting! Can you tell me more about this?", persona_key
    
    def _extract_intelligence(self, message: str) -> Dict[str, List[str]]:
        """
        Extracts intelligence using regex patterns
        """
        intel = {
            "phone_numbers": [],
            "bank_accounts": [],
            "ifsc_codes": [],
            "upi_ids": [],
            "urls": [],
            "emails": [],
            "payment_methods": []
        }
        
        # Extract using patterns
        for key, pattern in INTELLIGENCE_PATTERNS.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if key == "phone_number":
                intel["phone_numbers"] = list(set(matches))
            elif key == "bank_account":
                intel["bank_accounts"] = list(set(matches))
            elif key == "ifsc_code":
                intel["ifsc_codes"] = list(set(matches))
            elif key == "upi_id":
                intel["upi_ids"] = list(set(matches))
            elif key == "url":
                intel["urls"] = list(set(matches))
            elif key == "email":
                intel["emails"] = list(set(matches))
        
        # Detect payment method mentions
        payment_keywords = ["paytm", "phonepe", "gpay", "google pay", "paypal", "venmo", "western union", "moneygram", "bank transfer", "wire transfer", "bitcoin", "crypto"]
        for keyword in payment_keywords:
            if keyword.lower() in message.lower():
                intel["payment_methods"].append(keyword)
        
        intel["payment_methods"] = list(set(intel["payment_methods"]))
        
        return intel
    
    def _aggregate_intelligence(self, conversation_id: str) -> Dict:
        """
        Aggregates all intelligence collected in a conversation
        """
        if not conversation_id or conversation_id not in self.conversation_history:
            return {}
        
        aggregated = {
            "phone_numbers": set(),
            "bank_accounts": set(),
            "ifsc_codes": set(),
            "upi_ids": set(),
            "urls": set(),
            "emails": set(),
            "payment_methods": set()
        }
        
        for turn in self.conversation_history[conversation_id]:
            intel = turn.get("intelligence", {})
            for key in aggregated.keys():
                aggregated[key].update(intel.get(key, []))
        
        # Convert sets back to lists for JSON serialization
        return {k: list(v) for k, v in aggregated.items()}
    
    def _extract_json(self, text: str) -> Dict:
        """
        Safely extracts JSON from Claude's response
        """
        try:
            # Try to find JSON in the text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(text)
        except:
            return {}