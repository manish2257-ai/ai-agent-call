class UrgentAlert {
  final String alertId;
  final String callId;
  final String callerName;
  final String callerNumber;
  final String urgency;
  final String reason;
  final String summary;
  final String status;
  final String smsStatus;
  final String whatsappStatus;
  final String fcmStatus;
  final String provider;
  final String createdAt;

  UrgentAlert({
    required this.alertId,
    required this.callId,
    required this.callerName,
    required this.callerNumber,
    required this.urgency,
    required this.reason,
    required this.summary,
    required this.status,
    this.smsStatus = 'SENT',
    this.whatsappStatus = 'SENT',
    this.fcmStatus = 'SENT',
    required this.provider,
    required this.createdAt,
  });

  factory UrgentAlert.fromJson(Map<String, dynamic> json) {
    return UrgentAlert(
      alertId: json['alertId'] ?? json['id'] ?? '',
      callId: json['callId'] ?? '',
      callerName: json['callerName'] ?? 'Unknown Caller',
      callerNumber: json['callerNumber'] ?? '',
      urgency: json['urgency'] ?? 'HIGH',
      reason: json['reason'] ?? '',
      summary: json['summary'] ?? '',
      status: json['status'] ?? 'DELIVERED',
      smsStatus: json['smsStatus'] ?? 'SENT',
      whatsappStatus: json['whatsappStatus'] ?? 'SENT',
      fcmStatus: json['fcmStatus'] ?? 'SENT',
      provider: json['provider'] ?? 'Exotel & WhatsApp Cloud',
      createdAt: json['createdAt'] ?? '',
    );
  }
}
