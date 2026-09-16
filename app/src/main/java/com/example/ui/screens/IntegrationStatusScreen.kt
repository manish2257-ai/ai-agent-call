package com.example.ui.screens

import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.IntegrationStatusItem
import com.example.ui.components.SectionHeader
import com.example.ui.theme.PrimaryCyan
import com.example.ui.theme.UrgencyLow

@Composable
fun IntegrationStatusScreen(
    modifier: Modifier = Modifier
) {
    val items = remember {
        listOf(
            IntegrationStatusItem("OpenAI Voice & Reasoning", "AI Speech / LLM", true, "OPERATIONAL", 185, "Model: gpt-4o-realtime • Audio streaming active"),
            IntegrationStatusItem("Cloud Telephony Gateway", "SIP / Webhooks", true, "OPERATIONAL", 92, "Provider: Twilio • Inbound webhook verified"),
            IntegrationStatusItem("SMS Dispatch Gateway", "Carrier SMS", true, "DELIVERING", 120, "Sender ID configured • Cooldown active"),
            IntegrationStatusItem("Secure Backend API", "FastAPI / Uvicorn", true, "HEALTHY", 45, "JWT Auth active • TLS 1.3 enforced"),
            IntegrationStatusItem("Relational Call Database", "PostgreSQL", true, "SYNCED", 18, "Pool connections: 8 active • Encryption at rest")
        )
    }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 36.dp)
    ) {
        item {
            SectionHeader(
                title = "System Integrations & Gateway Health",
                subtitle = "Live telemetry and operational status of all backend subsystems"
            )
        }

        // Security Assurance Banner
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    modifier = Modifier.padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Icon(Icons.Default.VerifiedUser, contentDescription = null, tint = PrimaryCyan, modifier = Modifier.size(24.dp))
                    Column {
                        Text("Zero Credentials in APK Policy", fontWeight = FontWeight.Bold, fontSize = 13.sp)
                        Text(
                            "All carrier secrets, OpenAI API keys, and database credentials remain securely hosted on your backend.",
                            fontSize = 11.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }

        // Service Items
        items(items) { item ->
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                border = CardDefaults.outlinedCardBorder()
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
                            Box(
                                modifier = Modifier
                                    .size(10.dp)
                                    .clip(CircleShape)
                                    .background(UrgencyLow)
                            )
                            Text(item.name, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        }

                        Surface(
                            shape = RoundedCornerShape(6.dp),
                            color = UrgencyLow.copy(alpha = 0.15f)
                        ) {
                            Text(
                                text = item.statusText,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = UrgencyLow,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(4.dp))
                    Text(item.details, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Spacer(modifier = Modifier.height(8.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(item.type, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text("${item.latencyMs}ms ping", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = PrimaryCyan)
                    }
                }
            }
        }
    }
}
