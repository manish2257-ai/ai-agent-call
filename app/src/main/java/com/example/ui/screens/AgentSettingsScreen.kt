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
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.SectionHeader
import com.example.ui.theme.PrimaryCyan

@Composable
fun AgentSettingsScreen(
    onNavigateToPersonality: () -> Unit,
    modifier: Modifier = Modifier
) {
    val settings by CallAgentRepository.settings.collectAsState()

    var greetingText by remember(settings.greeting) { mutableStateOf(settings.greeting) }
    var selectedLanguage by remember(settings.languageMode) { mutableStateOf(settings.languageMode) }
    var durationSlider by remember(settings.maxCallDurationMinutes) { mutableStateOf(settings.maxCallDurationMinutes.toFloat()) }
    var transferEnabled by remember(settings.isTransferEnabled) { mutableStateOf(settings.isTransferEnabled) }
    var ownerNumber by remember(settings.ownerPhoneNumber) { mutableStateOf(settings.ownerPhoneNumber) }
    var aiNumber by remember(settings.aiPhoneNumber) { mutableStateOf(settings.aiPhoneNumber) }

    var saveSuccess by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 36.dp)
    ) {
        item {
            SectionHeader(
                title = "AI Agent Configuration",
                subtitle = "Call answering behavior, greeting, and routing controls"
            )
        }

        // Active State Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("AI Call Agent Switch", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                        Text(
                            if (settings.isAgentEnabled) "Active & answering callers" else "Paused (calls forward to voicemail)",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Switch(
                        checked = settings.isAgentEnabled,
                        onCheckedChange = { CallAgentRepository.toggleAgentStatus() }
                    )
                }
            }
        }

        // Phone Numbers Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Configured Phone Numbers", fontWeight = FontWeight.Bold, fontSize = 14.sp)

                    OutlinedTextField(
                        value = aiNumber,
                        onValueChange = { aiNumber = it },
                        label = { Text("AI Virtual Phone Number") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        leadingIcon = { Icon(Icons.Default.PhoneInTalk, contentDescription = null) },
                        shape = RoundedCornerShape(10.dp)
                    )

                    OutlinedTextField(
                        value = ownerNumber,
                        onValueChange = { ownerNumber = it },
                        label = { Text("Owner Mobile Number (Alerts & Transfers)") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        leadingIcon = { Icon(Icons.Default.Smartphone, contentDescription = null) },
                        shape = RoundedCornerShape(10.dp)
                    )
                }
            }
        }

        // Greeting Message Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text("Introductory Greeting", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text("Spoken first", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }

                    OutlinedTextField(
                        value = greetingText,
                        onValueChange = { greetingText = it },
                        modifier = Modifier.fillMaxWidth(),
                        minLines = 3,
                        maxLines = 5,
                        shape = RoundedCornerShape(10.dp)
                    )

                    Text(
                        text = "Note: Standard policy requires the AI to disclose it is an assistant and identify you as the owner.",
                        fontSize = 11.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }

        // Language & Personality Link Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Language & Accent Mode", fontWeight = FontWeight.Bold, fontSize = 14.sp)

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        listOf("English", "Hindi", "Hinglish", "Auto").forEach { lang ->
                            FilterChip(
                                selected = selectedLanguage == lang,
                                onClick = { selectedLanguage = lang },
                                label = { Text(lang, fontSize = 12.sp) }
                            )
                        }
                    }

                    HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.2f))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Personality & Prompt", fontWeight = FontWeight.SemiBold, fontSize = 14.sp)
                            Text("Current: ${settings.personality.title}", fontSize = 12.sp, color = PrimaryCyan)
                        }
                        OutlinedButton(onClick = onNavigateToPersonality) {
                            Text("Customize")
                        }
                    }
                }
            }
        }

        // Call Duration & Transfer Limits
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
                        Text("Maximum Call Duration", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text("${durationSlider.toInt()} minutes", fontWeight = FontWeight.Bold, color = PrimaryCyan)
                    }

                    Slider(
                        value = durationSlider,
                        onValueChange = { durationSlider = it },
                        valueRange = 1f..10f,
                        steps = 8
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text("Allow Direct Live Call Transfers", fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                            Text("Enables forwarding urgent callers to your phone", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Switch(
                            checked = transferEnabled,
                            onCheckedChange = { transferEnabled = it }
                        )
                    }
                }
            }
        }

        // Save Button
        item {
            Button(
                onClick = {
                    CallAgentRepository.updateSettings(
                        settings.copy(
                            greeting = greetingText,
                            languageMode = selectedLanguage,
                            maxCallDurationMinutes = durationSlider.toInt(),
                            isTransferEnabled = transferEnabled,
                            ownerPhoneNumber = ownerNumber,
                            aiPhoneNumber = aiNumber
                        )
                    )
                    saveSuccess = true
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .testTag("btn_save_agent_settings"),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.Save, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text("Save Configuration", fontWeight = FontWeight.Bold)
            }

            if (saveSuccess) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Settings successfully updated!",
                    color = PrimaryCyan,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.padding(horizontal = 4.dp)
                )
            }
        }
    }
}
