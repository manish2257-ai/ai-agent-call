package com.example.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.SectionHeader
import com.example.ui.theme.PrimaryCyan

@Composable
fun PrivacyAccountScreen(
    onSignOut: () -> Unit,
    modifier: Modifier = Modifier
) {
    val settings by CallAgentRepository.settings.collectAsState()

    var transcriptToggle by remember(settings.isTranscriptStorageEnabled) { mutableStateOf(settings.isTranscriptStorageEnabled) }
    var audioToggle by remember(settings.isAudioRecordingEnabled) { mutableStateOf(settings.isAudioRecordingEnabled) }
    var retentionDays by remember(settings.retentionDays) { mutableStateOf(settings.retentionDays) }
    var showPurgeConfirm by remember { mutableStateOf(false) }
    var purgedMessage by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 36.dp)
    ) {
        item {
            SectionHeader(
                title = "Privacy, Security & Account",
                subtitle = "Call recording consent, data retention, and account controls"
            )
        }

        // Account Profile Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("Owner Profile", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    Text("Manish Kumar", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                    Text("manish@aicallagent.com", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(settings.ownerPhoneNumber, fontSize = 12.sp, color = PrimaryCyan, fontWeight = FontWeight.Medium)
                }
            }
        }

        // Recording & Privacy Toggles
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    Text("Privacy & Recording Controls", fontWeight = FontWeight.Bold, fontSize = 14.sp)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Store Text Transcripts", fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                            Text("Save conversational transcripts to review in call details", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Switch(
                            checked = transcriptToggle,
                            onCheckedChange = {
                                transcriptToggle = it
                                CallAgentRepository.updateSettings(settings.copy(isTranscriptStorageEnabled = it))
                            }
                        )
                    }

                    HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.2f))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Store Raw Audio Recordings", fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                            Text("Keep audio recordings on cloud storage (requires consent notice)", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Switch(
                            checked = audioToggle,
                            onCheckedChange = {
                                audioToggle = it
                                CallAgentRepository.updateSettings(settings.copy(isAudioRecordingEnabled = it))
                            }
                        )
                    }
                }
            }
        }

        // Data Retention Period
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("Data Retention Policy", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text("Automatically purge calls older than selected period", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf(7, 30, 90, 365).forEach { days ->
                            FilterChip(
                                selected = retentionDays == days,
                                onClick = {
                                    retentionDays = days
                                    CallAgentRepository.updateSettings(settings.copy(retentionDays = days))
                                },
                                label = { Text("$days Days", fontSize = 12.sp) }
                            )
                        }
                    }
                }
            }
        }

        // Purge Data Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Permanent Data Deletion", fontWeight = FontWeight.Bold, fontSize = 14.sp, color = MaterialTheme.colorScheme.error)
                    Text(
                        "Delete all stored call logs, transcripts, and summaries from your device and backend database.",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    OutlinedButton(
                        onClick = { showPurgeConfirm = true },
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.error),
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Icon(Icons.Default.DeleteForever, contentDescription = null, modifier = Modifier.size(18.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Purge All Call History Now")
                    }

                    if (purgedMessage) {
                        Text("All call records have been purged.", color = PrimaryCyan, fontSize = 12.sp)
                    }
                }
            }
        }

        // Sign Out Button
        item {
            Button(
                onClick = onSignOut,
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Icon(Icons.Default.Logout, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text("Sign Out of Control App", color = MaterialTheme.colorScheme.onSurface)
            }
        }
    }

    if (showPurgeConfirm) {
        AlertDialog(
            onDismissRequest = { showPurgeConfirm = false },
            title = { Text("Confirm Data Purge") },
            text = { Text("Are you sure you want to permanently delete all call recordings and transcripts? This action cannot be undone.") },
            confirmButton = {
                Button(
                    onClick = {
                        CallAgentRepository.clearAllCalls()
                        showPurgeConfirm = false
                        purgedMessage = true
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
                ) {
                    Text("Purge Everything")
                }
            },
            dismissButton = {
                TextButton(onClick = { showPurgeConfirm = false }) { Text("Cancel") }
            }
        )
    }
}
