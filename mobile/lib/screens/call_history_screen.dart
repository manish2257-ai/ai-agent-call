import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/call_agent_provider.dart';
import '../models/call_record.dart';
import 'call_details_screen.dart';

class CallHistoryScreen extends StatefulWidget {
  const CallHistoryScreen({super.key});

  @override
  State<CallHistoryScreen> createState() => _CallHistoryScreenState();
}

class _CallHistoryScreenState extends State<CallHistoryScreen> {
  String _selectedFilter = 'ALL';

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CallAgentProvider>(context);
    final allCalls = provider.calls;

    final filteredCalls = allCalls.where((c) {
      if (_selectedFilter == 'URGENT') return c.urgency == 'HIGH' || c.urgency == 'CRITICAL';
      if (_selectedFilter == 'ESCALATED') return c.status == 'ESCALATED';
      if (_selectedFilter == 'ROUTINE') return c.urgency == 'LOW' || c.urgency == 'MEDIUM';
      return true;
    }).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Call History'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep_outlined),
            tooltip: 'Purge All Call Data',
            onPressed: () => _confirmPurge(context, provider),
          )
        ],
      ),
      body: Column(
        children: [
          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                _buildFilterChip('ALL', 'All Calls (${allCalls.length})'),
                const SizedBox(width: 8),
                _buildFilterChip('URGENT', 'Urgent Only'),
                const SizedBox(width: 8),
                _buildFilterChip('ESCALATED', 'Escalated to SMS'),
                const SizedBox(width: 8),
                _buildFilterChip('ROUTINE', 'Routine/Inquiry'),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: filteredCalls.isEmpty
                ? const Center(child: Text('No matching call records found.'))
                : ListView.builder(
                    itemCount: filteredCalls.length,
                    itemBuilder: (context, idx) {
                      final call = filteredCalls[idx];
                      return _buildCallTile(context, call, provider);
                    },
                  ),
          )
        ],
      ),
    );
  }

  Widget _buildFilterChip(String key, String label) {
    final isSelected = _selectedFilter == key;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        if (selected) setState(() => _selectedFilter = key);
      },
    );
  }

  Widget _buildCallTile(BuildContext context, CallRecord call, CallAgentProvider provider) {
    final isUrgent = call.urgency == 'HIGH' || call.urgency == 'CRITICAL';
    return Dismissible(
      key: Key(call.callId),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        color: Colors.redAccent,
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      onDismissed: (_) {
        provider.deleteCall(call.callId);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Call from ${call.callerName} deleted.')));
      },
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: isUrgent ? const Color(0xFFF97316).withOpacity(0.2) : Colors.blueGrey.withOpacity(0.2),
          child: Icon(
            isUrgent ? Icons.notification_important_rounded : Icons.call_received_rounded,
            color: isUrgent ? const Color(0xFFF97316) : Colors.cyanAccent,
          ),
        ),
        title: Text(call.callerName, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(call.reason, maxLines: 1, overflow: TextOverflow.ellipsis),
            Text('${call.createdAt} • ${call.duration}s duration', style: TextStyle(color: Colors.grey.shade400, fontSize: 12)),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: (isUrgent ? const Color(0xFFF97316) : Colors.teal).withOpacity(0.15),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            call.urgency,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: isUrgent ? const Color(0xFFF97316) : Colors.tealAccent,
            ),
          ),
        ),
        onTap: () {
          Navigator.push(context, MaterialPageRoute(builder: (_) => CallDetailsScreen(call: call)));
        },
      ),
    );
  }

  void _confirmPurge(BuildContext context, CallAgentProvider provider) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete all stored call data?'),
        content: const Text('This will permanently remove eligible call history, transcripts, and recordings. This action cannot be undone.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.redAccent),
            onPressed: () {
              provider.purgeAllData();
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('All call data permanently erased.')));
            },
            child: const Text('Delete All Data'),
          )
        ],
      ),
    );
  }
}
