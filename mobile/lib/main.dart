import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/call_agent_provider.dart';
import 'theme/app_theme.dart';
import 'screens/splash_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => CallAgentProvider()),
      ],
      child: const AICallAgentApp(),
    ),
  );
}

class AICallAgentApp extends StatelessWidget {
  const AICallAgentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Personal Call Agent',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const SplashScreen(),
    );
  }
}
