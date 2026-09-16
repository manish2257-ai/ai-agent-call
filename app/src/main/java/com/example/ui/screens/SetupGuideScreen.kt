package com.example.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
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
fun SetupGuideScreen(
    modifier: Modifier = Modifier
) {
    val clipboard = LocalClipboardManager.current
    val settings by CallAgentRepository.settings.collectAsState()

    var copiedNotice by remember { mutableStateOf<String?>(null) }

    val steps = remember {
        mutableStateListOf(
            Pair("Step 1: Account Creation", true),
            Pair("Step 2: Enter Alert Phone Number", true),
            Pair("Step 3: Configure AI Voice Provider (OpenAI)", true),
            Pair("Step 4: Configure Telephony Provider (Twilio/Exotel)", true),
            Pair("Step 5: Configure SMS Gateway Credentials", true),
            Pair("Step 6: Assign AI Virtual Phone Number", true),
            Pair("Step 7: Configure Voice & Status Webhooks", true),
            Pair("Step 8: Set AI Greeting & Disclaimer", true),
            Pair("Step 9: Configure Urgency Rules & Minimum Threshold", true),
            Pair("Step 10: Populate VIP Contacts & Knowledge FAQs", true),
            Pair("Step 11: Run Test Call Simulation (Outage Scenario)", true),
            Pair("Step 12: Verify Urgent SMS Notification Delivery", true),
            Pair("Step 13: Enable AI Agent & Set Up Carrier Forwarding", true)
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
                title = "13-Step Setup & Verification Guide",
                subtitle = "Complete setup checklist and cellular carrier USSD forwarding codes"
            )
        }

        // Checklist Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Implementation Checklist", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    steps.forEachIndexed { index, (label, checked) ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Checkbox(
                                checked = checked,
                                onCheckedChange = { isChecked ->
                                    steps[index] = Pair(label, isChecked)
                                }
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(label, fontSize = 12.sp, fontWeight = if (checked) FontWeight.SemiBold else FontWeight.Normal)
                        }
                    }
                }
            }
        }

        // Carrier USSD Codes Card
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Icon(Icons.Default.Dialpad, contentDescription = null, tint = PrimaryCyan)
                        Text("Carrier Call Forwarding Dial Codes", fontWeight = FontWeight.Bold, fontSize = 14.sp)
                    }

                    Text(
                        "Dial these USSD codes on your cellular dialer to route unanswered or busy calls to ${settings.aiPhoneNumber}:",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    val ussdCodes = listOf(
                        Triple("Jio (India)", "*404*${settings.aiPhoneNumber}#", "Forward when unanswered"),
                        Triple("Airtel (India)", "*61*${settings.aiPhoneNumber}#", "Forward when unanswered"),
                        Triple("Vodafone Idea", "*61*${settings.aiPhoneNumber}#", "Forward when unanswered"),
                        Triple("AT&T / T-Mobile (USA)", "**004*${settings.aiPhoneNumber}#", "Conditional call forwarding"),
                        Triple("Verizon (USA)", "*71${settings.aiPhoneNumber}", "Conditional call forwarding"),
                        Triple("Cancel All Forwarding", "##002#", "Revert to standard mobile line")
                    )

                    ussdCodes.forEach { (carrier, code, desc) ->
                        Surface(
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(8.dp),
                            color = MaterialTheme.colorScheme.surface
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(10.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Column {
                                    Text(carrier, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                                    Text(code, fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace, fontSize = 12.sp, color = PrimaryCyan)
                                    Text(desc, fontSize = 10.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                }
                                IconButton(
                                    onClick = {
                                        clipboard.setText(AnnotatedString(code))
                                        copiedNotice = "Copied code: $code"
                                    }
                                ) {
                                    Icon(Icons.Default.ContentCopy, contentDescription = "Copy code", modifier = Modifier.size(18.dp))
                                }
                            }
                        }
                    }

                    if (copiedNotice != null) {
                        Text(copiedNotice!!, color = PrimaryCyan, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                    }
                }
            }
        }
    }
}
