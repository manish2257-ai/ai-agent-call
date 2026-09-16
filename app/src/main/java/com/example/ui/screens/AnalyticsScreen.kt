package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
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
import com.example.data.model.CallStatus
import com.example.data.model.UrgencyLevel
import com.example.data.repository.CallAgentRepository
import com.example.ui.components.SectionHeader
import com.example.ui.components.StatCard
import com.example.ui.theme.*

@Composable
fun AnalyticsScreen(
    modifier: Modifier = Modifier
) {
    val calls by CallAgentRepository.calls.collectAsState()

    val totalCalls = calls.size
    val lowCalls = calls.count { it.urgency == UrgencyLevel.LOW }
    val medCalls = calls.count { it.urgency == UrgencyLevel.MEDIUM }
    val highCalls = calls.count { it.urgency == UrgencyLevel.HIGH }
    val critCalls = calls.count { it.urgency == UrgencyLevel.CRITICAL }

    val transferred = calls.count { it.status == CallStatus.TRANSFERRED }
    val escalated = calls.count { it.status == CallStatus.ESCALATED }
    val spam = calls.count { it.status == CallStatus.SPAM }

    LazyColumn(
        modifier = modifier
            .fillMaxSize()
            .padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
        contentPadding = PaddingValues(top = 12.dp, bottom = 36.dp)
    ) {
        item {
            SectionHeader(
                title = "Call Analytics & Intelligence",
                subtitle = "Screening metrics, urgency distributions, and call trends"
            )
        }

        // Summary Stats Grid
        item {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    StatCard(
                        title = "Screened Calls",
                        value = totalCalls.toString(),
                        subtitle = "100% automated",
                        icon = Icons.Default.Analytics,
                        accentColor = PrimaryCyan,
                        modifier = Modifier.weight(1f)
                    )
                    StatCard(
                        title = "Urgent Escalated",
                        value = escalated.toString(),
                        subtitle = "SMS Dispatched",
                        icon = Icons.Default.PriorityHigh,
                        accentColor = UrgencyHigh,
                        modifier = Modifier.weight(1f)
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    StatCard(
                        title = "Transferred Calls",
                        value = transferred.toString(),
                        subtitle = "Connected to phone",
                        icon = Icons.Default.PhoneForwarded,
                        accentColor = PrimaryIndigo,
                        modifier = Modifier.weight(1f)
                    )
                    StatCard(
                        title = "Spam Filtered",
                        value = spam.toString(),
                        subtitle = "Time saved",
                        icon = Icons.Default.Shield,
                        accentColor = UrgencyLow,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }

        // Urgency Distribution Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                    Text("Urgency Level Distribution", fontWeight = FontWeight.Bold, fontSize = 14.sp)

                    UrgencyBarItem("Low Urgency (Enquiries)", lowCalls, totalCalls, UrgencyLow)
                    UrgencyBarItem("Medium Urgency (Scheduling)", medCalls, totalCalls, UrgencyMedium)
                    UrgencyBarItem("High Urgency (Client Outages)", highCalls, totalCalls, UrgencyHigh)
                    UrgencyBarItem("Critical Urgency (Emergencies)", critCalls, totalCalls, UrgencyCritical)
                }
            }
        }

        // Hourly Activity Preview Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text("Peak Calling Hours", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    Text("Historical volume distribution during working hours", fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(100.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.Bottom
                    ) {
                        val hourlyData = listOf(
                            Pair("9 AM", 0.4f),
                            Pair("11 AM", 0.85f),
                            Pair("1 PM", 0.3f),
                            Pair("3 PM", 0.95f),
                            Pair("5 PM", 0.6f)
                        )

                        hourlyData.forEach { (label, frac) ->
                            Column(
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Bottom,
                                modifier = Modifier.weight(1f)
                            ) {
                                Box(
                                    modifier = Modifier
                                        .fillMaxWidth(0.5f)
                                        .fillMaxHeight(frac)
                                        .clip(RoundedCornerShape(topStart = 6.dp, topEnd = 6.dp))
                                        .background(PrimaryCyan)
                                )
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(label, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun UrgencyBarItem(
    label: String,
    count: Int,
    total: Int,
    color: Color
) {
    val percent = if (total > 0) (count.toFloat() / total) else 0f
    val percentText = "${(percent * 100).toInt()}%"

    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(label, fontSize = 12.sp, fontWeight = FontWeight.Medium)
            Text("$count ($percentText)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = color)
        }
        LinearProgressIndicator(
            progress = { percent },
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp)
                .clip(RoundedCornerShape(4.dp)),
            color = color,
            trackColor = MaterialTheme.colorScheme.surfaceVariant
        )
    }
}
