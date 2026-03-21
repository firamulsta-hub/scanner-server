import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class SummaryPanel extends StatelessWidget {
  final String title;
  final String body;

  const SummaryPanel({
    super.key,
    required this.title,
    required this.body,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.panelSoft,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: AppColors.white)),
          const SizedBox(height: 10),
          Text(body, style: const TextStyle(color: AppColors.muted, height: 1.6)),
        ],
      ),
    );
  }
}
