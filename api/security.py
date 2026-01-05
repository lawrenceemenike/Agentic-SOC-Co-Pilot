import re
import hashlib
import html

def sanitize_input(text: str) -> str:
    """
    Sanitizes input text by removing control characters, 
    stripping HTML tags, and normalizing whitespace.
    """
    if not text:
        return ""
    
    # 1. Remove control characters (except newlines/tabs if needed, but strict for now)
    # Allowing \n and \t might be necessary for formatted logs, but let's be strict first.
    # This regex removes everything in the range 0x00-0x1F and 0x7F, except \n (0x0A) and \t (0x09)
    text = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', text)
    
    # 2. Strip HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    
    # 3. Unescape HTML entities (to prevent double encoding issues, though stripping tags first handles most)
    text = html.unescape(text)
    
    # 4. Normalize whitespace
    text = " ".join(text.split())
    
    return text.strip()

def compute_payload_hash(payload: str) -> str:
    """
    Computes SHA256 hash of the raw payload.
    """
    return "sha256:" + hashlib.sha256(payload.encode('utf-8')).hexdigest()
