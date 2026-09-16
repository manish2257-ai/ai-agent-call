package com.example.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.CallRecord
import com.example.data.repository.CallAgentRepository
import com.example.ui.theme.PrimaryCyan
import com.example.ui.theme.UrgencyLow

enum class MainTab(val title: String, val icon: ImageVector) {
    DASHBOARD("Dashboard", Icons.Default.Dashboard),
    CALLS("Calls", Icons.Default.Call),
    AI_CONFIG("AI & Rules", Icons.Default.Psychology),
    PHONE_SMS("Phone & SMS", Icons.Default.SettingsPhone),
    MORE("More", Icons.Default.MoreHoriz)
}

enum class SubScreen {
    NONE,
    CALL_DETAILS,
    AI_PERSONALITY,
    VIP_CONTACTS,
    KNOWLEDGE_BASE,
    ANALYTICS,
    INTEGRATION_STATUS,
    PRIVACY_ACCOUNT,
    SETUP_GUIDE
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
    onSignOut: () -> Unit = {}
) {
    var selectedTab by remember { mutableStateOf(MainTab.DASHBOARD) }
    var currentSubScreen by remember { mutableStateOf(SubScreen.NONE) }
    var activeCallDetail by remember { mutableStateOf<CallRecord?>(null) }

    val settings by CallAgentRepository.settings.collectAsState()

    Scaffold(
        topBar = {
            if (currentSubScreen == SubScreen.NONE) {
                TopAppBar(
                    title = {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text("AI Call Agent", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                            Surface(
                                shape = CircleShape,
                                color = if (settings.isAgentEnabled) UrgencyLow.copy(alpha = 0.2f) else Color.Gray.copy(alpha = 0.2f)
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(6.dp)
                                            .clip(CircleShape)
                                            .background(if (settings.isAgentEnabled) UrgencyLow else Color.Gray)
                                    )
                                    Text(
                                        text = if (settings.isAgentEnabled) "ACTIVE" else "OFF",
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (settings.isAgentEnabled) UrgencyLow else Color.Gray
                                    )
                                }
                            }
                        }
                    },
                    actions = {
                        IconButton(
                            onClick = {
                                val call = CallAgentRepository.simulateCallScenario("outage")
                                activeCallDetail = call
                                currentSubScreen = SubScreen.CALL_DETAILS
                            },
                            modifier = Modifier.testTag("action_simulate_call")
                        ) {
                            Icon(
                                imageVector = Icons.Default.Bolt,
                                contentDescription = "Simulate Urgent Call",
                                tint = PrimaryCyan
                            )
                        }
                    }
                )
            }
        },
        bottomBar = {
            if (currentSubScreen == SubScreen.NONE) {
                NavigationBar(
                    containerColor = MaterialTheme.colorScheme.surface,
                    tonalElevation = 8.dp
                ) {
                    MainTab.values().forEach { tab ->
                        NavigationBarItem(
                            selected = selectedTab == tab,
                            onClick = { selectedTab = tab },
                            icon = { Icon(tab.icon, contentDescription = tab.title) },
                            label = { Text(tab.title, fontSize = 11.sp) },
                            modifier = Modifier.testTag("nav_tab_${tab.name.lowercase()}")
                        )
                    }
                }
            }
        }
    ) { innerPadding ->
        Box(modifier = Modifier.padding(innerPadding)) {
            when (currentSubScreen) {
                SubScreen.CALL_DETAILS -> {
                    activeCallDetail?.let { call ->
                        CallDetailsScreen(
                            call = call,
                            onBack = {
                                currentSubScreen = SubScreen.NONE
                                activeCallDetail = null
                            }
                        )
                    }
                }
                SubScreen.AI_PERSONALITY -> {
                    AIPersonalityScreen(
                        onBack = { currentSubScreen = SubScreen.NONE }
                    )
                }
                SubScreen.VIP_CONTACTS -> {
                    Scaffold(
                        topBar = {
                            TopAppBar(
                                title = { Text("VIP Contacts", fontWeight = FontWeight.Bold) },
                                navigationIcon = {
                                    IconButton(onClick = { currentSubScreen = SubScreen.NONE }) {
                                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                                    }
                                }
                            )
                        }
                    ) { p ->
                        ContactsScreen(modifier = Modifier.padding(p))
                    }
                }
                SubScreen.KNOWLEDGE_BASE -> {
                    Scaffold(
                        topBar = {
                            TopAppBar(
                                title = { Text("Knowledge Base", fontWeight = FontWeight.Bold) },
                                navigationIcon = {
                                    IconButton(onClick = { currentSubScreen = SubScreen.NONE }) {
                                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                                    }
                                }
                            )
                        }
                    ) { p ->
                        KnowledgeBaseScreen(modifier = Modifier.padding(p))
                    }
                }
                SubScreen.ANALYTICS -> {
                    Scaffold(
                        topBar = {
                            TopAppBar(
                                title = { Text("Call Analytics", fontWeight = FontWeight.Bold) },
                                navigationIcon = {
                                    IconButton(onClick = { currentSubScreen = SubScreen.NONE }) {
                                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                                    }
                                }
                            )
                        }
                    ) { p ->
                        AnalyticsScreen(modifier = Modifier.padding(p))
                    }
                }
                SubScreen.INTEGRATION_STATUS -> {
                    Scaffold(
                        topBar = {
                            TopAppBar(
                                title = { Text("Gateway Health", fontWeight = FontWeight.Bold) },
                                navigationIcon = {
                                    IconButton(onClick = { currentSubScreen = SubScreen.NONE }) {
                                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                                    }
                                }
                            )
                        }
                    ) { p ->
                        IntegrationStatusScreen(modifier = Modifier.padding(p))
                    }
                }
                SubScreen.PRIVACY_ACCOUNT -> {
                    Scaffold(
                        topBar = {
                            TopAppBar(
                                title = { Text("Privacy & Account", fontWeight = FontWeight.Bold) },
                                navigationIcon = {
                                    IconButton(onClick = { currentSubScreen = SubScreen.NONE }) {
                                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                                    }
                                }
                            )
                        }
                    ) { p ->
                        PrivacyAccountScreen(
                            onSignOut = onSignOut,
                            modifier = Modifier.padding(p)
                        )
                    }
                }
                SubScreen.SETUP_GUIDE -> {
                    Scaffold(
                        topBar = {
                            TopAppBar(
                                title = { Text("Setup & Forwarding", fontWeight = FontWeight.Bold) },
                                navigationIcon = {
                                    IconButton(onClick = { currentSubScreen = SubScreen.NONE }) {
                                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                                    }
                                }
                            )
                        }
                    ) { p ->
                        SetupGuideScreen(modifier = Modifier.padding(p))
                    }
                }
                SubScreen.NONE -> {
                    when (selectedTab) {
                        MainTab.DASHBOARD -> DashboardScreen(
                            onNavigateToCalls = { selectedTab = MainTab.CALLS },
                            onSelectCall = { call ->
                                activeCallDetail = call
                                currentSubScreen = SubScreen.CALL_DETAILS
                            },
                            onNavigateToSetup = { currentSubScreen = SubScreen.SETUP_GUIDE }
                        )
                        MainTab.CALLS -> CallHistoryScreen(
                            onSelectCall = { call ->
                                activeCallDetail = call
                                currentSubScreen = SubScreen.CALL_DETAILS
                            }
                        )
                        MainTab.AI_CONFIG -> {
                            var subTab by remember { mutableStateOf(0) }
                            Column(modifier = Modifier.fillMaxSize()) {
                                TabRow(selectedTabIndex = subTab) {
                                    Tab(selected = subTab == 0, onClick = { subTab = 0 }, text = { Text("General") })
                                    Tab(selected = subTab == 1, onClick = { subTab = 1 }, text = { Text("Urgency Rules") })
                                }
                                if (subTab == 0) {
                                    AgentSettingsScreen(
                                        onNavigateToPersonality = { currentSubScreen = SubScreen.AI_PERSONALITY }
                                    )
                                } else {
                                    UrgencyRulesScreen()
                                }
                            }
                        }
                        MainTab.PHONE_SMS -> {
                            var subTab by remember { mutableStateOf(0) }
                            Column(modifier = Modifier.fillMaxSize()) {
                                TabRow(selectedTabIndex = subTab) {
                                    Tab(selected = subTab == 0, onClick = { subTab = 0 }, text = { Text("Telephony") })
                                    Tab(selected = subTab == 1, onClick = { subTab = 1 }, text = { Text("SMS Gateway") })
                                }
                                if (subTab == 0) {
                                    TelephonySettingsScreen(
                                        onNavigateToForwardingGuide = { currentSubScreen = SubScreen.SETUP_GUIDE }
                                    )
                                } else {
                                    SmsSettingsScreen()
                                }
                            }
                        }
                        MainTab.MORE -> MoreMenuScreen(
                            onOpenVipContacts = { currentSubScreen = SubScreen.VIP_CONTACTS },
                            onOpenKnowledge = { currentSubScreen = SubScreen.KNOWLEDGE_BASE },
                            onOpenAnalytics = { currentSubScreen = SubScreen.ANALYTICS },
                            onOpenHealth = { currentSubScreen = SubScreen.INTEGRATION_STATUS },
                            onOpenSetup = { currentSubScreen = SubScreen.SETUP_GUIDE },
                            onOpenPrivacy = { currentSubScreen = SubScreen.PRIVACY_ACCOUNT }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun MoreMenuScreen(
    onOpenVipContacts: () -> Unit,
    onOpenKnowledge: () -> Unit,
    onOpenAnalytics: () -> Unit,
    onOpenHealth: () -> Unit,
    onOpenSetup: () -> Unit,
    onOpenPrivacy: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Text("Management & System Tools", fontWeight = FontWeight.Bold, fontSize = 16.sp, modifier = Modifier.padding(bottom = 6.dp))

        val menuItems = listOf(
            Triple("VIP & Known Contacts", "Special priority rules and contact categorization", Icons.Default.Contacts) to onOpenVipContacts,
            Triple("Approved Knowledge Base", "FAQs, office hours, and services facts", Icons.Default.MenuBook) to onOpenKnowledge,
            Triple("Call Analytics & Trends", "Screening statistics, graphs, and distribution", Icons.Default.BarChart) to onOpenAnalytics,
            Triple("Setup & Forwarding Guide", "13-step checklist & carrier dial codes", Icons.Default.Checklist) to onOpenSetup,
            Triple("Gateway & Integration Health", "Live telemetry for AI, carrier, and DB", Icons.Default.HealthAndSafety) to onOpenHealth,
            Triple("Privacy, Security & Account", "Consent terms, data retention, and purge", Icons.Default.Security) to onOpenPrivacy
        )

        menuItems.forEach { (item, action) ->
            val (title, subtitle, icon) = item
            Card(
                modifier = Modifier
                    .fillMaxWidth(),
                onClick = action,
                shape = androidx.compose.foundation.shape.RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(14.dp)
                ) {
                    Icon(icon, contentDescription = null, tint = PrimaryCyan, modifier = Modifier.size(24.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(title, fontWeight = FontWeight.Bold, fontSize = 14.sp)
                        Text(subtitle, fontSize = 12.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Icon(Icons.Default.ChevronRight, contentDescription = null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}
