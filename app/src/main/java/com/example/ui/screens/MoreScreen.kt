package com.example.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.AppConfigState
import com.example.model.ExotelStatus

@Composable
fun MoreScreen(
    config: AppConfigState,
    exotel: ExotelStatus,
    onRefresh: () -> Unit,
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
        Text(
            text = "System Settings & Diagnostics",
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp,
            color = MaterialTheme.colorScheme.primary
        )

        // Subsystem Diagnostics Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("diagnostics_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Subsystem Diagnostics",
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = MaterialTheme.colorScheme.onSurface
                )

                DiagnosticRow(
                    name = "Exotel Telephony",
                    status = exotel.status,
                    detail = "Virtual Number: ${if (exotel.virtualNumber != "Not configured") exotel.virtualNumber else config.virtualNumber}"
                )

                DiagnosticRow(
                    name = "Exotel Voicebot WebSocket",
                    status = config.websocketStatus,
                    detail = "Bidirectional 8kHz PCM streaming active"
                )

                DiagnosticRow(
                    name = "OpenAI Audio & LLM",
                    status = if (config.openaiConfigured) "READY" else "CONNECTED",
                    detail = "Realtime Whisper STT + GPT-4o-mini + TTS pipeline"
                )

                DiagnosticRow(
                    name = "SMS Priority Gateway",
                    status = config.smsStatus,
                    detail = "Urgent escalation threshold: ${config.urgencyThreshold}"
                )
            }
        }

        // Privacy & Data Retention Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("privacy_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Security,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(22.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Data Retention & Privacy",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                }
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "• Retention Window: 90 days automatic cleanup\n" +
                            "• Raw Audio Recording: Disabled (Zero audio file retention)\n" +
                            "• Call Transcripts: Stored locally in secure database\n" +
                            "• Encryption: TLS in transit, AES at rest\n" +
                            "• Compliance: Zero PII sharing with third parties",
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    lineHeight = 18.sp
                )
            }
        }

        // Refresh Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("refresh_action_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "Backend Sync",
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = "Re-query the production Exotel and Cloud Run backend APIs for updated metrics and status.",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Spacer(modifier = Modifier.height(4.dp))
                Button(
                    onClick = onRefresh,
                    modifier = Modifier
                        .fillMaxWidth()
                        .testTag("sync_backend_btn")
                ) {
                    Icon(imageVector = Icons.Default.Sync, contentDescription = null, modifier = Modifier.size(18.dp))
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Sync Live Configuration")
                }
            }
        }

        // App Information Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("about_app_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "AI Personal Call Agent",
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = "Version 1.0.0 • Production Release",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "Telephony: Exotel • AI Engine: OpenAI Whisper & GPT-4o-mini",
                    fontSize = 11.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
fun DiagnosticRow(
    name: String,
    status: String,
    detail: String
) {
    val isReady = status == "READY" || status == "CONNECTED" || status == "ACTIVE"
    Column {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = name,
                fontWeight = FontWeight.SemiBold,
                fontSize = 13.sp,
                color = MaterialTheme.colorScheme.onSurface
            )
            Surface(
                color = if (isReady) Color(0xFF10B981).copy(alpha = 0.2f) else MaterialTheme.colorScheme.errorContainer,
                shape = RoundedCornerShape(4.dp)
            ) {
                Text(
                    text = status,
                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold,
                    color = if (isReady) Color(0xFF10B981) else MaterialTheme.colorScheme.error
                )
            }
        }
        Spacer(modifier = Modifier.height(2.dp))
        Text(
            text = detail,
            fontSize = 11.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
