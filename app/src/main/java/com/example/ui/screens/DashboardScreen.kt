package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.AppConfigState
import com.example.model.CallRecord
import com.example.model.ExotelStatus

@Composable
fun DashboardScreen(
    config: AppConfigState,
    exotel: ExotelStatus,
    calls: List<CallRecord>,
    onToggleOnline: (Boolean) -> Unit,
    onNavigateToCalls: () -> Unit,
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Warning banner if backend unavailable
        if (!config.backendConnected) {
            Card(
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                ),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("backend_warning_card")
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = "Warning",
                        tint = MaterialTheme.colorScheme.error
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Backend unavailable - Displaying safe offline defaults",
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }

        // Online / Offline Status Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("agent_status_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                val isOnline = config.agentEnabled
                Box(
                    modifier = Modifier
                        .size(14.dp)
                        .clip(CircleShape)
                        .background(if (isOnline) Color(0xFF10B981) else Color(0xFFEF4444))
                )
                Spacer(modifier = Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = if (isOnline) "AI RECEPTIONIST ONLINE" else "AI RECEPTIONIST OFFLINE",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = if (isOnline) "Answering incoming calls via Exotel" else "Calls will ring directly to owner",
                        fontSize = 13.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = isOnline,
                    onCheckedChange = onToggleOnline,
                    modifier = Modifier.testTag("agent_online_switch")
                )
            }
        }

        // Metrics Section (2 rows of cards)
        Text(
            text = "Call Metrics & Telephony",
            fontWeight = FontWeight.SemiBold,
            fontSize = 16.sp,
            color = MaterialTheme.colorScheme.primary
        )

        // Row 1: Calls Today & Total Calls
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            MetricCard(
                title = "Calls Today",
                value = config.callsToday.toString(),
                icon = Icons.Default.PhoneCallback,
                color = Color(0xFF00E5FF),
                modifier = Modifier.weight(1f)
            )
            MetricCard(
                title = "Total Calls",
                value = config.totalCalls.toString(),
                icon = Icons.Default.Call,
                color = Color(0xFF38BDF8),
                modifier = Modifier.weight(1f)
            )
        }

        // Row 2: Urgent Escalations & SMS Alerts
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            MetricCard(
                title = "Urgent Escalations",
                value = config.urgentEscalations.toString(),
                icon = Icons.Default.NotificationImportant,
                color = Color(0xFFF97316),
                modifier = Modifier.weight(1f)
            )
            MetricCard(
                title = "SMS Alerts",
                value = config.smsAlertsSent.toString(),
                icon = Icons.Default.Message,
                color = Color(0xFF10B981),
                modifier = Modifier.weight(1f)
            )
        }

        // Row 3: Average Call Duration
        MetricCard(
            title = "Average Call Duration",
            value = "${config.avgCallDurationSeconds}s",
            icon = Icons.Default.Timer,
            color = Color(0xFFA855F7),
            modifier = Modifier.fillMaxWidth()
        )

        // Subsystem Connection Health
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("subsystems_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Text(
                    text = "Subsystem Integrations",
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    SubsystemBadge(
                        name = "Telephony",
                        provider = config.telephonyProvider,
                        status = config.telephonyStatus
                    )
                    SubsystemBadge(
                        name = "Voicebot",
                        provider = "WebSocket",
                        status = config.websocketStatus
                    )
                    SubsystemBadge(
                        name = "OpenAI",
                        provider = "GPT & TTS",
                        status = if (config.openaiConfigured) "READY" else "CONNECTED"
                    )
                    SubsystemBadge(
                        name = "SMS",
                        provider = config.smsProvider,
                        status = config.smsStatus
                    )
                }
            }
        }

        // Latest Call Section
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("latest_call_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Latest Call",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    if (calls.isNotEmpty()) {
                        TextButton(
                            onClick = onNavigateToCalls,
                            modifier = Modifier.testTag("view_all_calls_btn")
                        ) {
                            Text("View All Calls")
                        }
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                if (calls.isEmpty()) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Icon(
                            imageVector = Icons.Default.PhoneCallback,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.size(36.dp)
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "No calls yet",
                            fontWeight = FontWeight.SemiBold,
                            fontSize = 15.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "Incoming calls from Exotel will be recorded and summarized here automatically.",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(horizontal = 16.dp),
                            lineHeight = 16.sp
                        )
                    }
                } else {
                    val latest = calls.first()
                    Column {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = latest.callerName,
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                            Surface(
                                color = if (latest.urgency == "HIGH" || latest.urgency == "CRITICAL")
                                    Color(0xFFF97316).copy(alpha = 0.2f)
                                else
                                    MaterialTheme.colorScheme.primaryContainer,
                                shape = RoundedCornerShape(8.dp)
                            ) {
                                Text(
                                    text = latest.urgency,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (latest.urgency == "HIGH" || latest.urgency == "CRITICAL")
                                        Color(0xFFF97316)
                                    else
                                        MaterialTheme.colorScheme.onPrimaryContainer
                                )
                            }
                        }
                        Text(
                            text = latest.callerNumber,
                            fontSize = 13.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        if (latest.summary.isNotEmpty()) {
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                text = latest.summary,
                                fontSize = 13.sp,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun MetricCard(
    title: String,
    value: String,
    icon: ImageVector,
    color: Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.testTag("metric_card_${title.lowercase().replace(" ", "_")}"),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = color,
                modifier = Modifier.size(26.dp)
            )
            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = value,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = title,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
fun SubsystemBadge(
    name: String,
    provider: String,
    status: String
) {
    val isReady = status == "READY" || status == "CONNECTED" || status == "ACTIVE"
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Icon(
            imageVector = if (isReady) Icons.Default.CheckCircle else Icons.Default.Sensors,
            contentDescription = null,
            tint = if (isReady) Color(0xFF10B981) else Color(0xFF00E5FF),
            modifier = Modifier.size(20.dp)
        )
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = name,
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.onSurface
        )
        Text(
            text = status,
            fontSize = 10.sp,
            color = if (isReady) Color(0xFF10B981) else MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
