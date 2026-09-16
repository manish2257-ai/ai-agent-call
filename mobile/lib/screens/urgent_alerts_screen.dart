import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/call_agent_provider.dart';
import '../models/urgent_alert.dart';

class UrgentAlertsScreen extends StatelessWidget {
  const UrgentAlertsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CallAgentProvider>(context);
    final alerts = provider.alerts;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Urgent Alerts'),
        actions: [
          IconButton(
            icon: const Icon(Icons.chat_bubble_outline_rounded, color: Color(0xFF25D366)),
            tooltip: 'Send Test WhatsApp',
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
          IconButton(
            icon: const Icon(Icons.send_to_mobile_rounded),
            tooltip: 'Send Test SMS',
            onPressed: () {
              provider.sendTestSms();
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Test urgent SMS sent to owner phone!')));
            },
          )
        ],
      ),
      body: alerts.isEmpty
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.notifications_off_outlined, size: 64, color: Colors.grey),
                  SizedBox(height: 16),
                  Text('No urgent escalations recorded yet.'),
                  SizedBox(height: 8),
                  Text('High and Critical calls will automatically trigger SMS here.', style: TextStyle(color: Colors.grey, fontSize: 13)),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: alerts.length,
              itemBuilder: (context, idx) {
                final alert = alerts[idx];
                return _buildAlertCard(context, alert, provider);
              },
            ),
    );
  }

  Widget _buildAlertCard(BuildContext context, UrgentAlert alert, CallAgentProvider provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.warning_amber_rounded, color: Color(0xFFF97316)),
                    const SizedBox(width: 8),
                    Text(alert.urgency, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFF97316))),
                  ],
                ),
                Text(alert.createdAt, style: TextStyle(color: Colors.grey.shade400, fontSize: 12)),
              ],
            ),
            const SizedBox(height: 12),
            Text(alert.callerName, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
            Text(alert.callerNumber, style: TextStyle(color: Colors.grey.shade400, fontSize: 13)),
            const SizedBox(height: 10),
            Text(alert.reason, style: const TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 6),
            Text(alert.summary, style: TextStyle(color: Colors.grey.shade300, fontSize: 14)),
            const Divider(height: 24),
            // Channel Delivery Status
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: [
                _buildChannelBadge('SMS', alert.smsStatus),
                _buildChannelBadge('WhatsApp', alert.whatsappStatus),
                _buildChannelBadge('FCM Push', alert.fcmStatus),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    visualDensity: VisualDensity.compact,
                    foregroundColor: const Color(0xFF25D366),
                    side: const BorderSide(color: Color(0xFF25D366)),
                  ),
                  icon: const Icon(Icons.refresh_rounded, size: 14),
                  label: const Text('Retry WhatsApp', style: TextStyle(fontSize: 12)),
                  onPressed: () async {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Retrying WhatsApp notification...'), duration: Duration(seconds: 1)),
                    );
                    final res = await provider.retryWhatsAppAlert(alert.alertId);
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          backgroundColor: res['success'] == true ? Colors.green[800] : Colors.red[800],
                          content: Text(res['message'] ?? (res['success'] == true ? 'WhatsApp alert resent successfully!' : 'WhatsApp retry failed.')),
                        ),
                      );
                    }
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline, size: 20),
                  tooltip: 'Delete Alert',
                  onPressed: () {
                    provider.deleteAlert(alert.alertId);
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Alert removed.')));
                  },
                )
              ],
            )
          ],
        ),
      ),
    );
  }

  Widget _buildChannelBadge(String channel, String status) {
    final bool isSent = status.toUpperCase() == 'SENT' || status.toUpperCase() == 'DELIVERED';
    final Color color = isSent ? Colors.greenAccent : (status == 'NOT_CONFIGURED' ? Colors.grey : Colors.redAccent);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isSent ? Icons.check_circle_rounded : (status == 'NOT_CONFIGURED' ? Icons.info_outline : Icons.cancel_rounded),
            size: 13,
            color: color,
          ),
          const SizedBox(width: 4),
          Text(
            '$channel: $status',
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color),
          ),
        ],
      ),
    );
  }
}
