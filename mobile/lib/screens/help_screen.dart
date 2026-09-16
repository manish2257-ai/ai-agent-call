import 'package:flutter/material.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Help & Documentation')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildFaqItem(
            'How does the AI answer my phone calls?',
            'Callers dial your dedicated Exotel cloud virtual number. Exotel routes the call via inbound webhook to your FastAPI backend, where the AI assistant answers, identifies itself, determines caller intent, and checks urgency.',
          ),
          _buildFaqItem(
            'What happens when an urgent call occurs?',
            'If the AI classifies a call as HIGH or CRITICAL urgency (e.g. server outage, client contract deadline today), it immediately dispatches an SMS notification to your personal mobile number via Exotel and sends a Firebase push notification to this app.',
          ),
          _buildFaqItem(
            'Can callers tell it is an AI?',
            'Yes. The assistant always identifies itself clearly at the start of the call. If asked "Are you a real person?", it answers: "No. I\'m an AI assistant helping manage Manish\'s calls."',
          ),
          _buildFaqItem(
            'Is call recording enabled by default?',
            'No. Call recording and persistent transcripts are strictly OFF by default to respect caller privacy. You can configure consent mode and retention rules in the Privacy & Retention screen.',
          ),
          _buildFaqItem(
            'How can I test the system without real telephony fees?',
            'Use the "Test Normal Call" or "Test Urgent Call" buttons on the Dashboard. This runs a complete end-to-end simulation of call answering, urgency analysis, summary generation, and SMS triggering.',
          ),
        ],
      ),
    );
  }

  Widget _buildFaqItem(String question, String answer) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        title: Text(question, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Text(answer, style: TextStyle(color: Colors.grey.shade300, height: 1.4)),
          )
        ],
      ),
    );
  }
}
