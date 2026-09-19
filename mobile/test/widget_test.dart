import 'package:flutter_test/flutter_test.dart';
import 'package:ai_call_agent/models/call_record.dart';
import 'package:ai_call_agent/models/agent_settings.dart';

void main() {
  test('CallRecord deserialization test', () {
    final json = {
      'callId': 'call_123',
      'callerName': 'Rahul Verma',
      'callerNumber': '+919810012345',
      'reason': 'Production outage',
      'urgency': 'HIGH',
      'summary': 'Customer checkout failure',
      'callbackRequired': true,
      'status': 'ESCALATED',
      'smsSent': true,
      'duration': 54,
      'consentStatus': 'NOT_REQUIRED',
      'createdAt': 'Today, 10:41 AM',
      'messages': [
        {'speaker': 'AI', 'content': 'Hello', 'timestamp': '10:41 AM'}
      ]
    };

    final record = CallRecord.fromJson(json);
    expect(record.callId, 'call_123');
    expect(record.callerName, 'Rahul Verma');
    expect(record.urgency, 'HIGH');
    expect(record.callbackRequired, true);
    expect(record.messages.length, 1);
  });

  test('AgentSettings default privacy configuration test', () {
    final settings = AgentSettings();
    expect(settings.recordingEnabled, false);
    expect(settings.persistentTranscriptionEnabled, false);
    expect(settings.consentMode, 'DISABLE_RECORDING_AND_TRANSCRIPTION');
    expect(settings.callMetadataRetentionDays, 90);
  });
}
