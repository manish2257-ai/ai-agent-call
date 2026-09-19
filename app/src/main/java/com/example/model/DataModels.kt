package com.example.model

data class AppConfigState(
    val telephonyProvider: String = "Exotel",
    val telephonyStatus: String = "READY",
    val virtualNumberConfigured: Boolean = false,
    val virtualNumber: String = "Not configured",
    val smsProvider: String = "Exotel",
    val smsStatus: String = "READY",
    val openaiConfigured: Boolean = false,
    val voicebotStatus: String = "READY",
    val websocketStatus: String = "READY",
    val voicebotWssUrl: String = "Not configured",
    val incomingWebhookUrl: String = "Not configured",
    val statusCallbackUrl: String = "Not configured",
    val agentEnabled: Boolean = true,
    val active: Boolean = true,
    val ownerPhoneNumber: String = "Not configured",
    val aiPhoneNumber: String = "Not configured",
    val greeting: String = "Not configured",
    val urgencyThreshold: String = "HIGH",
    val callsToday: Int = 0,
    val totalCalls: Int = 0,
    val urgentEscalations: Int = 0,
    val smsAlertsSent: Int = 0,
    val avgCallDurationSeconds: Int = 0,
    val isLoading: Boolean = false,
    val backendConnected: Boolean = true,
    val errorMessage: String? = null
)

data class CallRecord(
    val id: String,
    val callerName: String,
    val callerNumber: String,
    val urgency: String,
    val reason: String,
    val summary: String,
    val durationSeconds: Int,
    val createdAt: String
)

data class ExotelStatus(
    val provider: String = "Exotel",
    val status: String = "READY",
    val mode: String = "PRODUCTION",
    val virtualNumber: String = "Not configured",
    val missingVariables: List<String> = emptyList()
)
