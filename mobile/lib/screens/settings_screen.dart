import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/call_agent_provider.dart';
import '../models/agent_settings.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _ownerPhoneCtrl;
  late TextEditingController _greetingCtrl;
  late TextEditingController _whatsappPhoneCtrl;

  @override
  void initState() {
    super.initState();
    final settings = Provider.of<CallAgentProvider>(context, listen: false).settings;
    _ownerPhoneCtrl = TextEditingController(text: settings.ownerPhoneNumber);
    _greetingCtrl = TextEditingController(text: settings.aiGreeting);
    _whatsappPhoneCtrl = TextEditingController(text: settings.whatsappRecipientNumber);
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CallAgentProvider>(context);
    final settings = provider.settings;
    final waStatus = provider.connectionStatus['whatsapp'] ?? 'CONNECTED';
    final isWaConnected = waStatus == 'CONNECTED' || waStatus == 'SIMULATED';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Agent Settings'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            tooltip: 'Save Settings',
            onPressed: () {
              settings.ownerPhoneNumber = _ownerPhoneCtrl.text;
              settings.aiGreeting = _greetingCtrl.text;
              settings.whatsappRecipientNumber = _whatsappPhoneCtrl.text;
              provider.updateSettings(settings);
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Settings saved successfully.')));
            },
          )
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Agent ON/OFF Switch
          SwitchListTile(
            title: const Text('AI Call Receptionist Enabled', style: TextStyle(fontWeight: FontWeight.bold)),
            subtitle: const Text('Automatically answers calls routed to your Exotel virtual number'),
            value: settings.agentEnabled,
            activeColor: const Color(0xFF00E5FF),
            onChanged: (val) {
              setState(() => settings.agentEnabled = val);
              provider.toggleAgentOnline(val);
            },
          ),
          const Divider(),

          // Owner Phone & Greeting
          const SizedBox(height: 8),
          TextField(
            controller: _ownerPhoneCtrl,
            decoration: const InputDecoration(
              labelText: 'Owner Mobile Phone Number (for Urgent SMS)',
              helperText: 'SMS alerts will be routed here',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.phone_android_rounded),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _greetingCtrl,
            maxLines: 3,
            decoration: const InputDecoration(
              labelText: 'AI Spoken Greeting',
              helperText: 'Played immediately when answering caller',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.record_voice_over_rounded),
            ),
          ),
          const Divider(height: 32),

          // Notification Channels Section
          const Text('Notification Channels', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF00E5FF))),
          const SizedBox(height: 12),
          SwitchListTile(
            title: const Text('SMS Alerts'),
            subtitle: const Text('Dispatches urgent SMS via Exotel when threshold is met'),
            value: settings.smsAlertsEnabled,
            activeColor: const Color(0xFF00E5FF),
            onChanged: (val) => setState(() => settings.smsAlertsEnabled = val),
          ),
          SwitchListTile(
            title: const Text('WhatsApp Alerts'),
            subtitle: const Text('Dispatches official WhatsApp Cloud API urgent message'),
            value: settings.whatsappAlertsEnabled,
            activeColor: const Color(0xFF25D366),
            onChanged: (val) => setState(() => settings.whatsappAlertsEnabled = val),
          ),
          SwitchListTile(
            title: const Text('Push Notifications'),
            subtitle: const Text('Delivers Firebase Cloud Messaging alerts to APK'),
            value: settings.pushNotificationsEnabled,
            activeColor: const Color(0xFF00E5FF),
            onChanged: (val) => setState(() => settings.pushNotificationsEnabled = val),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _whatsappPhoneCtrl,
            decoration: const InputDecoration(
              labelText: 'WhatsApp Recipient Phone Number',
              helperText: 'Format with country code: e.g. +91 98765 43210',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.chat_bubble_outline_rounded, color: Color(0xFF25D366)),
            ),
          ),
          const SizedBox(height: 16),

          // Channel Status Indicators
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.white10),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Channel Integration Status', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey)),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _buildStatusPill('SMS', true),
                    _buildStatusPill('WhatsApp API', isWaConnected),
                    _buildStatusPill('Push Notifications', true),
                  ],
                ),
              ],
            ),
          ),
          const Divider(height: 32),

          // Urgency Threshold
          const Text('Urgency Threshold', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF00E5FF))),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: settings.urgencyThreshold,
            decoration: const InputDecoration(
              labelText: 'Alert Trigger Threshold',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'LOW', child: Text('Low (Alert on all calls)')),
              DropdownMenuItem(value: 'MEDIUM', child: Text('Medium (Business & scheduling)')),
              DropdownMenuItem(value: 'HIGH', child: Text('High (Default - Outages & Deadlines)')),
              DropdownMenuItem(value: 'CRITICAL', child: Text('Critical (Emergencies only)')),
            ],
            onChanged: (val) {
              if (val != null) setState(() => settings.urgencyThreshold = val);
            },
          ),
          const Divider(height: 32),

          // Consent & Privacy Controls
          const Text('Privacy & Consent Mode', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF00E5FF))),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: settings.consentMode,
            decoration: const InputDecoration(
              labelText: 'Caller Consent Mode',
              helperText: 'Jurisdiction-specific caller disclosure policy',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(
                value: 'DISABLE_RECORDING_AND_TRANSCRIPTION',
                child: Text('Disable Recording & Transcripts (Default MVP)'),
              ),
              DropdownMenuItem(
                value: 'DISCLOSURE_ONLY',
                child: Text('Disclosure Notice Only'),
              ),
              DropdownMenuItem(
                value: 'ASK_FOR_CONSENT',
                child: Text('Explicit Verbal/Keypad Consent Required'),
              ),
            ],
            onChanged: (val) {
              if (val != null) setState(() => settings.consentMode = val);
            },
          ),
          const SizedBox(height: 12),
          SwitchListTile(
            title: const Text('Audio Call Recording'),
            subtitle: const Text('OFF by default. Stores audio files only if consented.'),
            value: settings.recordingEnabled,
            activeColor: const Color(0xFF00E5FF),
            onChanged: (val) => setState(() => settings.recordingEnabled = val),
          ),
          SwitchListTile(
            title: const Text('Persistent Text Transcription'),
            subtitle: const Text('OFF by default. Saves text transcripts permanently.'),
            value: settings.persistentTranscriptionEnabled,
            activeColor: const Color(0xFF00E5FF),
            onChanged: (val) => setState(() => settings.persistentTranscriptionEnabled = val),
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: () {
              settings.ownerPhoneNumber = _ownerPhoneCtrl.text;
              settings.aiGreeting = _greetingCtrl.text;
              settings.whatsappRecipientNumber = _whatsappPhoneCtrl.text;
              provider.updateSettings(settings);
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('All settings updated.')));
            },
            icon: const Icon(Icons.save_rounded),
            label: const Text('Save Settings'),
            style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
          )
        ],
      ),
    );
  }

  Widget _buildStatusPill(String name, bool connected) {
    return Column(
      children: [
        Text(name, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
        const SizedBox(height: 4),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              connected ? Icons.check_circle_rounded : Icons.cancel_rounded,
              size: 14,
              color: connected ? Colors.greenAccent : Colors.redAccent,
            ),
            const SizedBox(width: 4),
            Text(
              connected ? 'Connected' : 'Not Configured',
              style: TextStyle(
                fontSize: 10,
                color: connected ? Colors.greenAccent : Colors.redAccent,
              ),
            )
          ],
        )
      ],
    );
  }
}
