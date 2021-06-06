import hmac
import hashlib

from config import twitch_subscription_secret
message_ids = []

def verify_header(messageSig: str, messageId: str, messageTimestamp: str, messageBody: bytes) -> bool:
    hmacMessage = messageId.encode() + messageTimestamp.encode() + messageBody
    sig = hmac.new(twitch_subscription_secret.encode(), hmacMessage, hashlib.sha256)
    expectedSigHeader = 'sha256=' + sig.hexdigest()
    return str(messageSig) == str(expectedSigHeader)  