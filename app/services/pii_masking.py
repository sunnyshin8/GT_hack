"""
Comprehensive PII (Personally Identifiable Information) masking engine.
Detects and masks sensitive data for privacy protection.
"""
import re
import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import asyncio

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from app.core.cache import cache_get, cache_set
from app.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class PIIDetection:
    """Detected PII information."""
    pii_type: str
    value: str
    start_pos: int
    end_pos: int
    detection_method: str
    masked_value: str
    token: str

class PIIMaskingEngine:
    """Comprehensive PII masking engine with multiple detection methods."""
    
    def __init__(self):
        """Initialize the PII masking engine."""
        self.nlp = None
        self._initialize_spacy()
        
        # Indian name patterns (common first names)
        self.indian_names = {
            'male': [
                'rajesh', 'amit', 'rohit', 'vikram', 'suresh', 'deepak', 'anil', 'manoj',
                'prakash', 'vinod', 'ashok', 'ravi', 'mohan', 'krishna', 'ganesh', 'shiva',
                'arjun', 'kiran', 'ajay', 'rahul', 'ankit', 'nitin', 'sachin', 'vishal',
                'pradeep', 'mahesh', 'santosh', 'dinesh', 'ramesh', 'mukesh', 'yogesh'
            ],
            'female': [
                'priya', 'sneha', 'pooja', 'kavya', 'anita', 'meera', 'divya', 'riya',
                'sita', 'nisha', 'lakshmi', 'radha', 'geeta', 'shanti', 'indira', 'parvati',
                'saraswati', 'durga', 'kali', 'sunita', 'rekha', 'sonia', 'neha', 'asha',
                'usha', 'rita', 'lata', 'maya', 'kiran', 'jyoti', 'sapna'
            ]
        }
        
        # Regex patterns for Indian PII
        self.patterns = {
            'phone': r'(?:\+91[-\s]?)?(?:0?[6-9]\d{9}|\d{10})',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'aadhar': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'pan': r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
        }
        
    def _initialize_spacy(self):
        """Initialize spaCy NLP model if available."""
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy English model not found. Using regex-only detection.")
                self.nlp = None
        else:
            logger.warning("spaCy not available. Using regex-only detection.")
    
    def detect_pii_regex(self, text: str) -> List[PIIDetection]:
        """Detect PII using regex patterns."""
        detections = []
        
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group()
                start_pos = match.start()
                end_pos = match.end()
                
                # Create masked value
                if pii_type == 'phone':
                    masked_value = self._mask_phone(value)
                elif pii_type == 'email':
                    masked_value = self._mask_email(value)
                elif pii_type in ['aadhar', 'credit_card', 'pan']:
                    masked_value = '[REDACTED]'
                else:
                    masked_value = '*' * len(value)
                
                # Generate token
                token = f"[{pii_type.upper()}_MASKED_{len(detections)}]"
                
                detections.append(PIIDetection(
                    pii_type=pii_type,
                    value=value,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    detection_method='regex',
                    masked_value=masked_value,
                    token=token
                ))
        
        return detections
    
    def detect_pii_ner(self, text: str) -> List[PIIDetection]:
        """Detect PII using spaCy NER."""
        if not self.nlp:
            return []
        
        detections = []
        doc = self.nlp(text)
        person_count = 0
        org_count = 0
        
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG']:
                pii_type = ent.label_.lower()
                
                if pii_type == 'person':
                    token = f"[PERSON_MASKED_{person_count}]"
                    person_count += 1
                else:  # org
                    token = f"[ORG_MASKED_{org_count}]"
                    org_count += 1
                
                detections.append(PIIDetection(
                    pii_type=pii_type,
                    value=ent.text,
                    start_pos=ent.start_char,
                    end_pos=ent.end_char,
                    detection_method='ner',
                    masked_value=token,
                    token=token
                ))
        
        return detections
    
    def detect_indian_names(self, text: str) -> List[PIIDetection]:
        """Detect common Indian names using pattern matching."""
        detections = []
        words = text.split()
        
        for i, word in enumerate(words):
            word_clean = word.lower().strip('.,!?;:')
            
            # Check if it's a common Indian name
            if (word_clean in self.indian_names['male'] or 
                word_clean in self.indian_names['female']):
                
                # Find position in original text
                start_pos = text.lower().find(word_clean)
                if start_pos != -1:
                    end_pos = start_pos + len(word_clean)
                    token = f"[NAME_MASKED_{len(detections)}]"
                    
                    detections.append(PIIDetection(
                        pii_type='indian_name',
                        value=word_clean,
                        start_pos=start_pos,
                        end_pos=end_pos,
                        detection_method='name_pattern',
                        masked_value=token,
                        token=token
                    ))
        
        return detections
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone number keeping last 4 digits."""
        clean_phone = re.sub(r'[^\d+]', '', phone)
        if len(clean_phone) >= 10:
            if clean_phone.startswith('+91'):
                return f"+91-****-****-{clean_phone[-4:]}"
            else:
                return f"****-****-{clean_phone[-4:]}"
        return "****-****-****"
    
    def _mask_email(self, email: str) -> str:
        """Mask email showing first letter and domain."""
        parts = email.split('@')
        if len(parts) == 2:
            username = parts[0]
            domain = parts[1]
            if len(username) > 1:
                return f"{username[0]}****@{domain}"
            else:
                return f"****@{domain}"
        return "****@****.com"
    
    def detect_pii(self, text: str) -> List[PIIDetection]:
        """
        Detect PII using all available methods.
        
        Args:
            text: Input text to scan for PII
            
        Returns:
            List of PIIDetection objects with deduplicated results
        """
        all_detections = []
        
        # Method 1: Regex patterns
        regex_detections = self.detect_pii_regex(text)
        all_detections.extend(regex_detections)
        
        # Method 2: spaCy NER
        ner_detections = self.detect_pii_ner(text)
        all_detections.extend(ner_detections)
        
        # Method 3: Indian name patterns
        name_detections = self.detect_indian_names(text)
        all_detections.extend(name_detections)
        
        # Remove overlapping detections
        deduplicated = self._remove_overlapping_detections(all_detections)
        
        logger.info(f"Detected {len(deduplicated)} PII entities in text", 
                   extra={"detection_count": len(deduplicated)})
        
        return deduplicated
    
    def _remove_overlapping_detections(self, detections: List[PIIDetection]) -> List[PIIDetection]:
        """Remove overlapping PII detections, preferring higher confidence methods."""
        if not detections:
            return []
        
        # Sort by position
        sorted_detections = sorted(detections, key=lambda x: x.start_pos)
        
        # Method priority (higher number = higher priority)
        method_priority = {'regex': 3, 'ner': 2, 'name_pattern': 1}
        
        filtered = []
        for current in sorted_detections:
            # Check if this detection overlaps with any already accepted
            overlaps = False
            for accepted in filtered:
                if (current.start_pos < accepted.end_pos and 
                    current.end_pos > accepted.start_pos):
                    # There's an overlap
                    overlaps = True
                    
                    # Keep the one with higher priority method
                    current_priority = method_priority.get(current.detection_method, 0)
                    accepted_priority = method_priority.get(accepted.detection_method, 0)
                    
                    if current_priority > accepted_priority:
                        # Replace the accepted one with current
                        filtered.remove(accepted)
                        filtered.append(current)
                    break
            
            if not overlaps:
                filtered.append(current)
        
        return sorted(filtered, key=lambda x: x.start_pos)
    
    def mask_text(self, text: str, detected_pii: List[PIIDetection]) -> Tuple[str, Dict[str, Any]]:
        """
        Mask detected PII in text.
        
        Args:
            text: Original text
            detected_pii: List of detected PII entities
            
        Returns:
            Tuple of (masked_text, pii_map)
        """
        if not detected_pii:
            return text, {}
        
        # Sort by position in reverse order to maintain indices
        sorted_pii = sorted(detected_pii, key=lambda x: x.start_pos, reverse=True)
        
        masked_text = text
        pii_map = {}
        
        for detection in sorted_pii:
            # Generate hash for audit trail (never store actual PII)
            pii_hash = hashlib.sha256(detection.value.encode()).hexdigest()[:16]
            
            # Replace text with masked version
            masked_text = (masked_text[:detection.start_pos] + 
                          detection.masked_value + 
                          masked_text[detection.end_pos:])
            
            # Store mapping for potential unmasking (development only)
            pii_map[detection.token] = {
                'type': detection.pii_type,
                'hash': pii_hash,
                'method': detection.detection_method,
                'masked_value': detection.masked_value,
                'position': (detection.start_pos, detection.end_pos)
            }
        
        return masked_text, pii_map
    
    async def process_user_input(self, text: str) -> Dict[str, Any]:
        """
        Process user input by detecting and masking PII.
        
        Args:
            text: User input text
            
        Returns:
            Dict with masked text, session ID, and detection metadata
        """
        session_id = str(uuid.uuid4())
        
        # Detect PII
        detected_pii = self.detect_pii(text)
        
        # Mask text
        masked_text, pii_map = self.mask_text(text, detected_pii)
        
        # Store PII mapping in Redis for temporary use
        if pii_map:
            cache_key = f"pii_map:{session_id}"
            await cache_set(cache_key, pii_map, ttl=3600)  # 1 hour TTL
            
            # Store audit trail (hashes only)
            audit_data = {
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'pii_types': [detection.pii_type for detection in detected_pii],
                'detection_methods': list(set(d.detection_method for d in detected_pii)),
                'pii_count': len(detected_pii)
            }
            audit_key = f"pii_audit:{session_id}"
            await cache_set(audit_key, audit_data, ttl=86400)  # 24 hour TTL
            
            logger.info("PII detected and masked", 
                       extra={"session_id": session_id, 
                             "pii_count": len(detected_pii),
                             "pii_types": audit_data['pii_types']})
        
        return {
            'original_text': text,
            'masked_text': masked_text,
            'session_id': session_id,
            'pii_detected': [
                {
                    'type': detection.pii_type,
                    'method': detection.detection_method
                }
                for detection in detected_pii
            ],
            'pii_count': len(detected_pii)
        }
    
    async def unmask_response(self, masked_text: str, session_id: str) -> str:
        """
        Unmask response text using stored PII mapping.
        Note: This is for development/testing only.
        
        Args:
            masked_text: Text with masked PII tokens
            session_id: Session ID to retrieve PII mapping
            
        Returns:
            Text with PII unmasked (if mapping available)
        """
        cache_key = f"pii_map:{session_id}"
        pii_map = await cache_get(cache_key)
        
        if not pii_map:
            logger.warning("No PII mapping found for session", 
                          extra={"session_id": session_id})
            return masked_text
        
        unmasked_text = masked_text
        
        # Replace tokens with masked values (not original PII)
        for token, mapping in pii_map.items():
            if token in unmasked_text:
                unmasked_text = unmasked_text.replace(token, mapping['masked_value'])
        
        return unmasked_text

# Global PII masking engine instance
pii_engine = PIIMaskingEngine()

async def mask_user_input(text: str) -> Dict[str, Any]:
    """Convenience function to mask user input."""
    return await pii_engine.process_user_input(text)

async def unmask_response(masked_text: str, session_id: str) -> str:
    """Convenience function to unmask response."""
    return await pii_engine.unmask_response(masked_text, session_id)