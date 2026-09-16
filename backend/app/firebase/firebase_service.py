"""
Firebase Integration Service
Supports:
- Firebase Authentication (JWT/ID Token Verification)
- Cloud Firestore (users/{userId}/calls, alerts, settings, devices)
- Firebase Cloud Messaging (FCM Push Notifications)
- In-memory mock mode for local demo testing without live credentials
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("firebase_service")

# Try importing firebase_admin, with graceful fallback to Mock for Demo Mode
try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore, messaging
    HAS_FIREBASE_SDK = True
except ImportError:
    HAS_FIREBASE_SDK = False

class FirebaseManager:
    def __init__(self):
        self.is_initialized = False
        self.app = None
        self.db = None
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        
        # In-memory storage for Demo Mode
        self._mock_calls: Dict[str, Dict[str, Any]] = {}
        self._mock_alerts: Dict[str, Dict[str, Any]] = {}
        self._mock_settings: Dict[str, Dict[str, Any]] = {}
        self._mock_devices: Dict[str, List[str]] = {}
        self._mock_audit_logs: List[Dict[str, Any]] = []

        self._initialize()

    def _initialize(self):
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if HAS_FIREBASE_SDK and cred_path and os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                self.app = firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                self.is_initialized = True
                logger.info("Firebase Admin SDK initialized successfully with credentials.")
            except Exception as e:
                logger.warning(f"Failed to initialize Firebase Admin SDK: {e}. Falling back to Demo Mode.")
                self.is_initialized = False
        else:
            logger.info("Firebase credentials not configured or running in Demo Mode. Using safe Mock Store.")

    async def verify_id_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifies Firebase ID token or accepts demo tokens."""
        if self.demo_mode or not self.is_initialized:
            if token.startswith("demo_") or token == "mock-token" or len(token) > 5:
                return {
                    "uid": "user_demo_manish_123",
                    "email": "manish@aicallagent.com",
                    "name": "Manish Kumar"
                }
            return None

        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            logger.error(f"Error verifying Firebase token: {e}")
            return None

    # --- FIRESTORE CALL METHODS ---
    async def save_call(self, user_id: str, call_data: Dict[str, Any]) -> str:
        call_id = call_data.get("callId") or f"call_{int(datetime.now(timezone.utc).timestamp())}"
        call_data["callId"] = call_id
        if "createdAt" not in call_data:
            call_data["createdAt"] = datetime.now(timezone.utc).isoformat()

        if self.is_initialized and self.db:
            doc_ref = self.db.collection("users").document(user_id).collection("calls").document(call_id)
            doc_ref.set(call_data)
        else:
            key = f"{user_id}:{call_id}"
            self._mock_calls[key] = call_data
            
        return call_id

    async def get_call(self, user_id: str, call_id: str) -> Optional[Dict[str, Any]]:
        if self.is_initialized and self.db:
            doc = self.db.collection("users").document(user_id).collection("calls").document(call_id).get()
            return doc.to_dict() if doc.exists else None
        key = f"{user_id}:{call_id}"
        return self._mock_calls.get(key)

    async def get_all_calls(self, user_id: str) -> List[Dict[str, Any]]:
        if self.is_initialized and self.db:
            docs = self.db.collection("users").document(user_id).collection("calls").order_by("createdAt", direction=firestore.Query.DESCENDING).stream()
            return [doc.to_dict() for doc in docs]
        prefix = f"{user_id}:"
        calls = [v for k, v in self._mock_calls.items() if k.startswith(prefix)]
        return sorted(calls, key=lambda x: x.get("createdAt", ""), reverse=True)

    async def delete_call(self, user_id: str, call_id: str) -> bool:
        if self.is_initialized and self.db:
            self.db.collection("users").document(user_id).collection("calls").document(call_id).delete()
            return True
        key = f"{user_id}:{call_id}"
        if key in self._mock_calls:
            del self._mock_calls[key]
            return True
        return False

    async def delete_call_transcript(self, user_id: str, call_id: str) -> bool:
        if self.is_initialized and self.db:
            doc_ref = self.db.collection("users").document(user_id).collection("calls").document(call_id)
            doc_ref.update({"transcript": None, "messages": []})
            return True
        key = f"{user_id}:{call_id}"
        if key in self._mock_calls:
            self._mock_calls[key]["transcript"] = None
            self._mock_calls[key]["messages"] = []
            return True
        return False

    async def delete_all_calls(self, user_id: str) -> int:
        count = 0
        if self.is_initialized and self.db:
            docs = self.db.collection("users").document(user_id).collection("calls").stream()
            for doc in docs:
                doc.reference.delete()
                count += 1
        else:
            keys_to_del = [k for k in self._mock_calls if k.startswith(f"{user_id}:")]
            count = len(keys_to_del)
            for k in keys_to_del:
                del self._mock_calls[k]
        return count

    # --- ALERTS METHODS ---
    async def save_alert(self, user_id: str, alert_data: Dict[str, Any]) -> str:
        alert_id = alert_data.get("alertId") or f"alert_{int(datetime.now(timezone.utc).timestamp())}"
        alert_data["alertId"] = alert_id
        if "createdAt" not in alert_data:
            alert_data["createdAt"] = datetime.now(timezone.utc).isoformat()

        if self.is_initialized and self.db:
            doc_ref = self.db.collection("users").document(user_id).collection("alerts").document(alert_id)
            doc_ref.set(alert_data)
        else:
            self._mock_alerts[f"{user_id}:{alert_id}"] = alert_data
        return alert_id

    async def get_alerts(self, user_id: str) -> List[Dict[str, Any]]:
        if self.is_initialized and self.db:
            docs = self.db.collection("users").document(user_id).collection("alerts").order_by("createdAt", direction=firestore.Query.DESCENDING).stream()
            return [doc.to_dict() for doc in docs]
        prefix = f"{user_id}:"
        alerts = [v for k, v in self._mock_alerts.items() if k.startswith(prefix)]
        return sorted(alerts, key=lambda x: x.get("createdAt", ""), reverse=True)

    async def delete_alert(self, user_id: str, alert_id: str) -> bool:
        if self.is_initialized and self.db:
            self.db.collection("users").document(user_id).collection("alerts").document(alert_id).delete()
            return True
        key = f"{user_id}:{alert_id}"
        if key in self._mock_alerts:
            del self._mock_alerts[key]
            return True
        return False

    # --- FCM PUSH NOTIFICATIONS ---
    async def send_fcm_notification(self, user_id: str, title: str, body: str, data: Optional[Dict[str, str]] = None) -> bool:
        """Sends an urgent call push notification to the owner's Android app."""
        logger.info(f"Dispatching FCM to user {user_id}: Title='{title}', Body='{body}'")
        if self.is_initialized and HAS_FIREBASE_SDK:
            try:
                # Retrieve device tokens
                devices_ref = self.db.collection("users").document(user_id).collection("devices").stream()
                tokens = [d.to_dict().get("fcmToken") for d in devices_ref if d.to_dict().get("fcmToken")]
                
                if not tokens:
                    logger.warning(f"No FCM tokens found for user {user_id}")
                    return False
                
                message = messaging.MulticastMessage(
                    notification=messaging.Notification(title=title, body=body),
                    data=data or {},
                    tokens=tokens
                )
                response = messaging.send_multicast(message)
                logger.info(f"FCM Multicast sent: {response.success_count} successes, {response.failure_count} failures")
                return response.success_count > 0
            except Exception as e:
                logger.error(f"FCM send error: {e}")
                return False
        else:
            # In demo mode, log and record successful simulation
            logger.info(f"[DEMO FCM SENT] {title} - {body} (Payload: {data})")
            return True

firebase_manager = FirebaseManager()
