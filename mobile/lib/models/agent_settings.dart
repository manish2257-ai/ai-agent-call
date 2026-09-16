class AgentSettings {
  bool agentEnabled;
  String ownerPhoneNumber;
  String aiPhoneNumber;
  String aiGreeting;
  String urgencyThreshold;
  bool smsAlertsEnabled;
  bool whatsappAlertsEnabled;
  String whatsappRecipientNumber;
  String whatsappIntegrationStatus;
  bool pushNotificationsEnabled;
  int maxCallDurationSeconds;
  bool recordingEnabled;
  bool persistentTranscriptionEnabled;
  String consentMode;
  int callMetadataRetentionDays;
  int urgentAlertRetentionDays;

  AgentSettings({
    this.agentEnabled = true,
    this.ownerPhoneNumber = '+91 73679 66177',
    this.aiPhoneNumber = '+91 80471 00000',
    this.aiGreeting = "Hello, you've reached Manish's AI assistant. How can I help?",
    this.urgencyThreshold = 'HIGH',
    this.smsAlertsEnabled = true,
    this.whatsappAlertsEnabled = true,
    this.whatsappRecipientNumber = '+91 73679 66177',
    this.whatsappIntegrationStatus = 'CONNECTED',
    this.pushNotificationsEnabled = true,
    this.maxCallDurationSeconds = 180,
    this.recordingEnabled = false,
    this.persistentTranscriptionEnabled = false,
    this.consentMode = 'DISABLE_RECORDING_AND_TRANSCRIPTION',
    this.callMetadataRetentionDays = 90,
    this.urgentAlertRetentionDays = 90,
  });

  factory AgentSettings.fromJson(Map<String, dynamic> json) {
    return AgentSettings(
      agentEnabled: json['agentEnabled'] ?? true,
      ownerPhoneNumber: json['ownerPhoneNumber'] ?? '+91 73679 66177',
      aiPhoneNumber: json['aiPhoneNumber'] ?? '+91 80471 00000',
      aiGreeting: json['aiGreeting'] ?? "Hello, you've reached Manish's AI assistant.",
      urgencyThreshold: json['urgencyThreshold'] ?? 'HIGH',
      smsAlertsEnabled: json['smsAlertsEnabled'] ?? true,
      whatsappAlertsEnabled: json['whatsappAlertsEnabled'] ?? true,
      whatsappRecipientNumber: json['whatsappRecipientNumber'] ?? '+91 73679 66177',
      whatsappIntegrationStatus: json['whatsappIntegrationStatus'] ?? 'CONNECTED',
      pushNotificationsEnabled: json['pushNotificationsEnabled'] ?? true,
      maxCallDurationSeconds: json['maxCallDurationSeconds'] ?? 180,
      recordingEnabled: json['recordingEnabled'] ?? false,
      persistentTranscriptionEnabled: json['persistentTranscriptionEnabled'] ?? false,
      consentMode: json['consentMode'] ?? 'DISABLE_RECORDING_AND_TRANSCRIPTION',
      callMetadataRetentionDays: json['callMetadataRetentionDays'] ?? 90,
      urgentAlertRetentionDays: json['urgentAlertRetentionDays'] ?? 90,
    );
  }

  Map<String, dynamic> toJson() => {
    'agentEnabled': agentEnabled,
    'ownerPhoneNumber': ownerPhoneNumber,
    'aiPhoneNumber': aiPhoneNumber,
    'aiGreeting': aiGreeting,
    'urgencyThreshold': urgencyThreshold,
    'smsAlertsEnabled': smsAlertsEnabled,
    'whatsappAlertsEnabled': whatsappAlertsEnabled,
    'whatsappRecipientNumber': whatsappRecipientNumber,
    'whatsappIntegrationStatus': whatsappIntegrationStatus,
    'pushNotificationsEnabled': pushNotificationsEnabled,
    'maxCallDurationSeconds': maxCallDurationSeconds,
    'recordingEnabled': recordingEnabled,
    'persistentTranscriptionEnabled': persistentTranscriptionEnabled,
    'consentMode': consentMode,
    'callMetadataRetentionDays': callMetadataRetentionDays,
    'urgentAlertRetentionDays': urgentAlertRetentionDays,
  };
}
