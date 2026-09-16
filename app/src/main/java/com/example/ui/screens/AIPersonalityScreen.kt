package com.example.ui.screens

import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.AIPersonalityPreset
import com.example.data.repository.CallAgentRepository
import com.example.ui.theme.PrimaryCyan
import com.example.ui.theme.UrgencyCritical
import com.example.ui.theme.UrgencyCriticalBg

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AIPersonalityScreen(
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val settings by CallAgentRepository.settings.collectAsState()

    var selectedPreset by remember(settings.personality) { mutableStateOf(settings.personality) }
    var customPrompt by remember(settings.customSystemPrompt) { mutableStateOf(settings.customSystemPrompt) }
    var savedNotice by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("AI Personality & Prompt", fontWeight = FontWeight.Bold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
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
            // Presets Header
            item {
                Text(
                    text = "Personality Presets",
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = "Tunes tone, pacing, and conversational style",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // Presets Cards
            items(AIPersonalityPreset.values()) { preset ->
                val isSelected = selectedPreset == preset
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .clickable { selectedPreset = preset },
                    colors = CardDefaults.cardColors(
                        containerColor = if (isSelected) MaterialTheme.colorScheme.surfaceVariant else MaterialTheme.colorScheme.surface
                    ),
                    border = CardDefaults.outlinedCardBorder().copy(
                        brush = androidx.compose.ui.graphics.SolidColor(
                            if (isSelected) PrimaryCyan else MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
                        )
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(preset.title, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                            Spacer(modifier = Modifier.height(3.dp))
                            Text(preset.description, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        RadioButton(
                            selected = isSelected,
                            onClick = { selectedPreset = preset }
                        )
                    }
                }
            }

            // Custom Prompt Editor
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
                ) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text("Custom System Prompt (Optional Override)", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text(
                            "Add specific rules (e.g. 'Always ask for the caller's company name', 'Do not disclose vacation dates').",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )

                        OutlinedTextField(
                            value = customPrompt,
                            onValueChange = { customPrompt = it },
                            modifier = Modifier.fillMaxWidth(),
                            minLines = 4,
                            maxLines = 8,
                            placeholder = { Text("Enter custom system prompt rules...", fontSize = 13.sp) },
                            shape = RoundedCornerShape(10.dp)
                        )
                    }
                }
            }

            // Safety Protocols Warning Box
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    colors = CardDefaults.cardColors(containerColor = UrgencyCriticalBg),
                    border = CardDefaults.outlinedCardBorder().copy(
                        brush = androidx.compose.ui.graphics.SolidColor(UrgencyCritical.copy(alpha = 0.5f))
                    )
                ) {
                    Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Icon(Icons.Default.Security, contentDescription = null, tint = UrgencyCritical, modifier = Modifier.size(18.dp))
                            Text("Enforced Safety & Compliance Directives", fontWeight = FontWeight.Bold, fontSize = 13.sp, color = UrgencyCritical)
                        }
                        Text("• Anti-Impersonation: The agent never lies about being an AI.\n• Zero Sensitive Credentials: Never asks for OTPs, PINs, or bank passwords.\n• Emergency Redirection: Directed to call 112 / 911 for life safety.", fontSize = 12.sp, lineHeight = 16.sp)
                    }
                }
            }

            // Save Button
            item {
                Button(
                    onClick = {
                        CallAgentRepository.updateSettings(
                            settings.copy(
                                personality = selectedPreset,
                                customSystemPrompt = customPrompt
                            )
                        )
                        savedNotice = true
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("Apply Personality Changes", fontWeight = FontWeight.Bold)
                }

                if (savedNotice) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Personality updated successfully!", color = PrimaryCyan, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                }
            }
        }
    }
}
