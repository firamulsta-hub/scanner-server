import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class ScannerHeader extends StatelessWidget {
  final String title;
  final String updatedAt;

  const ScannerHeader({
    super.key,
    required this.title,
    required this.updatedAt,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.panel,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700, color: AppColors.white)),
          const SizedBox(height: 8),
          Text('데이터 집계 기준: $updatedAt', style: const TextStyle(color: AppColors.muted)),
        ],
      ),
    );
  }
}
