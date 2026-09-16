package com.example.ui.screens

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
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.UrgencyLevel
import com.example.data.model.UrgencyRule
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.SectionHeader
import com.example.ui.components.UrgencyBadge
import com.example.ui.theme.PrimaryCyan

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun UrgencyRulesScreen(
    modifier: Modifier = Modifier
) {
    val settings by CallAgentRepository.settings.collectAsState()
    val rules by CallAgentRepository.rules.collectAsState()

    var showAddDialog by remember { mutableStateOf(false) }
    var newTitle by remember { mutableStateOf("") }
    var newConditionType by remember { mutableStateOf("KEYWORD") }
    var newConditionValue by remember { mutableStateOf("") }
    var newAction by remember { mutableStateOf("SMS") }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 36.dp)
    ) {
        item {
            SectionHeader(
                title = "Urgency Engine & Escalation Rules",
                subtitle = "Define when the AI alerts you via SMS or transfers the call"
            )
        }

        // Global Alert Threshold Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Minimum Urgency for SMS Alert", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text("Only calls categorized at or above this level trigger immediate SMS alerts.", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        UrgencyLevel.values().forEach { level ->
                            FilterChip(
                                selected = settings.urgencyThreshold == level,
                                onClick = {
                                    CallAgentRepository.updateSettings(settings.copy(urgencyThreshold = level))
                                },
                                label = { Text(level.name, fontSize = 12.sp) }
                            )
                        }
                    }
                }
            }
        }

        // Rules Header + Add Button
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Configured Evaluation Rules", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                FilledTonalButton(
                    onClick = { showAddDialog = true },
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                ) {
                    Icon(Icons.Default.Add, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Add Rule", fontSize = 12.sp)
                }
            }
        }

        // Rules List
        items(rules, key = { it.id }) { rule ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = CardDefaults.outlinedCardBorder()
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(rule.title, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "Condition: ${rule.conditionType} -> '${rule.conditionValue}'",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "Action: ${rule.action}",
                            fontSize = 11.sp,
                            color = PrimaryCyan,
                            fontWeight = FontWeight.SemiBold
                        )
                    }

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Switch(
                            checked = rule.isEnabled,
                            onCheckedChange = { CallAgentRepository.toggleRule(rule.id) }
                        )
                        IconButton(onClick = { CallAgentRepository.deleteRule(rule.id) }) {
                            Icon(Icons.Default.DeleteOutline, contentDescription = "Delete", tint = MaterialTheme.colorScheme.error)
                        }
                    }
                }
            }
        }
    }

    if (showAddDialog) {
        AlertDialog(
            onDismissRequest = { showAddDialog = false },
            title = { Text("Add Urgency Evaluation Rule") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    OutlinedTextField(
                        value = newTitle,
                        onValueChange = { newTitle = it },
                        label = { Text("Rule Title") },
                        modifier = Modifier.fillMaxWidth()
                    )

                    OutlinedTextField(
                        value = newConditionValue,
                        onValueChange = { newConditionValue = it },
                        label = { Text("Match Value (Keywords / Condition)") },
                        modifier = Modifier.fillMaxWidth(),
                        placeholder = { Text("e.g. server crash, emergency") }
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        listOf("SMS", "CALL_TRANSFER", "NO_ALERT").forEach { act ->
                            FilterChip(
                                selected = newAction == act,
                                onClick = { newAction = act },
                                label = { Text(act, fontSize = 11.sp) }
                            )
                        }
                    }
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        if (newTitle.isNotBlank()) {
                            CallAgentRepository.addRule(
                                UrgencyRule(
                                    id = "rule_${System.currentTimeMillis() % 1000}",
                                    title = newTitle,
                                    conditionType = newConditionType,
                                    conditionValue = newConditionValue.ifBlank { "custom" },
                                    action = newAction,
                                    isEnabled = true
                                )
                            )
                            showAddDialog = false
                            newTitle = ""
                            newConditionValue = ""
                        }
                    }
                ) {
                    Text("Add Rule")
                }
            },
            dismissButton = {
                TextButton(onClick = { showAddDialog = false }) { Text("Cancel") }
            }
        )
    }
}
