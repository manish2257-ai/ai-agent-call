package com.example.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.CallRecord
import com.example.data.model.CallStatus
import com.example.data.model.SmsAlertLog
import com.example.data.model.UrgencyLevel
import com.example.ui.theme.*

@Composable
fun UrgencyBadge(urgency: UrgencyLevel, modifier: Modifier = Modifier) {
    val (color, bgColor, label) = when (urgency) {
        UrgencyLevel.LOW -> Triple(UrgencyLow, UrgencyLowBg, "LOW")
        UrgencyLevel.MEDIUM -> Triple(UrgencyMedium, UrgencyMediumBg, "MEDIUM")
        UrgencyLevel.HIGH -> Triple(UrgencyHigh, UrgencyHighBg, "HIGH")
        UrgencyLevel.CRITICAL -> Triple(UrgencyCritical, UrgencyCriticalBg, "CRITICAL")
    }

    Surface(
        modifier = modifier.clip(RoundedCornerShape(8.dp)),
        color = bgColor,
        contentColor = color
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Box(
                modifier = Modifier
                    .size(6.dp)
                    .clip(CircleShape)
                    .background(color)
            )
            Text(
                text = label,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                color = color
            )
        }
    }
}

@Composable
fun StatusPill(status: CallStatus, modifier: Modifier = Modifier) {
    val (color, label) = when (status) {
        CallStatus.COMPLETED -> Pair(Color(0xFF10B981), status.label)
        CallStatus.ESCALATED -> Pair(Color(0xFFF97316), status.label)
        CallStatus.TRANSFERRED -> Pair(Color(0xFF3B82F6), status.label)
        CallStatus.FAILED -> Pair(Color(0xFFEF4444), status.label)
        CallStatus.MISSED -> Pair(Color(0xFF9CA3AF), status.label)
        CallStatus.SPAM -> Pair(Color(0xFF6B7280), status.label)
    }

    Surface(
        modifier = modifier.clip(RoundedCornerShape(6.dp)),
        color = color.copy(alpha = 0.15f),
        contentColor = color
    ) {
        Text(
            text = label,
            fontSize = 11.sp,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(horizontal = 7.dp, vertical = 3.dp),
            color = color
        )
    }
}

@Composable
fun StatCard(
    title: String,
    value: String,
    subtitle: String? = null,
    icon: ImageVector,
    accentColor: Color,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.65f)
        ),
        shape = RoundedCornerShape(16.dp),
        border = CardDefaults.outlinedCardBorder().copy(
            brush = androidx.compose.ui.graphics.SolidColor(MaterialTheme.colorScheme.outline.copy(alpha = 0.4f))
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(14.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = title,
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontWeight = FontWeight.Medium
                )
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .clip(CircleShape)
                        .background(accentColor.copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = icon,
                        contentDescription = null,
                        tint = accentColor,
                        modifier = Modifier.size(18.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = value,
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface
            )
            if (subtitle != null) {
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = subtitle,
                    fontSize = 11.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
fun CallItemRow(
    call: CallRecord,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clickable { onClick() },
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        border = CardDefaults.outlinedCardBorder().copy(
            brush = androidx.compose.ui.graphics.SolidColor(
                if (call.urgency == UrgencyLevel.HIGH || call.urgency == UrgencyLevel.CRITICAL) {
                    UrgencyHigh.copy(alpha = 0.4f)
                } else {
                    MaterialTheme.colorScheme.outline.copy(alpha = 0.25f)
                }
            )
        )
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .size(38.dp)
                            .clip(CircleShape)
                            .background(
                                if (call.status == CallStatus.SPAM) Color(0xFF4B5563)
                                else MaterialTheme.colorScheme.primary.copy(alpha = 0.18f)
                            ),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(
                            imageVector = when (call.status) {
                                CallStatus.ESCALATED -> Icons.Default.PriorityHigh
                                CallStatus.TRANSFERRED -> Icons.Default.PhoneForwarded
                                CallStatus.SPAM -> Icons.Default.Block
                                else -> Icons.Default.PhoneCallback
                            },
                            contentDescription = null,
                            tint = when (call.status) {
                                CallStatus.ESCALATED -> UrgencyHigh
                                CallStatus.SPAM -> Color.LightGray
                                else -> MaterialTheme.colorScheme.primary
                            },
                            modifier = Modifier.size(20.dp)
                        )
                    }

                    Column {
                        Text(
                            text = call.callerName,
                            fontWeight = FontWeight.Bold,
                            fontSize = 15.sp,
                            color = MaterialTheme.colorScheme.onSurface
                        )
                        Text(
                            text = "${call.callerNumber} • ${call.timestampFormatted}",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }

                UrgencyBadge(urgency = call.urgency)
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = call.reason,
                fontSize = 13.sp,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = call.summary,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis,
                lineHeight = 16.sp
            )

            Spacer(modifier = Modifier.height(10.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                StatusPill(status = call.status)

                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "${call.durationSeconds}s duration",
                        fontSize = 11.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    if (call.isAlertSent) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            Icon(
                                imageVector = Icons.Default.Sms,
                                contentDescription = null,
                                tint = UrgencyHigh,
                                modifier = Modifier.size(13.dp)
                            )
                            Text(
                                text = "SMS Alerted",
                                fontSize = 11.sp,
                                fontWeight = FontWeight.SemiBold,
                                color = UrgencyHigh
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun SimulatedSmsBanner(
    alert: SmsAlertLog,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp)),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF1E1B4B)
        ),
        border = CardDefaults.outlinedCardBorder().copy(
            brush = androidx.compose.ui.graphics.SolidColor(UrgencyHigh)
        )
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
                    Icon(
                        imageVector = Icons.Default.SmsFailed,
                        contentDescription = null,
                        tint = UrgencyHigh,
                        modifier = Modifier.size(20.dp)
                    )
                    Text(
                        text = "SIMULATED SMS ALERT DISPATCHED",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Black,
                        color = UrgencyHigh
                    )
                }

                IconButton(
                    onClick = onDismiss,
                    modifier = Modifier.size(24.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Close,
                        contentDescription = "Dismiss",
                        tint = Color.White,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(8.dp)),
                color = Color(0xFF0F172A)
            ) {
                Text(
                    text = alert.formattedMessage,
                    fontSize = 12.sp,
                    color = Color(0xFFE2E8F0),
                    fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                    modifier = Modifier.padding(12.dp)
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Delivered to owner via ${alert.provider} at ${alert.timestamp}",
                    fontSize = 11.sp,
                    color = Color.LightGray
                )
                TextButton(
                    onClick = onDismiss,
                    contentPadding = PaddingValues(0.dp)
                ) {
                    Text("OK", color = PrimaryCyan, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
fun SectionHeader(
    title: String,
    subtitle: String? = null,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier.fillMaxWidth()) {
        Text(
            text = title,
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface
        )
        if (subtitle != null) {
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = subtitle,
                fontSize = 13.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
