import 'package:flutter/material.dart';
import '../models/call_record.dart';
import '../models/urgent_alert.dart';
import '../models/agent_settings.dart';
import '../services/api_service.dart';

class CallAgentProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  bool _isOnline = true;
  bool get isOnline => _isOnline;

  List<CallRecord> _calls = [];
  List<CallRecord> get calls => _calls;

  List<UrgentAlert> _alerts = [];
  List<UrgentAlert> get alerts => _alerts;

  AgentSettings _settings = AgentSettings();
  AgentSettings get settings => _settings;

  Map<String, String> _connectionStatus = {
    'firebase': 'CONNECTED',
    'openAI': 'CONNECTED',
    'exotel': 'CONNECTED',
    'sms': 'CONNECTED',
    'whatsapp': 'CONNECTED',
  };
  Map<String, String> get connectionStatus => _connectionStatus;

  CallAgentProvider() {
    loadInitialData();
  }

  Future<void> loadInitialData() async {
    _isLoading = true;
    notifyListeners();

    try {
      final dashboard = await _apiService.getDashboard();
      _isOnline = dashboard['agentStatus'] == 'ONLINE';
      if (dashboard['connectionStatus'] != null) {
        _connectionStatus = Map<String, String>.from(dashboard['connectionStatus']);
      }

      _calls = await _apiService.getCalls();
      _alerts = await _apiService.getAlerts();
      _settings = await _apiService.getSettings();
    } catch (_) {
      // Keep real states, no mock seeding in production
    }

    _isLoading = false;
    notifyListeners();
  }

  void toggleAgentOnline(bool value) {
    _isOnline = value;
    _settings.agentEnabled = value;
    _apiService.updateSettings(_settings);
    notifyListeners();
  }

  Future<void> updateSettings(AgentSettings newSettings) async {
    _settings = newSettings;
    await _apiService.updateSettings(newSettings);
    notifyListeners();
  }

  Future<void> simulateCallScenario(String scenario) async {
    _isLoading = true;
    notifyListeners();

    final newCall = await _apiService.simulateCall(scenario: scenario);
    if (newCall != null) {
      _calls.insert(0, newCall);
      if (newCall.urgency == 'HIGH' || newCall.urgency == 'CRITICAL') {
        _alerts.insert(0, UrgentAlert(
          alertId: 'alert_${DateTime.now().millisecondsSinceEpoch}',
          callId: newCall.callId,
          callerName: newCall.callerName,
          callerNumber: newCall.callerNumber,
          urgency: newCall.urgency,
          reason: newCall.reason,
          summary: newCall.summary,
          status: 'DELIVERED',
          provider: 'Exotel',
          createdAt: 'Just now',
        ));
      }
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<void> sendTestSms() async {
    await _apiService.testSmsAlert();
  }

  Future<void> sendTestPush() async {
    await _apiService.testPushNotification();
  }

  Future<Map<String, dynamic>> sendTestWhatsApp({String? recipientNumber}) async {
    return await _apiService.testWhatsAppNotification(recipientNumber: recipientNumber);
  }

  Future<Map<String, dynamic>> retryWhatsAppAlert(String alertId) async {
    final res = await _apiService.retryWhatsAppAlert(alertId);
    // Update local alert list
    final idx = _alerts.indexWhere((a) => a.alertId == alertId);
    if (idx != -1) {
      final old = _alerts[idx];
      _alerts[idx] = UrgentAlert(
        alertId: old.alertId,
        callId: old.callId,
        callerName: old.callerName,
        callerNumber: old.callerNumber,
        urgency: old.urgency,
        reason: old.reason,
        summary: old.summary,
        status: 'DELIVERED',
        smsStatus: old.smsStatus,
        whatsappStatus: res['status'] == 'SENT' ? 'SENT' : 'FAILED',
        fcmStatus: old.fcmStatus,
        provider: old.provider,
        createdAt: old.createdAt,
      );
      notifyListeners();
    }
    return res;
  }

  Future<void> deleteCall(String callId) async {
    _calls.removeWhere((c) => c.callId == callId);
    await _apiService.deleteCall(callId);
    notifyListeners();
  }

  Future<void> deleteAlert(String alertId) async {
    _alerts.removeWhere((a) => a.alertId == alertId);
    await _apiService.deleteAlert(alertId);
    notifyListeners();
  }

  Future<void> purgeAllData() async {
    _calls.clear();
    _alerts.clear();
    await _apiService.purgeAllData();
    notifyListeners();
  }
}
