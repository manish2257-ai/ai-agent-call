import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/call_agent_provider.dart';

class SetupIntegrationsScreen extends StatelessWidget {
  const SetupIntegrationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CallAgentProvider>(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Setup & Integrations')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // WhatsApp Cloud API Card
          Card(
            color: const Color(0xFF132F2B),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: const BorderSide(color: Color(0xFF25D366), width: 1.2),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: const [
                      Icon(Icons.chat_bubble_rounded, color: Color(0xFF25D366)),
                      SizedBox(width: 10),
                      Text('WhatsApp Business Cloud API', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text('Official WhatsApp Business Platform urgent notification channel.'),
                  const SizedBox(height: 8),
                  const Text('1. Register at developers.facebook.com and create a WhatsApp Business app.'),
                  const Text('2. Retrieve Phone Number ID and System User Permanent Access Token.'),
                  const Text('3. Configure variables in backend `.env` (kept 100% server-side):'),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(color: Colors.black38, borderRadius: BorderRadius.circular(6)),
                    child: const SelectableText(
                      'WHATSAPP_ENABLED=true\n'
                      'WHATSAPP_ACCESS_TOKEN=<system_user_token>\n'
                      'WHATSAPP_PHONE_NUMBER_ID=<phone_number_id>\n'
                      'WHATSAPP_BUSINESS_ACCOUNT_ID=<waba_id>\n'
                      'WHATSAPP_RECIPIENT_PHONE_NUMBER=+919876543210\n'
                      'WHATSAPP_API_VERSION=v20.0',
                      style: TextStyle(fontFamily: 'monospace', fontSize: 11, color: Color(0xFF69F0AE)),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF25D366),
                        side: const BorderSide(color: Color(0xFF25D366)),
                      ),
                      icon: const Icon(Icons.send_rounded),
                      label: const Text('Test WhatsApp Notification'),
                      onPressed: () async {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Dispatching test WhatsApp alert...'), duration: Duration(seconds: 1)),
                        );
                        final res = await provider.sendTestWhatsApp();
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              backgroundColor: res['success'] == true ? Colors.green[800] : Colors.red[800],
                              content: Text(res['message'] ?? 'WhatsApp test message sent successfully!'),
                            ),
                          );
                        }
                      },
                    ),
                  )
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Exotel Telephony Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: const [
                      Icon(Icons.phone_in_talk_rounded, color: Color(0xFF00E5FF)),
                      SizedBox(width: 10),
                      Text('Exotel Telephony & SMS', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  const Text('1. Log in to your Exotel dashboard at my.exotel.com.'),
                  const Text('2. Acquire a cloud virtual number (VN) for your AI receptionist.'),
                  const Text('3. Configure incoming call Passthru Applet to point to:'),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(color: Colors.black26, borderRadius: BorderRadius.circular(6)),
                    child: const SelectableText('POST https://your-server.com/webhooks/exotel/incoming', style: TextStyle(fontFamily: 'monospace', fontSize: 12)),
                  ),
                  const SizedBox(height: 8),
                  const Text('4. Set status callback URL to:'),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(color: Colors.black26, borderRadius: BorderRadius.circular(6)),
                    child: const SelectableText('POST https://your-server.com/webhooks/exotel/status', style: TextStyle(fontFamily: 'monospace', fontSize: 12)),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // OpenAI Voice AI Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Row(
                    children: [
                      Icon(Icons.psychology_rounded, color: Colors.purpleAccent),
                      SizedBox(width: 10),
                      Text('OpenAI Voice Processing', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  SizedBox(height: 12),
                  Text('1. Obtain an API Key from platform.openai.com.'),
                  Text('2. Place OPENAI_API_KEY in the backend environment file (.env).'),
                  Text('3. Defaults to gpt-4o-mini for low-latency conversational audio turns.'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Optional Carrier Call Forwarding
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: const [
                      Icon(Icons.call_split_rounded, color: Colors.greenAccent),
                      SizedBox(width: 10),
                      Text('Optional Carrier Call Forwarding', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'To automatically route missed or busy calls from your India SIM card to your AI receptionist, dial these standard MMI codes from your phone dialer:',
                    style: TextStyle(fontSize: 13, color: Colors.grey),
                  ),
                  const SizedBox(height: 12),
                  _buildForwardingRow('Jio / Airtel / Vi / BSNL (When Unanswered):', '*61*${provider.settings.aiPhoneNumber.replaceAll(" ", "")}#'),
                  _buildForwardingRow('Jio / Airtel / Vi / BSNL (When Busy):', '*67*${provider.settings.aiPhoneNumber.replaceAll(" ", "")}#'),
                  _buildForwardingRow('Jio / Airtel / Vi / BSNL (When Unreachable):', '*62*${provider.settings.aiPhoneNumber.replaceAll(" ", "")}#'),
                  _buildForwardingRow('Deactivate / Reset Call Forwarding:', '##002#'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildForwardingRow(String label, String code) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500)),
          const SizedBox(height: 2),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(color: Colors.black26, borderRadius: BorderRadius.circular(4)),
            child: Text(code, style: const TextStyle(fontFamily: 'monospace', color: Colors.greenAccent, fontSize: 13)),
          ),
        ],
      ),
    );
  }
}
