package com.example.data.repository

import com.example.data.model.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.text.SimpleDateFormat
import java.util.*

object CallAgentRepository {
    private val timeFormat = SimpleDateFormat("hh:mm a", Locale.getDefault())
    private val dateFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())

    private val _settings = MutableStateFlow(AgentSettings())
    val settings: StateFlow<AgentSettings> = _settings.asStateFlow()

    private val _calls = MutableStateFlow<List<CallRecord>>(emptyList())
    val calls: StateFlow<List<CallRecord>> = _calls.asStateFlow()

    private val _contacts = MutableStateFlow<List<VipContact>>(emptyList())
    val contacts: StateFlow<List<VipContact>> = _contacts.asStateFlow()

    private val _rules = MutableStateFlow<List<UrgencyRule>>(emptyList())
    val rules: StateFlow<List<UrgencyRule>> = _rules.asStateFlow()

    private val _knowledgeBase = MutableStateFlow<List<KnowledgeItem>>(emptyList())
    val knowledgeBase: StateFlow<List<KnowledgeItem>> = _knowledgeBase.asStateFlow()

    private val _smsLogs = MutableStateFlow<List<SmsAlertLog>>(emptyList())
    val smsLogs: StateFlow<List<SmsAlertLog>> = _smsLogs.asStateFlow()

    private val _latestAlert = MutableStateFlow<SmsAlertLog?>(null)
    val latestAlert: StateFlow<SmsAlertLog?> = _latestAlert.asStateFlow()

    init {
        seedInitialData()
    }

    private fun seedInitialData() {
        val now = System.currentTimeMillis()

        // 1. Seed Calls
        val demoCalls = listOf(
            CallRecord(
                id = "call_101",
                callerName = "Rahul Verma",
                callerNumber = "+91 98765 43210",
                timestampFormatted = "Today, 10:42 AM",
                durationSeconds = 64,
                reason = "Website outage - Checkout failure",
                urgency = UrgencyLevel.HIGH,
                summary = "Rahul reported that the production web storefront is unavailable and customers cannot complete orders.",
                importantDetails = "Checkout service returning HTTP 500. Immediate fix requested.",
                actionRequired = "Owner should inspect cloud hosting and restart payment webhook container.",
                callbackRequired = true,
                status = CallStatus.ESCALATED,
                messages = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant. Manish isn't available right now. How can I help you?", "10:41 AM"),
                    TranscriptMessage("Caller", "Hello! This is Rahul. The website is completely down and customers can't place orders! We need this fixed immediately.", "10:41 AM"),
                    TranscriptMessage("AI", "I understand the urgency regarding the website outage and checkout blockage. I am flagging this as a HIGH priority alert and dispatching an urgent SMS to Manish right now.", "10:42 AM"),
                    TranscriptMessage("Caller", "Thank you, please make sure he gets the notification ASAP.", "10:42 AM"),
                    TranscriptMessage("AI", "I have logged the incident and notified Manish. He will review this immediately. Thank you Rahul.", "10:42 AM")
                ),
                isAlertSent = true,
                createdAtEpoch = now - 1000 * 60 * 35
            ),
            CallRecord(
                id = "call_102",
                callerName = "Vikram Sethi",
                callerNumber = "+91 98445 56677",
                timestampFormatted = "Today, 09:15 AM",
                durationSeconds = 48,
                reason = "Client contract signing deadline today",
                urgency = UrgencyLevel.HIGH,
                summary = "Vikram from Acme Corp called regarding project contract countersign deadline before 4:00 PM today.",
                importantDetails = "Acme Corp contract requires Manish's digital signature before end of banking hours.",
                actionRequired = "Review digital agreement link sent to email and sign.",
                callbackRequired = true,
                status = CallStatus.ESCALATED,
                messages = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant. How may I direct your call?", "09:14 AM"),
                    TranscriptMessage("Caller", "Hi, Vikram here from Acme Corp. We have our contract deadline today and need Manish's sign-off before 4 PM.", "09:14 AM"),
                    TranscriptMessage("AI", "Understood Vikram. Given today's signing deadline, I'm escalating this directly to Manish so he can review and sign the contract.", "09:15 AM")
                ),
                isAlertSent = true,
                createdAtEpoch = now - 1000 * 60 * 120
            ),
            CallRecord(
                id = "call_103",
                callerName = "Priya Sharma",
                callerNumber = "+91 98112 23344",
                timestampFormatted = "Yesterday, 04:30 PM",
                durationSeconds = 52,
                reason = "Consultation enquiry and working hours",
                urgency = UrgencyLevel.LOW,
                summary = "Priya enquired about Manish's working hours and software architecture consulting availability for next week.",
                importantDetails = "Looking for a 2-hour technical review session next Tuesday.",
                actionRequired = "Send calendar link for next week's consultation slots.",
                callbackRequired = false,
                status = CallStatus.COMPLETED,
                messages = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant. How can I help?", "04:30 PM"),
                    TranscriptMessage("Caller", "Hi! I wanted to check what Manish's working hours are and if he has slots for an architecture consultation next week.", "04:30 PM"),
                    TranscriptMessage("AI", "Manish's office hours are Monday through Friday, 9:00 AM to 6:00 PM. I have noted your consultation request and will forward it to him.", "04:31 PM"),
                    TranscriptMessage("Caller", "That's perfect. My name is Priya Sharma. Thank you!", "04:31 PM")
                ),
                isAlertSent = false,
                createdAtEpoch = now - 1000 * 60 * 60 * 25
            ),
            CallRecord(
                id = "call_104",
                callerName = "Dr. Mehta's Clinic",
                callerNumber = "+91 98110 02233",
                timestampFormatted = "2 days ago, 11:20 AM",
                durationSeconds = 38,
                reason = "Dental appointment rescheduling",
                urgency = UrgencyLevel.MEDIUM,
                summary = "Dr. Mehta's clinic called to confirm rescheduling of tomorrow's dental checkup to Friday 3:00 PM.",
                importantDetails = "New slot confirmed for Friday 3:00 PM.",
                actionRequired = "Add rescheduled dental slot to personal calendar.",
                callbackRequired = false,
                status = CallStatus.COMPLETED,
                messages = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant. How can I help?", "11:20 AM"),
                    TranscriptMessage("Caller", "This is Dr. Mehta's clinic calling to confirm moving Manish's dental appointment to Friday at 3 PM.", "11:20 AM"),
                    TranscriptMessage("AI", "Thank you. I have logged the rescheduled appointment for Friday 3:00 PM and will notify Manish.", "11:21 AM")
                ),
                isAlertSent = false,
                createdAtEpoch = now - 1000 * 60 * 60 * 48
            ),
            CallRecord(
                id = "call_105",
                callerName = "Telemarketer (Spam)",
                callerNumber = "+91 98000 00001",
                timestampFormatted = "3 days ago, 02:10 PM",
                durationSeconds = 24,
                reason = "Pre-approved personal loan promotion",
                urgency = UrgencyLevel.LOW,
                summary = "Automated promotional call offering pre-approved personal credit loan.",
                importantDetails = "Cold sales pitch. Automatically flagged by Spam engine.",
                actionRequired = "No action required. Caller number automatically added to blocklist.",
                callbackRequired = false,
                status = CallStatus.SPAM,
                messages = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant.", "02:10 PM"),
                    TranscriptMessage("Caller", "Congratulations! You are pre-approved for an instant loan of 10 Lakhs at special rate...", "02:10 PM"),
                    TranscriptMessage("AI", "Manish does not accept unsolicited loan solicitations. Thank you.", "02:10 PM")
                ),
                isAlertSent = false,
                createdAtEpoch = now - 1000 * 60 * 60 * 72
            )
        )
        _calls.value = demoCalls

        // 2. Seed Contacts
        val demoContacts = listOf(
            VipContact("c1", "Rahul Verma", "+91 98765 43210", ContactCategory.CLIENT, "Lead Enterprise Client (Acme)", alwaysAlert = true),
            VipContact("c2", "Vikram Sethi", "+91 98445 56677", ContactCategory.BUSINESS, "Operations Director", alwaysAlert = true),
            VipContact("c3", "Ananya Kumar", "+91 98776 65544", ContactCategory.FAMILY, "Sister / Immediate Family", alwaysAlert = true, alwaysTransfer = true),
            VipContact("c4", "Dr. Mehta", "+91 98110 02233", ContactCategory.OTHER, "Family Physician", alwaysAlert = true),
            VipContact("c5", "Priya Sharma", "+91 98112 23344", ContactCategory.FRIEND, "Tech Consultant & Friend", alwaysAlert = false),
            VipContact("c6", "Spam Telemarketer", "+91 98000 00001", ContactCategory.OTHER, "Unsolicited loan telemarketing", isBlocked = true)
        )
        _contacts.value = demoContacts

        // 3. Seed Urgency Rules
        val demoRules = listOf(
            UrgencyRule("r1", "High Urgency Outage Escalation", "URGENCY_LEVEL", "HIGH", "SMS", true),
            UrgencyRule("r2", "Critical Life/Safety Emergency Forwarding", "URGENCY_LEVEL", "CRITICAL", "CALL_TRANSFER", true),
            UrgencyRule("r3", "Always Alert on VIP Contacts", "VIP_CALLER", "ALL_VIP", "SMS", true),
            UrgencyRule("r4", "Project Deadline Keyword Trigger", "KEYWORD", "deadline today", "SMS", true),
            UrgencyRule("r5", "Ignore Unsolicited Marketing Offers", "MARKETING_SPAM", "loan,credit card,promotional", "NO_ALERT", true)
        )
        _rules.value = demoRules

        // 4. Seed Knowledge Base
        val demoKb = listOf(
            KnowledgeItem("kb1", "General Business Hours", "Working Hours", "Monday through Friday from 9:00 AM to 6:00 PM IST. Closed on Sunday."),
            KnowledgeItem("kb2", "Core Engineering Services", "Services", "Specializes in high-scale Android development, AI agents, cloud architectures, and FastAPI backends."),
            KnowledgeItem("kb3", "Consultation Rates", "Pricing", "Standard architectural advisory starts at $150/hour. Fixed-bid project quotes available on request."),
            KnowledgeItem("kb4", "Appointment Booking Policy", "Appointments", "Appointments require 24 hours prior notice. Schedule via Google Calendar invite or email."),
            KnowledgeItem("kb5", "Emergency Protocol", "FAQ", "For life-safety, medical, or security crises, callers must dial 112/911. AI assistant does not replace emergency dispatch.")
        )
        _knowledgeBase.value = demoKb

        // 5. Seed Initial SMS Alert
        val initialAlert = SmsAlertLog(
            id = "sms_01",
            callerName = "Rahul Verma",
            callerNumber = "+91 98765 43210",
            urgency = UrgencyLevel.HIGH,
            formattedMessage = "URGENT CALL ALERT\n\nCaller: Rahul Verma\nNumber: +91 98765 43210\nUrgency: HIGH\n\nReason:\nWebsite outage - Checkout failure\n\nSummary:\nCustomer reports that users cannot place orders.\n\nTime:\n10:42 AM\n\nPlease review in AI Call Agent app.",
            timestamp = "10:42 AM",
            status = "DELIVERED",
            provider = "Twilio"
        )
        _smsLogs.value = listOf(initialAlert)
        _latestAlert.value = initialAlert
    }

    // Toggle Agent ON/OFF
    fun toggleAgentStatus() {
        val current = _settings.value
        _settings.value = current.copy(isAgentEnabled = !current.isAgentEnabled)
    }

    fun updateSettings(newSettings: AgentSettings) {
        _settings.value = newSettings
    }

    fun addContact(contact: VipContact) {
        _contacts.value = _contacts.value + contact
    }

    fun updateContact(contact: VipContact) {
        _contacts.value = _contacts.value.map { if (it.id == contact.id) contact else it }
    }

    fun deleteContact(contactId: String) {
        _contacts.value = _contacts.value.filterNot { it.id == contactId }
    }

    fun addRule(rule: UrgencyRule) {
        _rules.value = _rules.value + rule
    }

    fun toggleRule(ruleId: String) {
        _rules.value = _rules.value.map {
            if (it.id == ruleId) it.copy(isEnabled = !it.isEnabled) else it
        }
    }

    fun deleteRule(ruleId: String) {
        _rules.value = _rules.value.filterNot { it.id == ruleId }
    }

    fun addKnowledgeItem(item: KnowledgeItem) {
        _knowledgeBase.value = _knowledgeBase.value + item
    }

    fun deleteKnowledgeItem(itemId: String) {
        _knowledgeBase.value = _knowledgeBase.value.filterNot { it.id == itemId }
    }

    fun markCallUrgent(callId: String) {
        _calls.value = _calls.value.map {
            if (it.id == callId) it.copy(urgency = UrgencyLevel.HIGH, status = CallStatus.ESCALATED) else it
        }
    }

    fun transferCall(callId: String) {
        _calls.value = _calls.value.map {
            if (it.id == callId) it.copy(status = CallStatus.TRANSFERRED) else it
        }
    }

    fun deleteCall(callId: String) {
        _calls.value = _calls.value.filterNot { it.id == callId }
    }

    fun clearAllCalls() {
        _calls.value = emptyList()
    }

    fun dismissLatestAlert() {
        _latestAlert.value = null
    }

    private data class SimScenario(
        val name: String,
        val number: String,
        val urgency: UrgencyLevel,
        val reason: String,
        val summary: String,
        val action: String,
        val messages: List<TranscriptMessage>,
        val status: CallStatus
    )

    // Interactive Demo Simulation Engine
    fun simulateCallScenario(scenarioKey: String): CallRecord {
        val currentTime = timeFormat.format(Date())
        val newId = "call_${System.currentTimeMillis() % 10000}"

        val scenario = when (scenarioKey) {
            "outage" -> {
                val msgs = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant. Manish isn't available right now. How can I help you?", currentTime),
                    TranscriptMessage("Caller", "Hello, this is Rahul. The website is down and customers can't place orders! We need this fixed immediately.", currentTime),
                    TranscriptMessage("AI", "I understand the urgency regarding the website outage and checkout stoppage. I am marking this as HIGH urgency and sending an immediate SMS alert to Manish.", currentTime),
                    TranscriptMessage("Caller", "Thank you, please make sure he inspects the server now.", currentTime),
                    TranscriptMessage("AI", "Alert has been dispatched. Manish will review shortly.", currentTime)
                )
                SimScenario(
                    name = "Rahul Verma",
                    number = "+91 98765 43210",
                    urgency = UrgencyLevel.HIGH,
                    reason = "Website outage - Customers cannot place orders",
                    summary = "Rahul reported that the production website is down and customer transactions are failing.",
                    action = "Owner should investigate the website and server logs immediately.",
                    messages = msgs,
                    status = CallStatus.ESCALATED
                )
            }
            "enquiry" -> {
                val msgs = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant. How can I help you?", currentTime),
                    TranscriptMessage("Caller", "Hi, I wanted to inquire if Manish is available for a freelance mobile app consultation this Friday?", currentTime),
                    TranscriptMessage("AI", "Manish's consultation hours are Monday to Friday 9 AM to 6 PM. I've noted your request and will forward your message to him.", currentTime),
                    TranscriptMessage("Caller", "Great, my name is Priya Sharma. Have a nice day!", currentTime)
                )
                SimScenario(
                    name = "Priya Sharma",
                    number = "+91 98112 23344",
                    urgency = UrgencyLevel.LOW,
                    reason = "Consulting slot enquiry for Friday",
                    summary = "Priya asked about advisory availability for mobile application development.",
                    action = "Send booking link when convenient.",
                    messages = msgs,
                    status = CallStatus.COMPLETED
                )
            }
            "contract" -> {
                val msgs = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant. How may I help?", currentTime),
                    TranscriptMessage("Caller", "Vikram here from Acme Corp. We have a hard contract deadline today at 5 PM. We need Manish's signature immediately.", currentTime),
                    TranscriptMessage("AI", "I understand Vikram. Since the deadline is today, I am flagging this as HIGH priority and notifying Manish right away.", currentTime)
                )
                SimScenario(
                    name = "Vikram Sethi",
                    number = "+91 98445 56677",
                    urgency = UrgencyLevel.HIGH,
                    reason = "Contract deadline today before 5:00 PM",
                    summary = "Acme Corp requires countersignature on enterprise agreement before close of business.",
                    action = "Sign agreement document in email.",
                    messages = msgs,
                    status = CallStatus.ESCALATED
                )
            }
            "family" -> {
                val msgs = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant.", currentTime),
                    TranscriptMessage("Caller", "Hey Manish, pick up the phone! It's Ananya, need to talk about mom's flight details.", currentTime),
                    TranscriptMessage("AI", "Hello Ananya. I recognize you from Manish's VIP Family list. I am alerting him right now on his priority phone.", currentTime)
                )
                SimScenario(
                    name = "Ananya Kumar (Family)",
                    number = "+91 98776 65544",
                    urgency = UrgencyLevel.HIGH,
                    reason = "VIP Family Call - Urgent flight coordination",
                    summary = "Ananya called regarding travel coordination.",
                    action = "Call back immediately.",
                    messages = msgs,
                    status = CallStatus.ESCALATED
                )
            }
            "spam" -> {
                val msgs = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant.", currentTime),
                    TranscriptMessage("Caller", "Hello Sir! Special pre-approved credit card offer with zero annual fee and free lounge access...", currentTime),
                    TranscriptMessage("AI", "Manish does not accept promotional marketing calls. Ending call.", currentTime)
                )
                SimScenario(
                    name = "Credit Card Telemarketer",
                    number = "+91 98000 00001",
                    urgency = UrgencyLevel.LOW,
                    reason = "Unsolicited credit card promotion",
                    summary = "Automated marketing telemarketer attempting cold sales pitch.",
                    action = "No action required. Call blocked.",
                    messages = msgs,
                    status = CallStatus.SPAM
                )
            }
            else -> { // emergency
                val msgs = listOf(
                    TranscriptMessage("AI", "Hello, you've reached Manish's AI assistant.", currentTime),
                    TranscriptMessage("Caller", "There's smoke coming from the electrical box in the hallway, need immediate assistance!", currentTime),
                    TranscriptMessage("AI", "If there is fire, smoke, or immediate safety danger, please call 112 or 911 immediately! As an AI I cannot dispatch emergency responders.", currentTime)
                )
                SimScenario(
                    name = "Hallway Safety Alert",
                    number = "+91 98998 87766",
                    urgency = UrgencyLevel.CRITICAL,
                    reason = "Immediate safety hazard - Electrical smoke",
                    summary = "Caller reported smoke hazard in hallway. AI provided emergency service redirection advice.",
                    action = "Verify building safety status.",
                    messages = msgs,
                    status = CallStatus.ESCALATED
                )
            }
        }

        val record = CallRecord(
            id = newId,
            callerName = scenario.name,
            callerNumber = scenario.number,
            timestampFormatted = "Today, $currentTime",
            durationSeconds = 48,
            reason = scenario.reason,
            urgency = scenario.urgency,
            summary = scenario.summary,
            importantDetails = "Simulated call scenario ($scenarioKey) processed successfully.",
            actionRequired = scenario.action,
            callbackRequired = scenario.urgency == UrgencyLevel.HIGH || scenario.urgency == UrgencyLevel.CRITICAL,
            status = scenario.status,
            messages = scenario.messages,
            isAlertSent = scenario.urgency == UrgencyLevel.HIGH || scenario.urgency == UrgencyLevel.CRITICAL,
            createdAtEpoch = System.currentTimeMillis()
        )

        _calls.value = listOf(record) + _calls.value

        // Dispatch simulated SMS alert if High or Critical
        if (record.urgency == UrgencyLevel.HIGH || record.urgency == UrgencyLevel.CRITICAL) {
            val alertMsg = _settings.value.alertTemplate
                .replace("{caller}", record.callerName)
                .replace("{number}", record.callerNumber)
                .replace("{urgency}", record.urgency.name)
                .replace("{reason}", record.reason)
                .replace("{summary}", record.summary)
                .replace("{time}", currentTime)

            val alertLog = SmsAlertLog(
                id = "sms_${System.currentTimeMillis() % 10000}",
                callerName = record.callerName,
                callerNumber = record.callerNumber,
                urgency = record.urgency,
                formattedMessage = alertMsg,
                timestamp = currentTime,
                status = "DELIVERED",
                provider = _settings.value.smsProvider
            )
            _smsLogs.value = listOf(alertLog) + _smsLogs.value
            _latestAlert.value = alertLog
        }

        return record
    }
}
