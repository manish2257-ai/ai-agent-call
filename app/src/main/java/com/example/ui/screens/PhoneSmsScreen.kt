package com.example.ui.screens

import androidx.compose.foundation.background
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
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.AppConfigState
import com.example.model.ExotelStatus

@Composable
fun PhoneSmsScreen(
    config: AppConfigState,
    exotel: ExotelStatus,
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
        // Section 1: Telephony Provider Card
        Text(
            text = "Telephony Infrastructure",
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp,
            color = MaterialTheme.colorScheme.primary
        )

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("telephony_card"),
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
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.PhoneInTalk,
                            contentDescription = null,
                            tint = Color(0xFF00E5FF),
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(
                            text = config.telephonyProvider,
                            fontWeight = FontWeight.Bold,
                            fontSize = 16.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                    }
                    Surface(
                        color = Color(0xFF10B981).copy(alpha = 0.2f),
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        Text(
                            text = exotel.status,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF10B981)
                        )
                    }
                }

                Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))

                // Virtual Number
                UrlOrConfigRow(
                    label = "Virtual Phone Number",
                    value = if (exotel.virtualNumber != "Not configured") exotel.virtualNumber else config.virtualNumber
                )

                // Webhook incoming
                UrlOrConfigRow(
                    label = "Incoming Call Webhook URL",
                    value = config.incomingWebhookUrl,
                    isMonospace = true
                )

                // Voicebot WSS
                UrlOrConfigRow(
                    label = "Voicebot WebSocket (WSS) URL",
                    value = config.voicebotWssUrl,
                    isMonospace = true
                )

                // Status callback
                UrlOrConfigRow(
                    label = "Status Callback URL",
                    value = config.statusCallbackUrl,
                    isMonospace = true
                )
            }
        }

        // Section 2: SMS Gateway Card
        Text(
            text = "SMS Gateway",
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp,
            color = MaterialTheme.colorScheme.primary
        )

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("sms_gateway_card"),
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
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Message,
                            contentDescription = null,
                            tint = Color(0xFF10B981),
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(modifier = Modifier.width(10.dp))
                        Text(
                            text = config.smsProvider,
                            fontWeight = FontWeight.Bold,
                            fontSize = 16.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                    }
                    Surface(
                        color = Color(0xFF10B981).copy(alpha = 0.2f),
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        Text(
                            text = config.smsStatus,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF10B981)
                        )
                    }
                }

                Divider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.3f))

                UrlOrConfigRow(
                    label = "Owner Alert Destination",
                    value = config.ownerPhoneNumber
                )

                UrlOrConfigRow(
                    label = "Urgent Escalation Cooldown",
                    value = "5 minutes (prevents alert spam)"
                )
            }
        }

        // Section 3: Call Forwarding Guidance Card
        Text(
            text = "Carrier Call Forwarding",
            fontWeight = FontWeight.Bold,
            fontSize = 18.sp,
            color = MaterialTheme.colorScheme.primary
        )

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .testTag("call_forwarding_card"),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Text(
                    text = "Forward unanswered/busy calls to your virtual number:",
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                val vn = if (config.virtualNumber != "Not configured") config.virtualNumber else "<VirtualNumber>"

                ForwardingDialCode(
                    carrier = "Indian Carriers (Jio / Airtel / Vi)",
                    code = "*67*$vn#"
                )

                ForwardingDialCode(
                    carrier = "US Carriers (AT&T / Verizon / T-Mobile)",
                    code = "*71$vn"
                )

                ForwardingDialCode(
                    carrier = "Deactivate All Forwarding",
                    code = "##002#"
                )
            }
        }
    }
}

@Composable
fun UrlOrConfigRow(
    label: String,
    value: String,
    isMonospace: Boolean = false
) {
    Column {
        Text(
            text = label,
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(3.dp))
        if (isMonospace && value != "Not configured" && value != "Unavailable") {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(
                        color = MaterialTheme.colorScheme.background,
                        shape = RoundedCornerShape(6.dp)
                    )
                    .padding(8.dp)
            ) {
                Text(
                    text = value,
                    fontFamily = FontFamily.Monospace,
                    fontSize = 11.sp,
                    color = Color(0xFF00E5FF),
                    lineHeight = 15.sp
                )
            }
        } else {
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
fun ForwardingDialCode(
    carrier: String,
    code: String
) {
    Column {
        Text(
            text = carrier,
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(2.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    color = MaterialTheme.colorScheme.background,
                    shape = RoundedCornerShape(6.dp)
                )
                .padding(8.dp)
        ) {
            Text(
                text = code,
                fontFamily = FontFamily.Monospace,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF67E8F9)
            )
        }
    }
}
