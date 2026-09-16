package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.CallRecord
import com.example.data.model.UrgencyLevel
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.*
import com.example.ui.theme.*

@Composable
fun DashboardScreen(
    onNavigateToCalls: () -> Unit,
    onSelectCall: (CallRecord) -> Unit,
    onNavigateToSetup: () -> Unit,
    modifier: Modifier = Modifier
) {
    val settings by CallAgentRepository.settings.collectAsState()
    val calls by CallAgentRepository.calls.collectAsState()
    val latestAlert by CallAgentRepository.latestAlert.collectAsState()

    var showSimulateModal by remember { mutableStateOf(false) }

    val callsToday = remember(calls) {
        calls.count { it.timestampFormatted.startsWith("Today") }
    }
    val urgentCalls = remember(calls) {
        calls.count { it.urgency == UrgencyLevel.HIGH || it.urgency == UrgencyLevel.CRITICAL }
    }
    val avgDuration = remember(calls) {
        if (calls.isNotEmpty()) calls.map { it.durationSeconds }.average().toInt() else 0
    }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 32.dp)
    ) {
        // 1. Latest Urgent SMS Banner
        if (latestAlert != null) {
            item {
                SimulatedSmsBanner(
                    alert = latestAlert!!,
                    onDismiss = { CallAgentRepository.dismissLatestAlert() }
                )
            }
        }

        // 2. Main Agent Status Card (Switch & Status)
        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("agent_status_card"),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (settings.isAgentEnabled) {
                        MaterialTheme.colorScheme.surfaceVariant
                    } else {
                        MaterialTheme.colorScheme.surface
                    }
                ),
                border = CardDefaults.outlinedCardBorder().copy(
                    brush = if (settings.isAgentEnabled) {
                        Brush.horizontalGradient(listOf(PrimaryCyan, PrimaryIndigo))
                    } else {
                        androidx.compose.ui.graphics.SolidColor(MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))
                    }
                )
            ) {
                Column(modifier = Modifier.padding(18.dp)) {
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
                                    .size(44.dp)
                                    .clip(CircleShape)
                                    .background(
                                        if (settings.isAgentEnabled) PrimaryCyan.copy(alpha = 0.18f)
                                        else Color.Gray.copy(alpha = 0.15f)
                                    ),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(
                                    imageVector = Icons.Default.PhoneInTalk,
                                    contentDescription = null,
                                    tint = if (settings.isAgentEnabled) PrimaryCyan else Color.Gray,
                                    modifier = Modifier.size(24.dp)
                                )
                            }
                            Column {
                                Text(
                                    text = if (settings.isAgentEnabled) "AI Agent Active" else "AI Agent Paused",
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = MaterialTheme.colorScheme.onSurface
                                )
                                Text(
                                    text = if (settings.isAgentEnabled) "Answering & screening calls" else "Calls routing to voicemail",
                                    fontSize = 12.sp,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }

                        Switch(
                            checked = settings.isAgentEnabled,
                            onCheckedChange = { CallAgentRepository.toggleAgentStatus() },
                            modifier = Modifier.testTag("toggle_agent_switch")
                        )
                    }

                    Spacer(modifier = Modifier.height(16.dp))
                    HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.2f))
                    Spacer(modifier = Modifier.height(14.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(
                                text = "AI Virtual Phone",
                                fontSize = 11.sp,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Text(
                                text = settings.aiPhoneNumber,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }

                        Column(horizontalAlignment = Alignment.End) {
                            Text(
                                text = "Alert SMS Number",
                                fontSize = 11.sp,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            Text(
                                text = settings.ownerPhoneNumber,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = PrimaryCyan
                            )
                        }
                    }
                }
            }
        }

        // 3. Fast Simulation Action Bar
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surface
                ),
                border = CardDefaults.outlinedCardBorder().copy(
                    brush = androidx.compose.ui.graphics.SolidColor(PrimaryIndigo.copy(alpha = 0.4f))
                )
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.PlayCircleFilled,
                                contentDescription = null,
                                tint = PrimaryIndigo,
                                modifier = Modifier.size(20.dp)
                            )
                            Text(
                                text = "Interactive Simulation Engine",
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp,
                                color = MaterialTheme.colorScheme.onSurface
                            )
                        }
                        Text(
                            text = "Demo Mode",
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = PrimaryIndigo
                        )
                    }

                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Test call answering, speech turns, and instant SMS alerts without connecting real carrier trunks.",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    Spacer(modifier = Modifier.height(14.dp))
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(10.dp)
                    ) {
                        Button(
                            onClick = {
                                val record = CallAgentRepository.simulateCallScenario("outage")
                                onSelectCall(record)
                            },
                            modifier = Modifier
                                .weight(1f)
                                .testTag("btn_test_urgent_call"),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = UrgencyHigh
                            ),
                            shape = RoundedCornerShape(10.dp)
                        ) {
                            Icon(Icons.Default.Bolt, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("Test Urgent Outage", fontSize = 12.sp, fontWeight = FontWeight.Bold)
                        }

                        OutlinedButton(
                            onClick = { showSimulateModal = true },
                            modifier = Modifier
                                .weight(1f)
                                .testTag("btn_choose_scenario"),
                            shape = RoundedCornerShape(10.dp)
                        ) {
                            Icon(Icons.Default.Tune, contentDescription = null, modifier = Modifier.size(16.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("All Scenarios", fontSize = 12.sp)
                        }
                    }
                }
            }
        }

        // 4. Key Metrics Grid
        item {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    StatCard(
                        title = "Calls Today",
                        value = callsToday.toString(),
                        subtitle = "${calls.size} all-time",
                        icon = Icons.Default.Call,
                        accentColor = PrimaryCyan,
                        modifier = Modifier.weight(1f)
                    )
                    StatCard(
                        title = "Urgent Escalations",
                        value = urgentCalls.toString(),
                        subtitle = "SMS Alerted",
                        icon = Icons.Default.Warning,
                        accentColor = UrgencyHigh,
                        modifier = Modifier.weight(1f)
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    StatCard(
                        title = "Avg Call Duration",
                        value = "${avgDuration}s",
                        subtitle = "Target < 90s",
                        icon = Icons.Default.Timer,
                        accentColor = PrimaryIndigo,
                        modifier = Modifier.weight(1f)
                    )
                    StatCard(
                        title = "System Setup",
                        value = "Ready",
                        subtitle = "13 Steps Configured",
                        icon = Icons.Default.CheckCircle,
                        accentColor = UrgencyLow,
                        modifier = Modifier
                            .weight(1f)
                            .clickable { onNavigateToSetup() }
                    )
                }
            }
        }

        // 5. Recent Calls Section Header
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                SectionHeader(
                    title = "Recent Screened Calls",
                    subtitle = "Real-time incoming call log"
                )
                TextButton(onClick = onNavigateToCalls) {
                    Text("View All", color = PrimaryCyan, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                }
            }
        }

        // 6. Recent Calls List (Top 3)
        if (calls.isEmpty()) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f))
                ) {
                    Box(modifier = Modifier.padding(32.dp).fillMaxWidth(), contentAlignment = Alignment.Center) {
                        Text("No calls received yet. Try simulating a call above!", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        } else {
            items(calls.take(3)) { call ->
                CallItemRow(
                    call = call,
                    onClick = { onSelectCall(call) }
                )
            }
        }
    }

    // Simulation Scenario Dialog
    if (showSimulateModal) {
        AlertDialog(
            onDismissRequest = { showSimulateModal = false },
            title = { Text("Select Call Simulation Scenario", fontWeight = FontWeight.Bold) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Choose a scenario to test the AI conversational engine, urgency classifier, and SMS alert delivery:", fontSize = 13.sp)
                    Spacer(modifier = Modifier.height(4.dp))

                    val scenarios = listOf(
                        Triple("outage", "🚨 Website Outage (Urgent Client)", UrgencyHigh),
                        Triple("contract", "📑 Contract Deadline Today (Work)", UrgencyHigh),
                        Triple("family", "❤️ VIP Family Caller (Sister)", UrgencyMedium),
                        Triple("enquiry", "💼 General Consulting Hours Enquiry", UrgencyLow),
                        Triple("spam", "🚫 Unsolicited Loan Telemarketer", Color.Gray),
                        Triple("emergency", "⚠️ Life Safety / Hallway Smoke", UrgencyCritical)
                    )

                    scenarios.forEach { (key, label, color) ->
                        Surface(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .clickable {
                                    showSimulateModal = false
                                    val r = CallAgentRepository.simulateCallScenario(key)
                                    onSelectCall(r)
                                },
                            color = MaterialTheme.colorScheme.surfaceVariant
                        ) {
                            Row(
                                modifier = Modifier.padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(label, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                                Box(
                                    modifier = Modifier
                                        .size(10.dp)
                                        .clip(CircleShape)
                                        .background(color)
                                )
                            }
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showSimulateModal = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}
