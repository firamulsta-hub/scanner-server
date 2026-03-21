import 'package:flutter/material.dart';

class AppColors {
  static const bg = Color(0xFF0C1016);
  static const panel = Color(0xFF151B24);
  static const panelSoft = Color(0xFF1B2430);
  static const line = Color(0xFF283241);
  static const white = Color(0xFFF3F6FA);
  static const muted = Color(0xFFAAB6C5);
  static const blue = Color(0xFF67B7FF);
  static const red = Color(0xFFFF7A86);
  static const green = Color(0xFF49D17D);
  static const orange = Color(0xFFFFB457);
}

class AppTheme {
  static ThemeData dark() {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.bg,
      fontFamily: 'Roboto',
      colorScheme: const ColorScheme.dark(
        primary: AppColors.blue,
        secondary: AppColors.green,
        surface: AppColors.panel,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.bg,
        elevation: 0,
        centerTitle: true,
        foregroundColor: AppColors.white,
      ),
      textTheme: const TextTheme(
        headlineMedium: TextStyle(color: AppColors.white, fontWeight: FontWeight.w700),
        titleLarge: TextStyle(color: AppColors.white, fontWeight: FontWeight.w700),
        bodyLarge: TextStyle(color: AppColors.white),
        bodyMedium: TextStyle(color: AppColors.muted),
      ),
      useMaterial3: true,
    );
  }
}
