package com.example.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.CallRecord

@Composable
fun CallsScreen(
    calls: List<CallRecord>,
    onRefresh: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedFilter by remember { mutableStateOf("All") }
    var selectedCallDetails by remember { mutableStateOf<CallRecord?>(null) }

    val filteredCalls = remember(calls, selectedFilter) {
        when (selectedFilter) {
            "Urgent" -> calls.filter { it.urgency == "HIGH" || it.urgency == "CRITICAL" }
            else -> calls
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Filter Chips Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            FilterChip(
                selected = selectedFilter == "All",
                onClick = { selectedFilter = "All" },
                label = { Text("All (${calls.size})") },
                modifier = Modifier.testTag("filter_all")
            )
            FilterChip(
                selected = selectedFilter == "Urgent",
                onClick = { selectedFilter = "Urgent" },
                label = { Text("Urgent (${calls.count { it.urgency == "HIGH" || it.urgency == "CRITICAL" }})") },
                modifier = Modifier.testTag("filter_urgent")
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (filteredCalls.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .testTag("calls_empty_state"),
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                    modifier = Modifier.padding(32.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.PhoneMissed,
                        contentDescription = null,
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(56.dp)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = "No calls yet",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "Real incoming calls handled by Exotel Telephony and your AI Voicebot will appear here in real-time.",
                        fontSize = 13.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        lineHeight = 18.sp,
                        modifier = Modifier.align(Alignment.CenterHorizontally)
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    OutlinedButton(
                        onClick = onRefresh,
                        modifier = Modifier.testTag("refresh_calls_btn")
                    ) {
                        Icon(imageVector = Icons.Default.Refresh, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Refresh List")
                    }
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .testTag("calls_list"),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                items(filteredCalls, key = { it.id }) { call ->
                    CallItemCard(
                        call = call,
                        onClick = { selectedCallDetails = call }
                    )
                }
            }
        }
    }

    // Detail dialog
    if (selectedCallDetails != null) {
        val call = selectedCallDetails!!
        AlertDialog(
            onDismissRequest = { selectedCallDetails = null },
            title = {
                Text(
                    text = call.callerName,
                    fontWeight = FontWeight.Bold
                )
            },
            text = {
                Column(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Number: ${call.callerNumber}",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Text(
                        text = "Urgency: ${call.urgency}",
                        fontWeight = FontWeight.SemiBold,
                        color = if (call.urgency == "HIGH" || call.urgency == "CRITICAL")
                            Color(0xFFF97316)
                        else
                            MaterialTheme.colorScheme.primary
                    )
                    if (call.durationSeconds > 0) {
                        Text(
                            text = "Duration: ${call.durationSeconds}s",
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                    if (call.reason.isNotEmpty()) {
                        Divider()
                        Text(
                            text = "Reason for Call:",
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(text = call.reason)
                    }
                    if (call.summary.isNotEmpty()) {
                        Divider()
                        Text(
                            text = "AI Call Summary:",
                            fontWeight = FontWeight.SemiBold
                        )
                        Text(text = call.summary)
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { selectedCallDetails = null }) {
                    Text("Close")
                }
            }
        )
    }
}

@Composable
fun CallItemCard(
    call: CallRecord,
    onClick: () -> Unit
) {
    val isUrgent = call.urgency == "HIGH" || call.urgency == "CRITICAL"

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .testTag("call_item_${call.id}"),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        shape = RoundedCornerShape(14.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (isUrgent) Icons.Default.NotificationImportant else Icons.Default.PhoneCallback,
                contentDescription = null,
                tint = if (isUrgent) Color(0xFFF97316) else MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = call.callerName,
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Surface(
                        color = if (isUrgent) Color(0xFFF97316).copy(alpha = 0.2f) else MaterialTheme.colorScheme.primaryContainer,
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        Text(
                            text = call.urgency,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp),
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (isUrgent) Color(0xFFF97316) else MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                }
                Text(
                    text = call.callerNumber,
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                if (call.summary.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = call.summary,
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurface,
                        maxLines = 2
                    )
                }
            }
        }
    }
}
