import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/call_agent_provider.dart';
import 'call_history_screen.dart';
import 'call_details_screen.dart';
import 'urgent_alerts_screen.dart';
import 'settings_screen.dart';
import 'setup_integrations_screen.dart';
import 'privacy_retention_screen.dart';
import 'help_screen.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CallAgentProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI CALL AGENT', style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.2)),
        actions: [
          IconButton(
            icon: const Icon(Icons.shield_outlined),
            tooltip: 'Privacy & Retention',
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PrivacyRetentionScreen())),
          ),
          IconButton(
            icon: const Icon(Icons.help_outline),
            tooltip: 'Help',
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const HelpScreen())),
          ),
        ],
      ),
      drawer: _buildDrawer(context),
      body: RefreshIndicator(
        onRefresh: () => provider.loadInitialData(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Online / Offline Status Banner
              _buildAgentStatusCard(context, provider),
              const SizedBox(height: 16),

              // Metrics Row: Calls Today & Urgent Calls
              Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      context,
                      title: 'Calls Today',
                      value: '${provider.calls.length}',
                      icon: Icons.phone_callback_rounded,
                      color: const Color(0xFF00E5FF),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricCard(
                      context,
                      title: 'Urgent Calls',
                      value: '${provider.calls.where((c) => c.urgency == "HIGH" || c.urgency == "CRITICAL").length}',
                      icon: Icons.notification_important_rounded,
                      color: const Color(0xFFF97316),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Subsystem Connection Health
              _buildConnectionHealthCard(context, provider),
              const SizedBox(height: 16),

              // Latest Call Section
              _buildLatestCallCard(context, provider),
              const SizedBox(height: 20),

              // Interactive Testing & Demo Engine
              _buildDemoActionsCard(context, provider),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAgentStatusCard(BuildContext context, CallAgentProvider provider) {
    final isOnline = provider.isOnline;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 14,
              height: 14,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isOnline ? Colors.greenAccent : Colors.redAccent,
                boxShadow: [
                  BoxShadow(
                    color: (isOnline ? Colors.greenAccent : Colors.redAccent).withOpacity(0.5),
                    blurRadius: 8,
                    spreadRadius: 2,
                  )
                ],
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isOnline ? 'AI RECEPTIONIST ONLINE' : 'AI RECEPTIONIST OFFLINE',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  Text(
                    isOnline ? 'Answering incoming calls via Exotel' : 'Calls will ring directly to owner',
                    style: TextStyle(color: Colors.grey.shade400, fontSize: 13),
                  ),
                ],
              ),
            ),
            Switch(
              value: isOnline,
              activeColor: const Color(0xFF00E5FF),
              onChanged: (val) => provider.toggleAgentOnline(val),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricCard(BuildContext context, {required String title, required String value, required IconData icon, required Color color}) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 12),
            Text(value, style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(title, style: TextStyle(color: Colors.grey.shade400, fontSize: 13)),
          ],
        ),
      ),
    );
  }

  Widget _buildConnectionHealthCard(BuildContext context, CallAgentProvider provider) {
    final status = provider.connectionStatus;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Subsystem Integrations', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildHealthBadge('Firebase', status['firebase'] ?? 'CONNECTED'),
                _buildHealthBadge('OpenAI', status['openAI'] ?? 'CONNECTED'),
                _buildHealthBadge('Exotel', status['exotel'] ?? 'CONNECTED'),
                _buildHealthBadge('SMS', status['sms'] ?? 'CONNECTED'),
                _buildHealthBadge('WhatsApp', status['whatsapp'] ?? 'CONNECTED'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthBadge(String name, String state) {
    final isOk = state == 'CONNECTED';
    return Column(
      children: [
        Icon(isOk ? Icons.check_circle_rounded : Icons.sensors_rounded, size: 20, color: isOk ? Colors.greenAccent : const Color(0xFF00E5FF)),
        const SizedBox(height: 4),
        Text(name, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
        Text(state, style: TextStyle(fontSize: 10, color: Colors.grey.shade400)),
      ],
    );
  }

  Widget _buildLatestCallCard(BuildContext context, CallAgentProvider provider) {
    if (provider.calls.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(20),
          child: Center(child: Text('No calls recorded yet.')),
        ),
      );
    }
    final latest = provider.calls.first;
    final isUrgent = latest.urgency == 'HIGH' || latest.urgency == 'CRITICAL';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Latest Call', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: (isUrgent ? const Color(0xFFF97316) : Colors.blueGrey).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    latest.urgency,
                    style: TextStyle(
                      color: isUrgent ? const Color(0xFFF97316) : Colors.blueGrey.shade200,
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                    ),
                  ),
                )
              ],
            ),
            const SizedBox(height: 12),
            Text(latest.callerName, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Text(latest.callerNumber, style: TextStyle(color: Colors.grey.shade400, fontSize: 13)),
            const SizedBox(height: 8),
            Text(
              latest.reason,
              style: const TextStyle(fontStyle: FontStyle.italic),
            ),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                onPressed: () {
                  Navigator.push(context, MaterialPageRoute(builder: (_) => CallDetailsScreen(call: latest)));
                },
                icon: const Icon(Icons.arrow_forward_rounded, size: 16),
                label: const Text('View Call Details'),
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildDemoActionsCard(BuildContext context, CallAgentProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Demo & Test Control', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 4),
            Text('Simulate inbound calls and test alerts without live telephony charges:', style: TextStyle(color: Colors.grey.shade400, fontSize: 12)),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ActionChip(
                  avatar: const Icon(Icons.call, size: 16),
                  label: const Text('Test Normal Call'),
                  onPressed: () {
                    provider.simulateCallScenario('enquiry');
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Simulated Normal Call (Priya - Advisory Enquiry)')));
                  },
                ),
                ActionChip(
                  avatar: const Icon(Icons.warning_amber_rounded, size: 16, color: Color(0xFFF97316)),
                  label: const Text('Test Urgent Call'),
                  onPressed: () {
                    provider.simulateCallScenario('outage');
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Simulated Urgent Call (Rahul - Website Outage) -> SMS Dispatched!')));
                  },
                ),
                ActionChip(
                  avatar: const Icon(Icons.sms_outlined, size: 16),
                  label: const Text('Test SMS Alert'),
                  onPressed: () {
                    provider.sendTestSms();
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Sent Test SMS to owner phone via Exotel gateway.')));
                  },
                ),
                ActionChip(
                  avatar: const Icon(Icons.chat_bubble_outline_rounded, size: 16, color: Color(0xFF25D366)),
                  label: const Text('Test WhatsApp Alert'),
                  onPressed: () async {
                    final res = await provider.sendTestWhatsApp();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          backgroundColor: res['success'] == true ? Colors.green[800] : Colors.red[800],
                          content: Text(res['message'] ?? 'Test WhatsApp alert dispatched!'),
                        ),
                      );
                    }
                  },
                ),
                ActionChip(
                  avatar: const Icon(Icons.notifications_active_outlined, size: 16),
                  label: const Text('Test Push Notification'),
                  onPressed: () {
                    provider.sendTestPush();
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Sent FCM Test Push Notification.')));
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          DrawerHeader(
            decoration: const BoxDecoration(color: Color(0xFF0F172A)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const Icon(Icons.support_agent_rounded, size: 48, color: Color(0xFF00E5FF)),
                const SizedBox(height: 12),
                const Text('AI Personal Call Agent', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.white)),
                Text('Owner: Manish Kumar', style: TextStyle(color: Colors.grey.shade400, fontSize: 13)),
              ],
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard_rounded),
            title: const Text('Dashboard'),
            onTap: () => Navigator.pop(context),
          ),
          ListTile(
            leading: const Icon(Icons.call_rounded),
            title: const Text('Call History'),
            onTap: () {
              Navigator.pop(context);
              Navigator.push(context, MaterialPageRoute(builder: (_) => const CallHistoryScreen()));
            },
          ),
          ListTile(
            leading: const Icon(Icons.notification_important_rounded),
            title: const Text('Urgent Alerts'),
            onTap: () {
              Navigator.pop(context);
              Navigator.push(context, MaterialPageRoute(builder: (_) => const UrgentAlertsScreen()));
            },
          ),
          ListTile(
            leading: const Icon(Icons.settings_rounded),
            title: const Text('Agent Settings'),
            onTap: () {
              Navigator.pop(context);
              Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen()));
            },
          ),
          ListTile(
            leading: const Icon(Icons.cloud_sync_rounded),
            title: const Text('Setup & Integrations'),
            onTap: () {
              Navigator.pop(context);
              Navigator.push(context, MaterialPageRoute(builder: (_) => const SetupIntegrationsScreen()));
            },
          ),
          ListTile(
            leading: const Icon(Icons.security_rounded),
            title: const Text('Privacy & Retention'),
            onTap: () {
              Navigator.pop(context);
              Navigator.push(context, MaterialPageRoute(builder: (_) => const PrivacyRetentionScreen()));
            },
          ),
          ListTile(
            leading: const Icon(Icons.help_outline_rounded),
            title: const Text('Help & Documentation'),
            onTap: () {
              Navigator.pop(context);
              Navigator.push(context, MaterialPageRoute(builder: (_) => const HelpScreen()));
            },
          ),
        ],
      ),
    );
  }
}
