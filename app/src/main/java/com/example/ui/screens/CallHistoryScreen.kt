package com.example.ui.screens

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.CallRecord
import com.example.data.model.CallStatus
import com.example.data.model.UrgencyLevel
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.CallItemRow
import com.example.ui.components.SectionHeader
import com.example.ui.theme.UrgencyHigh

@Composable
fun CallHistoryScreen(
    onSelectCall: (CallRecord) -> Unit,
    modifier: Modifier = Modifier
) {
    val calls by CallAgentRepository.calls.collectAsState()

    var searchQuery by remember { mutableStateOf("") }
    var selectedFilter by remember { mutableStateOf("All") }
    var showClearConfirm by remember { mutableStateOf(false) }

    val filteredCalls = remember(calls, searchQuery, selectedFilter) {
        calls.filter { call ->
            val matchesSearch = searchQuery.isBlank() ||
                    call.callerName.contains(searchQuery, ignoreCase = true) ||
                    call.callerNumber.contains(searchQuery, ignoreCase = true) ||
                    call.reason.contains(searchQuery, ignoreCase = true) ||
                    call.summary.contains(searchQuery, ignoreCase = true)

            val matchesFilter = when (selectedFilter) {
                "Today" -> call.timestampFormatted.startsWith("Today")
                "Yesterday" -> call.timestampFormatted.startsWith("Yesterday")
                "Urgent" -> call.urgency == UrgencyLevel.HIGH || call.urgency == UrgencyLevel.CRITICAL
                "Spam" -> call.status == CallStatus.SPAM
                else -> true
            }

            matchesSearch && matchesFilter
        }
    }

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp)
    ) {
        Spacer(modifier = Modifier.height(8.dp))

        // Search Bar
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            modifier = Modifier
                .fillMaxWidth()
                .testTag("call_search_field"),
            placeholder = { Text("Search caller, phone, reason...", fontSize = 14.sp) },
            leadingIcon = {
                Icon(Icons.Default.Search, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
            },
            trailingIcon = {
                if (searchQuery.isNotEmpty()) {
                    IconButton(onClick = { searchQuery = "" }) {
                        Icon(Icons.Default.Close, contentDescription = "Clear search")
                    }
                }
            },
            singleLine = true,
            shape = RoundedCornerShape(12.dp)
        )

        Spacer(modifier = Modifier.height(10.dp))

        // Filter Chips Row
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(rememberScrollState()),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            listOf("All", "Today", "Yesterday", "Urgent", "Spam").forEach { filterTag ->
                FilterChip(
                    selected = selectedFilter == filterTag,
                    onClick = { selectedFilter = filterTag },
                    label = { Text(filterTag) },
                    leadingIcon = if (filterTag == "Urgent" && selectedFilter == filterTag) {
                        { Icon(Icons.Default.Warning, contentDescription = null, tint = UrgencyHigh, modifier = Modifier.size(14.dp)) }
                    } else null
                )
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Header with count & Purge
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "${filteredCalls.size} Call${if (filteredCalls.size == 1) "" else "s"}",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            if (calls.isNotEmpty()) {
                TextButton(
                    onClick = { showClearConfirm = true },
                    contentPadding = PaddingValues(0.dp)
                ) {
                    Icon(Icons.Default.DeleteSweep, contentDescription = null, modifier = Modifier.size(16.dp), tint = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Clear All", fontSize = 12.sp, color = MaterialTheme.colorScheme.error)
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Calls List
        if (filteredCalls.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(bottom = 60.dp),
                contentAlignment = Alignment.Center
            ) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Icon(
                        imageVector = Icons.Default.PhoneMissed,
                        contentDescription = null,
                        modifier = Modifier.size(48.dp),
                        tint = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.5f)
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = "No matching calls found",
                        fontWeight = FontWeight.Medium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        } else {
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(10.dp),
                contentPadding = PaddingValues(bottom = 32.dp)
            ) {
                items(filteredCalls, key = { it.id }) { call ->
                    CallItemRow(
                        call = call,
                        onClick = { onSelectCall(call) }
                    )
                }
            }
        }
    }

    if (showClearConfirm) {
        AlertDialog(
            onDismissRequest = { showClearConfirm = false },
            title = { Text("Clear All Call History?") },
            text = { Text("This will permanently delete all call recordings, summaries, and transcripts. This action complies with data privacy regulations.") },
            confirmButton = {
                Button(
                    onClick = {
                        CallAgentRepository.clearAllCalls()
                        showClearConfirm = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
                ) {
                    Text("Clear History")
                }
            },
            dismissButton = {
                TextButton(onClick = { showClearConfirm = false }) {
                    Text("Cancel")
                }
            }
        )
    }
}
