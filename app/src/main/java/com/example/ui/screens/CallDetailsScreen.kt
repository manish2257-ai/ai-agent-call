package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.CallRecord
import com.example.data.model.CallStatus
import com.example.data.model.TranscriptMessage
import com.example.data.model.UrgencyLevel
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.StatusPill
import com.example.ui.components.UrgencyBadge
import com.example.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CallDetailsScreen(
    call: CallRecord,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    var currentCall by remember { mutableStateOf(call) }
    var snackbarMessage by remember { mutableStateOf<String?>(null) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Call Details", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    IconButton(
                        onClick = {
                            CallAgentRepository.deleteCall(currentCall.id)
                            onBack()
                        }
                    ) {
                        Icon(Icons.Default.Delete, contentDescription = "Delete call", tint = MaterialTheme.colorScheme.error)
                    }
                }
            )
        },
        snackbarHost = {
            if (snackbarMessage != null) {
                Snackbar(
                    action = {
                        TextButton(onClick = { snackbarMessage = null }) {
                            Text("Dismiss", color = PrimaryCyan)
                        }
                    },
                    modifier = Modifier.padding(16.dp)
                ) {
                    Text(snackbarMessage!!)
                }
            }
        }
    ) { innerPadding ->
        LazyColumn(
            modifier = modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            contentPadding = PaddingValues(bottom = 32.dp)
        ) {
            // 1. Caller Hero Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .size(46.dp)
                                        .clip(CircleShape)
                                        .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)),
                                    contentAlignment = Alignment.Center
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Person,
                                        contentDescription = null,
                                        tint = MaterialTheme.colorScheme.primary,
                                        modifier = Modifier.size(26.dp)
                                    )
                                }
                                Column {
                                    Text(
                                        text = currentCall.callerName,
                                        fontSize = 18.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = MaterialTheme.colorScheme.onSurface
                                    )
                                    Text(
                                        text = currentCall.callerNumber,
                                        fontSize = 13.sp,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }

                            UrgencyBadge(urgency = currentCall.urgency)
                        }

                        Spacer(modifier = Modifier.height(14.dp))
                        HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.2f))
                        Spacer(modifier = Modifier.height(12.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text("Time", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                Text(currentCall.timestampFormatted, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                            }
                            Column {
                                Text("Duration", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                Text("${currentCall.durationSeconds} seconds", fontSize = 13.sp, fontWeight = FontWeight.Medium)
                            }
                            Column(horizontalAlignment = Alignment.End) {
                                Text("Outcome", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                StatusPill(status = currentCall.status)
                            }
                        }
                    }
                }
            }

            // 2. Urgency Reason Card
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = when (currentCall.urgency) {
                            UrgencyLevel.HIGH -> UrgencyHighBg
                            UrgencyLevel.CRITICAL -> UrgencyCriticalBg
                            UrgencyLevel.MEDIUM -> UrgencyMediumBg
                            UrgencyLevel.LOW -> UrgencyLowBg
                        }
                    )
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = when (currentCall.urgency) {
                                    UrgencyLevel.HIGH, UrgencyLevel.CRITICAL -> Icons.Default.Warning
                                    else -> Icons.Default.Info
                                },
                                contentDescription = null,
                                tint = when (currentCall.urgency) {
                                    UrgencyLevel.HIGH -> UrgencyHigh
                                    UrgencyLevel.CRITICAL -> UrgencyCritical
                                    UrgencyLevel.MEDIUM -> UrgencyMedium
                                    UrgencyLevel.LOW -> UrgencyLow
                                },
                                modifier = Modifier.size(18.dp)
                            )
                            Text(
                                text = "Urgency Assessment: ${currentCall.urgency.name}",
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = currentCall.reason,
                            fontSize = 13.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                    }
                }
            }

            // 3. AI Summary & Action Items
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    border = CardDefaults.outlinedCardBorder()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(Icons.Default.Summarize, contentDescription = null, tint = PrimaryCyan, modifier = Modifier.size(18.dp))
                            Text("Call Summary", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = currentCall.summary,
                            fontSize = 13.sp,
                            lineHeight = 18.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )

                        Spacer(modifier = Modifier.height(14.dp))
                        HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.2f))
                        Spacer(modifier = Modifier.height(12.dp))

                        Text("Recommended Action", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = MaterialTheme.colorScheme.onSurface)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = currentCall.actionRequired,
                            fontSize = 13.sp,
                            color = PrimaryIndigo,
                            fontWeight = FontWeight.Medium
                        )

                        if (currentCall.callbackRequired) {
                            Spacer(modifier = Modifier.height(10.dp))
                            AssistChip(
                                onClick = {},
                                label = { Text("Callback Requested by Caller", fontSize = 11.sp, fontWeight = FontWeight.SemiBold) },
                                leadingIcon = {
                                    Icon(Icons.Default.PhoneCallback, contentDescription = null, modifier = Modifier.size(14.dp), tint = UrgencyHigh)
                                }
                            )
                        }
                    }
                }
            }

            // 4. Quick Action Buttons
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    OutlinedButton(
                        onClick = {
                            CallAgentRepository.transferCall(currentCall.id)
                            currentCall = currentCall.copy(status = CallStatus.TRANSFERRED)
                            snackbarMessage = "Call transferred to owner phone."
                        },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Icon(Icons.Default.PhoneForwarded, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Transfer", fontSize = 12.sp)
                    }

                    if (currentCall.urgency != UrgencyLevel.HIGH && currentCall.urgency != UrgencyLevel.CRITICAL) {
                        Button(
                            onClick = {
                                CallAgentRepository.markCallUrgent(currentCall.id)
                                currentCall = currentCall.copy(urgency = UrgencyLevel.HIGH, status = CallStatus.ESCALATED)
                                snackbarMessage = "Call marked as HIGH urgency and alert recorded."
                            },
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(10.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = UrgencyHigh)
                        ) {
                            Icon(Icons.Default.PriorityHigh, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Mark Urgent", fontSize = 12.sp)
                        }
                    }
                }
            }

            // 5. Full Transcript Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Full Audio Transcript",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = "${currentCall.messages.size} Turns",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // 6. Chat Bubbles
            items(currentCall.messages) { msg ->
                TranscriptBubble(msg = msg)
            }
        }
    }
}

@Composable
fun TranscriptBubble(msg: TranscriptMessage) {
    val isAI = msg.speaker == "AI"

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalAlignment = if (isAI) Alignment.Start else Alignment.End
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            if (isAI) {
                Box(
                    modifier = Modifier
                        .size(18.dp)
                        .clip(CircleShape)
                        .background(PrimaryCyan.copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(Icons.Default.SmartToy, contentDescription = null, tint = PrimaryCyan, modifier = Modifier.size(12.dp))
                }
                Text("AI Assistant", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = PrimaryCyan)
                Text("• ${msg.timestamp}", fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            } else {
                Text(msg.timestamp, fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text("Caller", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface)
                Box(
                    modifier = Modifier
                        .size(18.dp)
                        .clip(CircleShape)
                        .background(Color(0xFF3B82F6).copy(alpha = 0.2f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(Icons.Default.Person, contentDescription = null, tint = Color(0xFF3B82F6), modifier = Modifier.size(12.dp))
                }
            }
        }

        Spacer(modifier = Modifier.height(4.dp))

        Surface(
            shape = RoundedCornerShape(
                topStart = if (isAI) 4.dp else 16.dp,
                topEnd = if (isAI) 16.dp else 4.dp,
                bottomStart = 16.dp,
                bottomEnd = 16.dp
            ),
            color = if (isAI) MaterialTheme.colorScheme.surfaceVariant else Color(0xFF1E293B),
            modifier = Modifier.widthIn(max = 300.dp)
        ) {
            Text(
                text = msg.content,
                fontSize = 13.sp,
                lineHeight = 18.sp,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
                color = if (isAI) MaterialTheme.colorScheme.onSurface else Color(0xFFF1F5F9)
            )
        }
    }
}
