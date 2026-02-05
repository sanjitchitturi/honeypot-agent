import json
import re
import random
from typing import Dict, List, Tuple
from config import *

class HoneypotAgent:
    """
    DEMO MODE: Simulates AI responses without calling external APIs
    Perfect for testing API structure and endpoints
    """
    def __init__(self):
        self.conversation_history: Dict[str, List[Dict]] = {}
        self.demo_responses = {
            "prize_scam": [
                "Oh my goodness, really?! I can't believe I won! This is so exciting! How exactly do I claim this prize? Do I need to provide any verification first?",
                "Wow, $50,000! That's amazing! What do I need to do? Should I send you my bank details now?",
                "This is wonderful news! I've never won anything before. Can you tell me more about how this works?"
            ],
            "phishing": [
                "Oh no, my account is compromised? That's terrible! What should I do? Should I click that link you sent?",
                "I'm so worried about my account. Can you help me secure it? What information do you need from me?",
                "Thank you for letting me know. I'll click on that link right away to verify my account."
            ],
            "investment_fraud": [
                "This investment opportunity sounds incredible! A 50% return in just one month? How do I get started?",
                "I've been looking for good investment options. Can you tell me more about this? How much should I invest initially?",
                "That sounds too good to be true, but I trust you! What's the minimum investment amount?"
            ],
            "tech_support_scam": [
                "Oh dear, my computer has a virus? I didn't know! How can you help me fix it? Do you need remote access?",
                "Thank you for calling! Yes, my computer has been running slowly. What do I need to do to fix it?",
                "A virus? That's scary! Should I give you access to my computer to remove it?"
            ],
            "default": [
                "That sounds interesting! Can you tell me more about this?",
                "I see. How exactly does this work? I want to make sure I understand correctly.",
                "Okay, I'm listening. What do I need to do next?"
            ]
        }
    
    def analyze_message(self, message: str, conversation_id: str = None) -> Dict:
        """
        Demo analysis function - detects scams using keyword matching
        and generates realistic responses
        """
        # Step 1: Detect if it's a scam using keywords
        is_scam, confidence, scam_type, reasoning = self._detect_scam_demo(message)
        
        # Step 2: Extract intelligence from the message
        extracted_intel = self._extract_intelligence(message)
        
        # Step 3: Generate believable response if it's a scam
        ai_response = ""
        persona_used = None
        
        if is_scam and confidence >= SCAM_CONFIDENCE_THRESHOLD:
            ai_response, persona_used = self._generate_demo_response(scam_type)
        
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
    
    def _detect_scam_demo(self, message: str) -> Tuple[bool, float, str, str]:
        """
        Demo scam detection using keyword patterns
        """
        message_lower = message.lower()
        
        # Prize/Lottery scams
        if any(word in message_lower for word in ['won', 'winner', 'prize', 'lottery', 'congratulations', 'claim']):
            return True, 0.92, "prize_scam", "Message contains typical prize scam indicators: offering unexpected prizes/winnings and urgency to claim"
        
        # Phishing
        if any(word in message_lower for word in ['verify', 'account', 'suspended', 'click', 'link', 'confirm', 'urgent']):
            return True, 0.88, "phishing", "Message shows phishing characteristics: requests to verify account or click links with sense of urgency"
        
        # Investment fraud
        if any(word in message_lower for word in ['investment', 'profit', 'return', 'crypto', 'bitcoin', 'opportunity', 'guaranteed']):
            return True, 0.85, "investment_fraud", "Message exhibits investment fraud patterns: promises of high returns or guaranteed profits"
        
        # Tech support scam
        if any(word in message_lower for word in ['virus', 'infected', 'tech support', 'microsoft', 'apple', 'refund', 'computer']):
            return True, 0.90, "tech_support_scam", "Message matches tech support scam indicators: claims of computer issues or need for technical assistance"
        
        # Impersonation
        if any(word in message_lower for word in ['bank', 'irs', 'government', 'official', 'payment', 'tax', 'penalty']):
            return True, 0.87, "impersonation", "Message appears to impersonate official organizations: banks, government agencies, or authorities"
        
        # Romance scam
        if any(word in message_lower for word in ['love', 'darling', 'money', 'emergency', 'hospital', 'stranded']):
            return True, 0.83, "romance_scam", "Message contains romance scam elements: emotional manipulation combined with financial requests"
        
        # Job scam
        if any(word in message_lower for word in ['job', 'work from home', 'easy money', 'hiring', 'recruitment fee']):
            return True, 0.86, "job_scam", "Message shows job scam characteristics: promises of easy money or requests for upfront fees"
        
        # Check for bank account, UPI, payment requests
        if any(word in message_lower for word in ['bank account', 'account number', 'upi', 'send money', 'transfer']):
            return True, 0.94, "payment_request_scam", "Message directly requests financial information or money transfer - major red flag"
        
        # Not a scam
        return False, 0.15, "legitimate", "Message appears to be legitimate communication with no obvious scam indicators"
    
    def _generate_demo_response(self, scam_type: str) -> Tuple[str, str]:
        """
        Generates a demo victim response based on scam type
        """
        # Select persona
        if scam_type in ["prize_scam", "investment_fraud"]:
            persona_key = "desperate"
        elif scam_type in ["tech_support_scam", "phishing"]:
            persona_key = "elderly"
        else:
            persona_key = "young_professional"
        
        # Get appropriate response
        responses = self.demo_responses.get(scam_type, self.demo_responses["default"])
        response = random.choice(responses)
        
        return response, persona_key
    
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
        payment_keywords = ["paytm", "phonepe", "gpay", "google pay", "paypal", "venmo", 
                           "western union", "moneygram", "bank transfer", "wire transfer", 
                           "bitcoin", "crypto", "zelle", "cashapp"]
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
            return {
                "phone_numbers": [],
                "bank_accounts": [],
                "ifsc_codes": [],
                "upi_ids": [],
                "urls": [],
                "emails": [],
                "payment_methods": []
            }
        
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
