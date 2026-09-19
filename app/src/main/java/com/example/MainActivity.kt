package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.AppViewModel
import com.example.ui.screens.*
import com.example.ui.theme.AICallAgentTheme

sealed class ScreenTab(val title: String, val icon: ImageVector, val tag: String) {
    object Dashboard : ScreenTab("Dashboard", Icons.Default.Dashboard, "tab_dashboard")
    object Calls : ScreenTab("Calls", Icons.Default.Call, "tab_calls")
    object AiRules : ScreenTab("AI & Rules", Icons.Default.SmartToy, "tab_ai_rules")
    object PhoneSms : ScreenTab("Phone & SMS", Icons.Default.PhoneInTalk, "tab_phone_sms")
    object More : ScreenTab("More", Icons.Default.MoreHoriz, "tab_more")
}

class MainActivity : ComponentActivity() {

    private val viewModel: AppViewModel by viewModels()

    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            AICallAgentTheme {
                val configState by viewModel.configState.collectAsState()
                val exotelStatus by viewModel.exotelStatus.collectAsState()
                val calls by viewModel.calls.collectAsState()
                val selectedTab by viewModel.selectedTab.collectAsState()

                val tabs = listOf(
                    ScreenTab.Dashboard,
                    ScreenTab.Calls,
                    ScreenTab.AiRules,
                    ScreenTab.PhoneSms,
                    ScreenTab.More
                )

                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    topBar = {
                        TopAppBar(
                            title = {
                                Column {
                                    Text(
                                        text = "AI CALL AGENT",
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 18.sp,
                                        letterSpacing = 1.sp,
                                        color = MaterialTheme.colorScheme.onSurface
                                    )
                                    Text(
                                        text = if (configState.agentEnabled) "Exotel Telephony Active" else "Agent Offline",
                                        fontSize = 11.sp,
                                        color = if (configState.agentEnabled) Color(0xFF10B981) else MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            },
                            actions = {
                                IconButton(
                                    onClick = { viewModel.loadData() },
                                    modifier = Modifier.testTag("top_bar_refresh")
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.Refresh,
                                        contentDescription = "Refresh live configuration",
                                        tint = MaterialTheme.colorScheme.primary
                                    )
                                }
                            },
                            colors = TopAppBarDefaults.topAppBarColors(
                                containerColor = MaterialTheme.colorScheme.surface
                            )
                        )
                    },
                    bottomBar = {
                        NavigationBar(
                            containerColor = MaterialTheme.colorScheme.surface,
                            modifier = Modifier.testTag("bottom_navigation_bar")
                        ) {
                            tabs.forEachIndexed { index, tab ->
                                NavigationBarItem(
                                    icon = {
                                        Icon(
                                            imageVector = tab.icon,
                                            contentDescription = tab.title
                                        )
                                    },
                                    label = {
                                        Text(
                                            text = tab.title,
                                            fontSize = 10.sp,
                                            fontWeight = if (selectedTab == index) FontWeight.Bold else FontWeight.Normal
                                        )
                                    },
                                    selected = selectedTab == index,
                                    onClick = { viewModel.selectTab(index) },
                                    modifier = Modifier.testTag(tab.tag),
                                    colors = NavigationBarItemDefaults.colors(
                                        selectedIconColor = MaterialTheme.colorScheme.primary,
                                        selectedTextColor = MaterialTheme.colorScheme.primary,
                                        indicatorColor = MaterialTheme.colorScheme.primaryContainer
                                    )
                                )
                            }
                        }
                    }
                ) { innerPadding ->
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(innerPadding)
                    ) {
                        when (selectedTab) {
                            0 -> DashboardScreen(
                                config = configState,
                                exotel = exotelStatus,
                                calls = calls,
                                onToggleOnline = { viewModel.toggleAgentOnline(it) },
                                onNavigateToCalls = { viewModel.selectTab(1) }
                            )
                            1 -> CallsScreen(
                                calls = calls,
                                onRefresh = { viewModel.loadData() }
                            )
                            2 -> AiRulesScreen(
                                config = configState,
                                onToggleAgent = { viewModel.toggleAgentOnline(it) }
                            )
                            3 -> PhoneSmsScreen(
                                config = configState,
                                exotel = exotelStatus
                            )
                            4 -> MoreScreen(
                                config = configState,
                                exotel = exotelStatus,
                                onRefresh = { viewModel.loadData() }
                            )
                        }
                    }
                }
            }
        }
    }
}
