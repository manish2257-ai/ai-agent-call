class TranscriptMessage {
  final String speaker;
  final String content;
  final String timestamp;

  TranscriptMessage({
    required this.speaker,
    required this.content,
    required this.timestamp,
  });

  factory TranscriptMessage.fromJson(Map<String, dynamic> json) {
    return TranscriptMessage(
      speaker: json['speaker'] ?? 'Unknown',
      content: json['content'] ?? '',
      timestamp: json['timestamp'] ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
    'speaker': speaker,
    'content': content,
    'timestamp': timestamp,
  };
}

class CallRecord {
  final String callId;
  final String callerName;
  final String callerNumber;
  final String reason;
  final String urgency;
  final String summary;
  final bool callbackRequired;
  final String status;
  final bool smsSent;
  final bool whatsappSent;
  final bool fcmSent;
  final String whatsappStatus;
  final String? whatsappMessageId;
  final String? whatsappSentAt;
  final int duration;
  final String consentStatus;
  final String createdAt;
  final List<TranscriptMessage> messages;

  CallRecord({
    required this.callId,
    required this.callerName,
    required this.callerNumber,
    required this.reason,
    required this.urgency,
    required this.summary,
    required this.callbackRequired,
    required this.status,
    required this.smsSent,
    this.whatsappSent = false,
    this.fcmSent = false,
    this.whatsappStatus = 'NOT_CONFIGURED',
    this.whatsappMessageId,
    this.whatsappSentAt,
    required this.duration,
    required this.consentStatus,
    required this.createdAt,
    required this.messages,
  });

  factory CallRecord.fromJson(Map<String, dynamic> json) {
    var rawMsgs = json['messages'] as List? ?? [];
    List<TranscriptMessage> msgs = rawMsgs
        .map((m) => TranscriptMessage.fromJson(Map<String, dynamic>.from(m)))
        .toList();

    return CallRecord(
      callId: json['callId'] ?? json['id'] ?? '',
      callerName: json['callerName'] ?? 'Unknown Caller',
      callerNumber: json['callerNumber'] ?? '',
      reason: json['reason'] ?? '',
      urgency: json['urgency'] ?? 'LOW',
      summary: json['summary'] ?? '',
      callbackRequired: json['callbackRequired'] ?? false,
      status: json['status'] ?? 'COMPLETED',
      smsSent: json['smsSent'] ?? false,
      whatsappSent: json['whatsappSent'] ?? false,
      fcmSent: json['fcmSent'] ?? false,
      whatsappStatus: json['whatsappStatus'] ?? 'NOT_CONFIGURED',
      whatsappMessageId: json['whatsappMessageId'],
      whatsappSentAt: json['whatsappSentAt'],
      duration: json['duration'] ?? json['durationSeconds'] ?? 0,
      consentStatus: json['consentStatus'] ?? 'NOT_REQUIRED',
      createdAt: json['createdAt'] ?? '',
      messages: msgs,
    );
  }
}
