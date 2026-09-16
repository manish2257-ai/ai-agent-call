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
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.SectionHeader
import com.example.ui.theme.PrimaryCyan

@Composable
fun TelephonySettingsScreen(
    onNavigateToForwardingGuide: () -> Unit,
    modifier: Modifier = Modifier
) {
    val settings by CallAgentRepository.settings.collectAsState()
    val clipboard = LocalClipboardManager.current

    var selectedProvider by remember(settings.telephonyProvider) { mutableStateOf(settings.telephonyProvider) }
    var aiNumber by remember(settings.aiPhoneNumber) { mutableStateOf(settings.aiPhoneNumber) }
    var copiedNotice by remember { mutableStateOf<String?>(null) }

    val webhookIncoming = "https://api.yourdomain.com/webhooks/telephony/incoming"
    val webhookStatus = "https://api.yourdomain.com/webhooks/telephony/status"

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 36.dp)
    ) {
        item {
            SectionHeader(
                title = "Telephony Carrier & Webhooks",
                subtitle = "Manage cloud carrier trunks and webhook routing"
            )
        }

        // Provider Selector Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Voice Telephony Carrier", fontWeight = FontWeight.Bold, fontSize = 14.sp)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf("Twilio", "Exotel", "Plivo").forEach { prov ->
                            FilterChip(
                                selected = selectedProvider == prov,
                                onClick = {
                                    selectedProvider = prov
                                    CallAgentRepository.updateSettings(settings.copy(telephonyProvider = prov))
                                },
                                label = { Text(prov, fontSize = 12.sp) }
                            )
                        }
                    }

                    OutlinedTextField(
                        value = aiNumber,
                        onValueChange = {
                            aiNumber = it
                            CallAgentRepository.updateSettings(settings.copy(aiPhoneNumber = it))
                        },
                        label = { Text("Carrier Virtual Number") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        leadingIcon = { Icon(Icons.Default.PhoneInTalk, contentDescription = null) },
                        shape = RoundedCornerShape(10.dp)
                    )
                }
            }
        }

        // Webhook URLs Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Carrier Webhook Endpoints", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text("Configure these in your carrier console (Twilio / Exotel / Plivo) under Phone Numbers > Voice.", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)

                    // Incoming URL
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp),
                        color = MaterialTheme.colorScheme.surfaceVariant
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text("A Call Comes In (POST)", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = PrimaryCyan)
                                Text(webhookIncoming, fontSize = 12.sp, fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace)
                            }
                            IconButton(onClick = {
                                clipboard.setText(AnnotatedString(webhookIncoming))
                                copiedNotice = "Copied Incoming Webhook URL"
                            }) {
                                Icon(Icons.Default.ContentCopy, contentDescription = "Copy")
                            }
                        }
                    }

                    // Status URL
                    Surface(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp),
                        color = MaterialTheme.colorScheme.surfaceVariant
                    ) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text("Call Status Changes (POST)", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = PrimaryCyan)
                                Text(webhookStatus, fontSize = 12.sp, fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace)
                            }
                            IconButton(onClick = {
                                clipboard.setText(AnnotatedString(webhookStatus))
                                copiedNotice = "Copied Status Webhook URL"
                            }) {
                                Icon(Icons.Default.ContentCopy, contentDescription = "Copy")
                            }
                        }
                    }

                    if (copiedNotice != null) {
                        Text(copiedNotice!!, color = PrimaryCyan, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }

        // Call Forwarding Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(Icons.Default.PhoneForwarded, contentDescription = null, tint = PrimaryCyan)
                        Text("Carrier Conditional Call Forwarding", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    }

                    Text(
                        "Route missed, unanswered, or busy calls from your personal SIM card directly to the AI number using standard USSD codes.",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    Button(
                        onClick = onNavigateToForwardingGuide,
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Text("View Carrier USSD Forwarding Codes")
                    }
                }
            }
        }
    }
}
