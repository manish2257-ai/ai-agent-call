import 'package:flutter/material.dart';

class AppTheme {
  static const Color primaryCyan = Color(0xFF00E5FF);
  static const Color accentIndigo = Color(0xFF6366F1);
  static const Color darkCanvas = Color(0xFF0F172A);
  static const Color darkCard = Color(0xFF1E293B);
  static const Color urgencyHigh = Color(0xFFF97316);
  static const Color urgencyCritical = Color(0xFFEF4444);
  static const Color urgencyMedium = Color(0xFF38BDF8);
  static const Color urgencyLow = Color(0xFF10B981);

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: const ColorScheme.dark(
        primary: primaryCyan,
        secondary: accentIndigo,
        surface: darkCard,
        background: darkCanvas,
      ),
      scaffoldBackgroundColor: darkCanvas,
      appBarTheme: const AppBarTheme(
        backgroundColor: darkCanvas,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardTheme(
        color: darkCard,
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    );
  }

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: const ColorScheme.light(
        primary: Color(0xFF0097A7),
        secondary: accentIndigo,
        surface: Colors.white,
        background: Color(0xFFF8FAFC),
      ),
      scaffoldBackgroundColor: const Color(0xFFF8FAFC),
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardTheme(
        color: Colors.white,
        elevation: 1,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    );
  }
}
