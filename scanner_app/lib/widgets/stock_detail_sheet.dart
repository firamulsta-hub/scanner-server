import 'package:flutter/material.dart';
import '../models/scanner_models.dart';
import '../theme/app_theme.dart';

class StockDetailSheet extends StatelessWidget {
  final StockItem item;

  const StockDetailSheet({super.key, required this.item});

  String numText(double? value) {
    if (value == null) return '-';

    final isInt = value % 1 == 0;
    final str = isInt
        ? value.toInt().toString()
        : value.toStringAsFixed(2);

    return _comma(str);
  }

  String _comma(String digits) {
    final reg = RegExp(r'\B(?=(\d{3})+(?!\d))');
    return digits.replaceAllMapped(reg, (m) => ',');
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => Navigator.pop(context), // 🔥 내부 터치하면 닫힘
      child: Container(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
        decoration: const BoxDecoration(
          color: AppColors.panel,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: SafeArea(
          top: false,
          child: SingleChildScrollView(
            child: GestureDetector(
              onTap: () {}, // 내부 요소 클릭 막기 (버튼 대비)
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 50,
                      height: 5,
                      decoration: BoxDecoration(
                        color: AppColors.line,
                        borderRadius: BorderRadius.circular(10),
                      ),
                    ),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    '${item.code} / ${item.name}',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                      color: AppColors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    item.scannerType.isEmpty
                        ? item.market
                        : '${item.scannerType} / ${item.market}',
                    style: const TextStyle(color: AppColors.muted),
                  ),
                  const SizedBox(height: 18),

                  _row('현재가', numText(item.currentPrice)),
                  _row('등락률', '${item.changePercent.toStringAsFixed(2)}%'),
                  _row('전략', item.scannerType),
                  _row('진입', numText(item.entry1)),
                  _row('손절', numText(item.stop)),
                  _row('목표', numText(item.target1)),
                  _row('RR', numText(item.rr)),
                  _row('코멘트', item.comment ?? '-'),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _row(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 72,
            child: Text(label, style: const TextStyle(color: AppColors.muted)),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: AppColors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}