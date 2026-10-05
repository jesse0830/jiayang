# WeChat iLink Bot QR Reconnection Reference

## Scenario
iLink Bot session expires (gateway log: `errcode=-14 errmsg=session timeout`). 
Standard QR code re-login flow attempts all fail — even after QR scan confirmed, 
the new bot token still returns session timeout on sendmessage.

## Root Cause
iLink's `get_bot_qrcode` → user scans → status=confirmed returns a **brand new bot account** 
every time. But the new bot's session is not actually established with the user's WeChat 
— All API calls (sendmessage, getupdates, getconfig) return -14.

Key facts discovered during debugging:
- Old token still works for `get_bot_qrcode` (ret=0) — token not revoked
- New bot also gets QR code successfully — but ALL subsequent APIs fail with -14
- Gateway shows `✓ weixin connected` but send still fails
- iLink server endpoints are alive (`ilinkai.weixin.qq.com` responds)

## The One Thing That Worked
After exhausting QR re-login (3+ attempts), the actual fix was:
1. **User sends a message to the bot from their phone WeChat** (随便打个字)
2. Gateway picks up the inbound message via long-polling getupdates
3. This re-establishes the bidirectional session
4. Outbound sendmessage starts working again automatically

## Why QR Re-Login Fails
The hypothesis: `get_bot_qrcode` without a valid session context creates orphan bot accounts. 
The QR scan happens on the user's phone but the session corridor between iLink server and 
the Hermes gateway never fully initializes because the bot token is replaced mid-flight.

## Recommended Sequence (when session timeout occurs)
```
1. Check gateway log: tail -20 ~/.hermes/logs/gateway.log | grep weixin
2. If it says "pausing for 10 minutes" → wait or restart gateway
3. Ask user to send ANY message to the bot from their phone
4. Watch gateway log for inbound message receipt
5. Once inbound works, outbound auto-recovers
6. If NO inbound after 10 min → try QR re-login:
   a. Generate QR with old token
   b. User scans on phone
   c. Update .env with new token/account_id
   d. Restart gateway
   e. If still fails → go back to step 3 (user sends message)
7. Last resort: Switch to WeCom Callback mode
```

## Important Caveat
Even when everything works: **Mac WeChat client does NOT receive iLink Bot messages**.
Phone WeChat receives them. Windows WeChat may receive them. This is WeChat's device 
sync policy, not a Hermes/iLink issue. The user must understand this limitation.
