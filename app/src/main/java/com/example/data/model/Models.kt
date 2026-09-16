package com.example.data.model

enum class UrgencyLevel {
    LOW, MEDIUM, HIGH, CRITICAL
}

enum class CallStatus(val label: String) {
    COMPLETED("Completed"),
    ESCALATED("Escalated"),
    TRANSFERRED("Transferred"),
    FAILED("Failed"),
    MISSED("Missed"),
    SPAM("Spam")
}

enum class ContactCategory(val label: String) {
    FAMILY("Family"),
    FRIEND("Friend"),
    CLIENT("Client"),
    COLLEGE("College"),
    BUSINESS("Business"),
    OTHER("Other")
}

enum class AIPersonalityPreset(val title: String, val description: String) {
    PROFESSIONAL("Professional", "Polite, structured, and formal. Ideal for business and executive phone lines."),
    FRIENDLY("Friendly", "Warm, welcoming, empathetic, and approachable."),
    CONCISE("Concise", "Direct, high-speed, and ultra-succinct. Under 2 sentences per turn."),
    BUSINESS("Business", "Focused on client requirements, deadlines, budgets, and deliverables."),
    PERSONAL_ASSISTANT("Personal Assistant", "Acts as an executive secretary, protecting owner focus and triaging callers.")
}

data class TranscriptMessage(
    val speaker: String, // "AI" or "Caller"
    val content: String,
    val timestamp: String
)

data class CallRecord(
    val id: String,
    val callerName: String,
    val callerNumber: String,
    val timestampFormatted: String,
    val durationSeconds: Int,
    val reason: String,
    val urgency: UrgencyLevel,
    val summary: String,
    val importantDetails: String,
    val actionRequired: String,
    val callbackRequired: Boolean,
    val status: CallStatus,
    val messages: List<TranscriptMessage> = emptyList(),
    val isAlertSent: Boolean = false,
    val createdAtEpoch: Long = System.currentTimeMillis()
)

data class VipContact(
    val id: String,
    val name: String,
    val phoneNumber: String,
    val category: ContactCategory,
    val notes: String = "",
    val alwaysAlert: Boolean = false,
    val alwaysTransfer: Boolean = false,
    val isBlocked: Boolean = false
)

data class UrgencyRule(
    val id: String,
    val title: String,
    val conditionType: String, // "URGENCY_LEVEL", "VIP_CALLER", "KEYWORD", "MARKETING_SPAM"
    val conditionValue: String,
    val action: String, // "SMS", "CALL_TRANSFER", "NO_ALERT"
    val isEnabled: Boolean = true
)

data class KnowledgeItem(
    val id: String,
    val title: String,
    val category: String, // "Working Hours", "Services", "Pricing", "Appointments", "FAQ"
    val content: String
)

data class AgentSettings(
    val isAgentEnabled: Boolean = true,
    val aiPhoneNumber: String = "+1 (800) 555-0199",
    val ownerPhoneNumber: String = "+1 (987) 654-3210",
    val greeting: String = "Hello, you've reached Manish's AI assistant. Manish isn't available to take the call right now. I can help you with your request and pass along an important message. How can I help?",
    val personality: AIPersonalityPreset = AIPersonalityPreset.PROFESSIONAL,
    val customSystemPrompt: String = "",
    val languageMode: String = "English", // "English", "Hindi", "Hinglish", "Auto"
    val maxCallDurationMinutes: Int = 5,
    val urgencyThreshold: UrgencyLevel = UrgencyLevel.HIGH,
    val alertTemplate: String = "URGENT CALL ALERT\n\nCaller: {caller}\nNumber: {number}\nUrgency: {urgency}\n\nReason:\n{reason}\n\nSummary:\n{summary}\n\nTime:\n{time}\n\nPlease review in AI Call Agent app.",
    val smsCooldownMinutes: Int = 5,
    val telephonyProvider: String = "Twilio",
    val smsProvider: String = "Twilio",
    val isTranscriptStorageEnabled: Boolean = true,
    val isAudioRecordingEnabled: Boolean = false,
    val retentionDays: Int = 90,
    val isTransferEnabled: Boolean = true,
    val transferNumber: String = "+1 (987) 654-3210"
)

data class SmsAlertLog(
    val id: String,
    val callerName: String,
    val callerNumber: String,
    val urgency: UrgencyLevel,
    val formattedMessage: String,
    val timestamp: String,
    val status: String = "DELIVERED",
    val provider: String = "Twilio"
)

data class IntegrationStatusItem(
    val name: String,
    val type: String,
    val isConnected: Boolean,
    val statusText: String,
    val latencyMs: Int,
    val details: String
)
