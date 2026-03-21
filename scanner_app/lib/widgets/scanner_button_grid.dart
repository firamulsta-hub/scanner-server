import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class ScannerButtonGrid extends StatelessWidget {
  final String selectedKey;
  final void Function(String key) onSelect;

  const ScannerButtonGrid({
    super.key,
    required this.selectedKey,
    required this.onSelect,
  });

  static const buttons = [
    ('50', 'Stable 5.0\n(안정형)'),
    ('51', 'Swing 5.1\n(단타형)'),
    ('60', 'Force 6.0\n(세력포착형)'),
    ('70', 'Early 7.0\n(세력초기진입포착형)'),
    ('92', 'Strategy 9.2\n(자동 전략 추천)'),
    ('93b', 'Total 9.3B\n(전체 조건 통합)'),
  ];

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 10,
      mainAxisSpacing: 10,
      childAspectRatio: 2.2,
      children: buttons.map((entry) {
        final isSelected = selectedKey == entry.$1;
        return InkWell(
          onTap: () => onSelect(entry.$1),
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: isSelected ? AppColors.blue.withOpacity(0.18) : AppColors.panel,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: isSelected ? AppColors.blue : AppColors.line, width: 1.2),
            ),
            child: Center(
              child: Text(
                entry.$2,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: isSelected ? AppColors.white : AppColors.muted,
                  fontWeight: FontWeight.w700,
                  height: 1.4,
                ),
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}
