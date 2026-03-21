import 'package:flutter/material.dart';
import '../models/scanner_models.dart';
import '../theme/app_theme.dart';

class IndexBanner extends StatelessWidget {
  final Map<String, IndexInfo> indexes;

  const IndexBanner({super.key, required this.indexes});

  String formatIndex(double value) {
    final fixed = value.toStringAsFixed(2);
    final parts = fixed.split('.');
    return '${_comma(parts[0])}.${parts[1]}';
  }

  String _comma(String digits) {
    final reg = RegExp(r'\B(?=(\d{3})+(?!\d))');
    return digits.replaceAllMapped(reg, (m) => ',');
  }

  @override
  Widget build(BuildContext context) {
    final kospi = indexes['kospi'];
    final kosdaq = indexes['kosdaq'];

    return Row(
      children: [
        if (kospi != null) Expanded(child: _tile(kospi)),
        if (kospi != null && kosdaq != null) const SizedBox(width: 10),
        if (kosdaq != null) Expanded(child: _tile(kosdaq)),
      ],
    );
  }

  Widget _tile(IndexInfo item) {
    final color = item.changePercent >= 0 ? AppColors.red : AppColors.blue;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.panel,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            item.name,
            style: const TextStyle(color: AppColors.muted),
          ),
          const SizedBox(height: 6),
          Text(
            formatIndex(item.value),
            style: const TextStyle(
              color: AppColors.white,
              fontSize: 18,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            '${item.changePercent >= 0 ? '+' : ''}${item.changePercent.toStringAsFixed(2)}%',
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}