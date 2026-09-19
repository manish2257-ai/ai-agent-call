package com.example.network

import com.example.model.AppConfigState
import com.example.model.CallRecord
import com.example.model.ExotelStatus
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL

class BackendRepository {

    // Candidate base URLs: emulator loopback, localhost, and cloud backend
    private val candidateHosts = listOf(
        "http://10.0.2.2:8080",
        "http://127.0.0.1:8080",
        "https://ais-dev-drq6zz2gzpkest44ecny22-192566711824.asia-east1.run.app"
    )

    @Volatile
    private var resolvedBaseUrl: String? = null

    private suspend fun makeGetRequest(endpoint: String): String? = withContext(Dispatchers.IO) {
        val hostsToTry = if (resolvedBaseUrl != null) {
            listOf(resolvedBaseUrl!!) + candidateHosts.filter { it != resolvedBaseUrl }
        } else {
            candidateHosts
        }

        for (host in hostsToTry) {
            var connection: HttpURLConnection? = null
            try {
                val fullUrl = "$host$endpoint"
                val url = URL(fullUrl)
                connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "GET"
                connection.connectTimeout = 3000
                connection.readTimeout = 4000
                connection.setRequestProperty("Accept", "application/json")

                val responseCode = connection.responseCode
                if (responseCode in 200..299) {
                    val reader = BufferedReader(InputStreamReader(connection.inputStream))
                    val response = reader.readText()
                    reader.close()
                    resolvedBaseUrl = host
                    return@withContext response
                }
            } catch (_: Exception) {
                // Try next host candidate
            } finally {
                connection?.disconnect()
            }
        }
        null
    }

    suspend fun fetchAppConfig(): AppConfigState = withContext(Dispatchers.IO) {
        val jsonStr = makeGetRequest("/api/app/config")
        if (jsonStr != null) {
            try {
                val obj = JSONObject(jsonStr)
                val metricsObj = obj.optJSONObject("metrics")

                return@withContext AppConfigState(
                    telephonyProvider = obj.optString("telephony_provider", "Exotel"),
                    telephonyStatus = obj.optString("telephony_status", "READY"),
                    virtualNumberConfigured = obj.optBoolean("virtual_number_configured", false),
                    virtualNumber = obj.optString("virtual_number", "Not configured").ifEmpty { "Not configured" },
                    smsProvider = obj.optString("sms_provider", "Exotel"),
                    smsStatus = obj.optString("sms_status", "READY"),
                    openaiConfigured = obj.optBoolean("openai_configured", false),
                    voicebotStatus = obj.optString("voicebot_status", "READY"),
                    websocketStatus = obj.optString("websocket_status", "READY"),
                    voicebotWssUrl = obj.optString("voicebot_wss_url", "Not configured").ifEmpty { "Not configured" },
                    incomingWebhookUrl = obj.optString("incoming_webhook_url", "Not configured").ifEmpty { "Not configured" },
                    statusCallbackUrl = obj.optString("status_callback_url", "Not configured").ifEmpty { "Not configured" },
                    agentEnabled = obj.optBoolean("agent_enabled", true),
                    active = obj.optBoolean("active", true),
                    ownerPhoneNumber = obj.optString("owner_phone_number", "Not configured").ifEmpty { "Not configured" },
                    aiPhoneNumber = obj.optString("ai_phone_number", "Not configured").ifEmpty { "Not configured" },
                    greeting = obj.optString("greeting", "Not configured").ifEmpty { "Not configured" },
                    urgencyThreshold = obj.optString("urgency_threshold", "HIGH"),
                    callsToday = metricsObj?.optInt("calls_today", 0) ?: 0,
                    totalCalls = metricsObj?.optInt("total_calls", 0) ?: 0,
                    urgentEscalations = metricsObj?.optInt("urgent_escalations", 0) ?: 0,
                    smsAlertsSent = metricsObj?.optInt("sms_alerts_sent", 0) ?: 0,
                    avgCallDurationSeconds = metricsObj?.optInt("avg_call_duration_seconds", 0) ?: 0,
                    isLoading = false,
                    backendConnected = true,
                    errorMessage = null
                )
            } catch (e: Exception) {
                // Parse error fallback
            }
        }

        // If backend temporarily unreachable, return safe un-invented state
        AppConfigState(
            telephonyProvider = "Exotel",
            telephonyStatus = "READY",
            virtualNumberConfigured = false,
            virtualNumber = "Not configured",
            smsProvider = "Exotel",
            smsStatus = "READY",
            openaiConfigured = false,
            voicebotStatus = "READY",
            websocketStatus = "READY",
            voicebotWssUrl = "Not configured",
            incomingWebhookUrl = "Not configured",
            statusCallbackUrl = "Not configured",
            agentEnabled = true,
            active = true,
            ownerPhoneNumber = "Not configured",
            aiPhoneNumber = "Not configured",
            greeting = "Not configured",
            urgencyThreshold = "HIGH",
            callsToday = 0,
            totalCalls = 0,
            urgentEscalations = 0,
            smsAlertsSent = 0,
            avgCallDurationSeconds = 0,
            isLoading = false,
            backendConnected = false,
            errorMessage = "Backend unavailable"
        )
    }

    suspend fun fetchExotelStatus(): ExotelStatus = withContext(Dispatchers.IO) {
        val jsonStr = makeGetRequest("/api/voice/exotel/status")
        if (jsonStr != null) {
            try {
                val obj = JSONObject(jsonStr)
                val missingArray = obj.optJSONArray("missing_variables")
                val missingList = mutableListOf<String>()
                if (missingArray != null) {
                    for (i in 0 until missingArray.length()) {
                        missingList.add(missingArray.getString(i))
                    }
                }
                return@withContext ExotelStatus(
                    provider = obj.optString("provider", "Exotel"),
                    status = obj.optString("status", "READY"),
                    mode = obj.optString("mode", "PRODUCTION"),
                    virtualNumber = obj.optString("virtual_number", "Not configured").ifEmpty { "Not configured" },
                    missingVariables = missingList
                )
            } catch (_: Exception) {}
        }
        ExotelStatus()
    }

    suspend fun fetchCalls(): List<CallRecord> = withContext(Dispatchers.IO) {
        val jsonStr = makeGetRequest("/calls")
        if (jsonStr != null) {
            try {
                val array = JSONArray(jsonStr)
                val calls = mutableListOf<CallRecord>()
                for (i in 0 until array.length()) {
                    val item = array.getJSONObject(i)
                    calls.add(
                        CallRecord(
                            id = item.optString("id", item.optString("call_id", "")),
                            callerName = item.optString("caller_name", "Unknown Caller"),
                            callerNumber = item.optString("caller_number", "Unknown Number"),
                            urgency = item.optString("urgency", "LOW"),
                            reason = item.optString("reason", ""),
                            summary = item.optString("summary", ""),
                            durationSeconds = item.optInt("duration_seconds", 0),
                            createdAt = item.optString("created_at", "")
                        )
                    )
                }
                return@withContext calls
            } catch (_: Exception) {}
        }
        emptyList()
    }

    suspend fun toggleAgentEnabled(enabled: Boolean): Boolean = withContext(Dispatchers.IO) {
        val host = resolvedBaseUrl ?: candidateHosts.first()
        var connection: HttpURLConnection? = null
        try {
            val url = URL("$host/settings")
            connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "PUT"
            connection.connectTimeout = 3000
            connection.readTimeout = 4000
            connection.setRequestProperty("Content-Type", "application/json")
            connection.doOutput = true

            val body = JSONObject().apply {
                put("is_agent_enabled", enabled)
            }.toString()

            connection.outputStream.use { os ->
                os.write(body.toByteArray())
            }

            return@withContext connection.responseCode in 200..299
        } catch (_: Exception) {
            return@withContext false
        } finally {
            connection?.disconnect()
        }
    }
}
