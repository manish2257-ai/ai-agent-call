import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/call_agent_provider.dart';

class PrivacyRetentionScreen extends StatefulWidget {
  const PrivacyRetentionScreen({super.key});

  @override
  State<PrivacyRetentionScreen> createState() => _PrivacyRetentionScreenState();
}

class _PrivacyRetentionScreenState extends State<PrivacyRetentionScreen> {
  int _callRetention = 90;
  String _transcriptRetention = 'DISABLED';
  String _recordingRetention = 'DISABLED';
  int _alertRetention = 90;

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CallAgentProvider>(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Privacy & Data Retention')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Privacy Dashboard Card
          Card(
            color: const Color(0xFF1E293B),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Privacy Dashboard', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF00E5FF))),
                  const SizedBox(height: 12),
                  _buildDashboardRow('Live AI Processing', 'ON (Transient)', Colors.greenAccent),
                  _buildDashboardRow('Persistent Transcripts', 'OFF (Disabled by default)', Colors.orangeAccent),
                  _buildDashboardRow('Call Audio Recording', 'OFF (Disabled by default)', Colors.orangeAccent),
                  _buildDashboardRow('Call Metadata Retention', '$_callRetention Days', Colors.white),
                  _buildDashboardRow('Urgent Alert Retention', '$_alertRetention Days', Colors.white),
                  _buildDashboardRow('Consent Mode', 'Disable Recording & Transcripts', Colors.white70),
                  const Divider(height: 20),
                  Row(
                    children: const [
                      Icon(Icons.cleaning_services_rounded, size: 16, color: Colors.grey),
                      SizedBox(width: 8),
                      Text('Last automatic cleanup: Today, 04:00 AM UTC', style: TextStyle(color: Colors.grey, fontSize: 12)),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Retention Rules Configuration
          const Text('Retention Limits', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),

          DropdownButtonFormField<int>(
            value: _callRetention,
            decoration: const InputDecoration(
              labelText: 'Call Metadata Retention',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 7, child: Text('7 Days')),
              DropdownMenuItem(value: 30, child: Text('30 Days')),
              DropdownMenuItem(value: 90, child: Text('90 Days (Default MVP)')),
              DropdownMenuItem(value: 180, child: Text('180 Days')),
              DropdownMenuItem(value: 365, child: Text('1 Year')),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _callRetention = val);
            },
          ),
          const SizedBox(height: 16),

          DropdownButtonFormField<String>(
            value: _transcriptRetention,
            decoration: const InputDecoration(
              labelText: 'Persistent Transcript Retention',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'DISABLED', child: Text('Disabled (Never store transcripts - Default)')),
              DropdownMenuItem(value: '7', child: Text('7 Days')),
              DropdownMenuItem(value: '30', child: Text('30 Days')),
              DropdownMenuItem(value: '90', child: Text('90 Days')),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _transcriptRetention = val);
            },
          ),
          const SizedBox(height: 16),

          DropdownButtonFormField<String>(
            value: _recordingRetention,
            decoration: const InputDecoration(
              labelText: 'Audio Recording Retention',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'DISABLED', child: Text('Disabled (Never store audio recordings - Default)')),
              DropdownMenuItem(value: '7', child: Text('7 Days')),
              DropdownMenuItem(value: '30', child: Text('30 Days')),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _recordingRetention = val);
            },
          ),
          const SizedBox(height: 16),

          DropdownButtonFormField<int>(
            value: _alertRetention,
            decoration: const InputDecoration(
              labelText: 'Urgent Alert Retention',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 7, child: Text('7 Days')),
              DropdownMenuItem(value: 30, child: Text('30 Days')),
              DropdownMenuItem(value: 90, child: Text('90 Days (Default)')),
              DropdownMenuItem(value: 180, child: Text('180 Days')),
            ],
            onChanged: (val) {
              if (val != null) setState(() => _alertRetention = val);
            },
          ),
          const SizedBox(height: 24),

          // Data Export & Purge Actions
          const Text('Owner Data Rights', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Export My Data: Generated JSON archive with sanitized call metadata and summaries.')),
              );
            },
            icon: const Icon(Icons.download_rounded),
            label: const Text('Export My Data (JSON)'),
            style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            style: FilledButton.styleFrom(
              backgroundColor: Colors.redAccent.shade700,
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
            onPressed: () => _confirmBulkPurge(context, provider),
            icon: const Icon(Icons.delete_forever_rounded),
            label: const Text('Delete All Stored Call Data'),
          ),
        ],
      ),
    );
  }

  Widget _buildDashboardRow(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 13, color: Colors.grey)),
          Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: color)),
        ],
      ),
    );
  }

  void _confirmBulkPurge(BuildContext context, CallAgentProvider provider) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete all stored call data?'),
        content: const Text('This will permanently remove eligible call history, transcripts, and recordings.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.redAccent),
            onPressed: () {
              provider.purgeAllData();
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('All stored call records have been deleted.')));
            },
            child: const Text('Permanently Purge'),
          )
        ],
      ),
    );
  }
}
