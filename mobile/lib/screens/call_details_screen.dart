import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/call_record.dart';
import '../providers/call_agent_provider.dart';

class CallDetailsScreen extends StatelessWidget {
  final CallRecord call;

  const CallDetailsScreen({super.key, required this.call});

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CallAgentProvider>(context, listen: false);
    final isUrgent = call.urgency == 'HIGH' || call.urgency == 'CRITICAL';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Call Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            tooltip: 'Delete Call Record',
            onPressed: () {
              provider.deleteCall(call.callId);
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Call record deleted.')));
            },
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Caller Header Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(call.callerName, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: (isUrgent ? const Color(0xFFF97316) : Colors.green).withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            call.urgency,
                            style: TextStyle(
                              color: isUrgent ? const Color(0xFFF97316) : Colors.greenAccent,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(call.callerNumber, style: TextStyle(color: Colors.grey.shade400)),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Icon(Icons.access_time_rounded, size: 16, color: Colors.grey.shade400),
                        const SizedBox(width: 6),
                        Text('${call.createdAt}  •  ${call.duration} seconds', style: TextStyle(color: Colors.grey.shade400, fontSize: 13)),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        Icon(Icons.shield_outlined, size: 16, color: Colors.grey.shade400),
                        const SizedBox(width: 6),
                        Text('Consent Status: ${call.consentStatus}', style: TextStyle(color: Colors.grey.shade400, fontSize: 13)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // AI Reason & Summary Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Reason for Call', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF00E5FF))),
                    const SizedBox(height: 6),
                    Text(call.reason, style: const TextStyle(fontSize: 15)),
                    const Divider(height: 24),
                    const Text('AI Structured Summary', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF00E5FF))),
                    const SizedBox(height: 6),
                    Text(call.summary, style: const TextStyle(fontSize: 15)),
                    const Divider(height: 24),
                    Row(
                      children: [
                        Icon(
                          call.callbackRequired ? Icons.call_missed_outgoing_rounded : Icons.check_circle_outline,
                          color: call.callbackRequired ? const Color(0xFFF97316) : Colors.greenAccent,
                        ),
                        const SizedBox(width: 10),
                        Text(
                          call.callbackRequired ? 'Immediate Callback Requested' : 'No Immediate Callback Needed',
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                      ],
                    ),
                    if (call.smsSent) ...[
                      const SizedBox(height: 12),
                      Row(
                        children: const [
                          Icon(Icons.sms_rounded, size: 18, color: Color(0xFF00E5FF)),
                          SizedBox(width: 10),
                          Text('Priority SMS Alert Dispatched to Owner', style: TextStyle(color: Color(0xFF00E5FF), fontSize: 13)),
                        ],
                      )
                    ],
                    if (call.whatsappSent) ...[
                      const SizedBox(height: 8),
                      Row(
                        children: const [
                          Icon(Icons.chat_bubble_rounded, size: 18, color: Color(0xFF25D366)),
                          SizedBox(width: 10),
                          Text('WhatsApp Urgent Alert Dispatched', style: TextStyle(color: Color(0xFF25D366), fontSize: 13)),
                        ],
                      )
                    ]
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Conversation Transcript
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Conversation Transcript', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                        if (call.messages.isNotEmpty)
                          TextButton(
                            onPressed: () {
                              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Transcript cleared.')));
                            },
                            child: const Text('Delete Transcript', style: TextStyle(color: Colors.redAccent, fontSize: 12)),
                          )
                      ],
                    ),
                    const SizedBox(height: 12),
                    if (call.messages.isEmpty)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.blueGrey.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'Persistent transcript is disabled by default under your privacy settings. The AI processed caller speech temporarily in memory to generate the above summary.',
                          style: TextStyle(fontSize: 13, fontStyle: FontStyle.italic),
                        ),
                      )
                    else
                      ...call.messages.map((m) => _buildTranscriptBubble(m)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTranscriptBubble(TranscriptMessage msg) {
    final isAI = msg.speaker == 'AI';
    return Align(
      alignment: isAI ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isAI ? const Color(0xFF1E293B) : const Color(0xFF0284C7).withOpacity(0.3),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: isAI ? Colors.white12 : const Color(0xFF0284C7)),
        ),
        constraints: const BoxConstraints(maxWidth: 280),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              msg.speaker,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 11,
                color: isAI ? const Color(0xFF00E5FF) : Colors.orangeAccent,
              ),
            ),
            const SizedBox(height: 4),
            Text(msg.content, style: const TextStyle(fontSize: 14)),
          ],
        ),
      ),
    );
  }
}
