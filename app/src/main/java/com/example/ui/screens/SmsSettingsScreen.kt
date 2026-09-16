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
import com.example.data.model.SmsAlertLog
import com.example.data.model.UrgencyLevel
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.SectionHeader
import com.example.ui.components.UrgencyBadge
import com.example.ui.theme.PrimaryCyan
import com.example.ui.theme.UrgencyHigh

@Composable
fun SmsSettingsScreen(
    modifier: Modifier = Modifier
) {
    val settings by CallAgentRepository.settings.collectAsState()
    val smsLogs by CallAgentRepository.smsLogs.collectAsState()

    var ownerPhone by remember(settings.ownerPhoneNumber) { mutableStateOf(settings.ownerPhoneNumber) }
    var selectedProvider by remember(settings.smsProvider) { mutableStateOf(settings.smsProvider) }
    var templateText by remember(settings.alertTemplate) { mutableStateOf(settings.alertTemplate) }
    var cooldownSlider by remember(settings.smsCooldownMinutes) { mutableStateOf(settings.smsCooldownMinutes.toFloat()) }

    var testDispatched by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 36.dp)
    ) {
        item {
            SectionHeader(
                title = "SMS Gateway & Alert Templates",
                subtitle = "Configure SMS delivery when high-urgency calls occur"
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
                    Text("SMS Gateway Provider", fontWeight = FontWeight.Bold, fontSize = 14.sp)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf("Twilio", "Exotel", "Plivo", "Mock (Demo)").forEach { prov ->
                            FilterChip(
                                selected = selectedProvider == prov,
                                onClick = {
                                    selectedProvider = prov
                                    CallAgentRepository.updateSettings(settings.copy(smsProvider = prov))
                                },
                                label = { Text(prov, fontSize = 12.sp) }
                            )
                        }
                    }

                    OutlinedTextField(
                        value = ownerPhone,
                        onValueChange = {
                            ownerPhone = it
                            CallAgentRepository.updateSettings(settings.copy(ownerPhoneNumber = it))
                        },
                        label = { Text("Owner Mobile Number (Destination)") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        leadingIcon = { Icon(Icons.Default.Smartphone, contentDescription = null) },
                        shape = RoundedCornerShape(10.dp)
                    )
                }
            }
        }

        // Alert Template Editor
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("Urgent SMS Notification Template", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text("Supported tokens: {caller}, {number}, {urgency}, {reason}, {summary}, {time}", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)

                    OutlinedTextField(
                        value = templateText,
                        onValueChange = {
                            templateText = it
                            CallAgentRepository.updateSettings(settings.copy(alertTemplate = it))
                        },
                        modifier = Modifier.fillMaxWidth(),
                        minLines = 5,
                        maxLines = 10,
                        shape = RoundedCornerShape(10.dp)
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        listOf("{caller}", "{reason}", "{summary}", "{time}").forEach { tag ->
                            SuggestionChip(
                                onClick = {
                                    templateText += " $tag"
                                    CallAgentRepository.updateSettings(settings.copy(alertTemplate = templateText))
                                },
                                label = { Text(tag, fontSize = 11.sp) }
                            )
                        }
                    }
                }
            }
        }

        // Cooldown & Test SMS Action
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Spam Suppression Cooldown", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text("${cooldownSlider.toInt()} min", fontWeight = FontWeight.Bold, color = PrimaryCyan)
                    }

                    Text("Prevents sending multiple SMS for repeated calls from same caller within this window.", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)

                    Slider(
                        value = cooldownSlider,
                        onValueChange = {
                            cooldownSlider = it
                            CallAgentRepository.updateSettings(settings.copy(smsCooldownMinutes = it.toInt()))
                        },
                        valueRange = 1f..30f,
                        steps = 28
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Button(
                        onClick = {
                            val newLog = SmsAlertLog(
                                id = "sms_${System.currentTimeMillis() % 1000}",
                                callerName = "Test Verification",
                                callerNumber = "+91 98765 00000",
                                urgency = UrgencyLevel.HIGH,
                                formattedMessage = templateText
                                    .replace("{caller}", "Test Verification")
                                    .replace("{number}", "+91 98765 00000")
                                    .replace("{urgency}", "HIGH")
                                    .replace("{reason}", "SMS Gateway Verification Ping")
                                    .replace("{summary}", "Test alert sent to confirm delivery to $ownerPhone")
                                    .replace("{time}", "Just now"),
                                timestamp = "Just now",
                                status = "DELIVERED",
                                provider = selectedProvider
                            )
                            CallAgentRepository.updateSettings(settings.copy(alertTemplate = templateText))
                            testDispatched = true
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .testTag("btn_send_test_sms"),
                        colors = ButtonDefaults.buttonColors(containerColor = UrgencyHigh),
                        shape = RoundedCornerShape(10.dp)
                    ) {
                        Icon(Icons.Default.Send, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Dispatch Test Alert SMS", fontWeight = FontWeight.Bold)
                    }

                    if (testDispatched) {
                        Text("Test SMS alert sent! Inspect simulated SMS banner on Dashboard.", color = PrimaryCyan, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }

        // SMS Dispatch Logs Header
        item {
            Text("Recent SMS Delivery Log", fontWeight = FontWeight.Bold, fontSize = 15.sp)
        }

        // SMS Logs
        items(smsLogs) { log ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            Icon(Icons.Default.CheckCircle, contentDescription = null, tint = PrimaryCyan, modifier = Modifier.size(16.dp))
                            Text("Sent to $ownerPhone", fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                        }
                        UrgencyBadge(urgency = log.urgency)
                    }
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(log.formattedMessage, fontSize = 11.sp, fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace, maxLines = 4)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("Provider: ${log.provider} • ${log.timestamp}", fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}
