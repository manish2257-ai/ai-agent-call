package com.example.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.AppConfigState

@Composable
fun AiRulesScreen(
    config: AppConfigState,
    onToggleAgent: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(scrollState)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "AI Agent Configuration",
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp,
            color = MaterialTheme.colorScheme.primary
        )

        // Agent Toggle Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("ai_agent_switch_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.SmartToy,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(28.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "AI Receptionist Switch",
                        fontWeight = FontWeight.Bold,
                        fontSize = 15.sp,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    Text(
                        text = if (config.agentEnabled) "Active - Screening incoming calls" else "Disabled - Calls routed directly",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Switch(
                    checked = config.agentEnabled,
                    onCheckedChange = onToggleAgent,
                    modifier = Modifier.testTag("ai_agent_toggle")
                )
            }
        }

        // Configuration Parameters Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("ai_config_params_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                Text(
                    text = "Phone Numbers & Personality",
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 15.sp,
                    color = MaterialTheme.colorScheme.onSurface
                )

                // Virtual Number
                ConfigFieldItem(
                    label = "AI Virtual Phone Number",
                    value = config.aiPhoneNumber,
                    icon = Icons.Default.Phone
                )

                Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))

                // Owner Number
                ConfigFieldItem(
                    label = "Owner Mobile Number",
                    value = config.ownerPhoneNumber,
                    icon = Icons.Default.Person
                )

                Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))

                // Greeting
                ConfigFieldItem(
                    label = "Introductory Greeting",
                    value = config.greeting,
                    icon = Icons.Default.RecordVoiceOver
                )

                Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))

                // Urgency Threshold
                ConfigFieldItem(
                    label = "Urgency Escalation Threshold",
                    value = config.urgencyThreshold,
                    icon = Icons.Default.Speed
                )
            }
        }

        // Urgency Classification Rules
        Text(
            text = "Urgency Classification Rules",
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp,
            color = MaterialTheme.colorScheme.primary
        )

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("urgency_rules_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                RuleItem(
                    level = "CRITICAL",
                    color = Color(0xFFEF4444),
                    description = "Medical emergencies, safety hazards, critical server downtime",
                    action = "Immediate SMS & WhatsApp dispatch to owner"
                )
                Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))
                RuleItem(
                    level = "HIGH",
                    color = Color(0xFFF97316),
                    description = "Urgent business transactions, high-priority appointments, same-day deadlines",
                    action = "Priority SMS notification to owner"
                )
                Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))
                RuleItem(
                    level = "MEDIUM",
                    color = Color(0xFF38BDF8),
                    description = "General inquiries, standard scheduling, routine inquiries",
                    action = "Saved to call log with summary"
                )
                Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))
                RuleItem(
                    level = "LOW",
                    color = Color(0xFF94A3B8),
                    description = "Telemarketers, robo-calls, promotional sales, silent callers",
                    action = "Screened silently without alerting owner"
                )
            }
        }
    }
}

@Composable
fun ConfigFieldItem(
    label: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Top
    ) {
        Icon(
            imageVector = icon,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary,
            modifier = Modifier
                .size(20.dp)
                .padding(top = 2.dp)
        )
        Spacer(modifier = Modifier.width(10.dp))
        Column {
            Text(
                text = label,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = value,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = if (value == "Not configured" || value == "Unavailable")
                    MaterialTheme.colorScheme.onSurfaceVariant
                else
                    MaterialTheme.colorScheme.onSurface
            )
        }
    }
}

@Composable
fun RuleItem(
    level: String,
    color: Color,
    description: String,
    action: String
) {
    Column {
        Row(
            verticalAlignment = Alignment.CenterVertically
        ) {
            Surface(
                color = color.copy(alpha = 0.2f),
                shape = RoundedCornerShape(4.dp)
            ) {
                Text(
                    text = level,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    color = color,
                    modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = action,
                fontSize = 12.sp,
                fontWeight = FontWeight.SemiBold,
                color = MaterialTheme.colorScheme.onSurface
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = description,
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}
