import 'package:flutter/material.dart';
import '../models/scanner_models.dart';
import '../theme/app_theme.dart';
import 'stock_detail_sheet.dart';

class StockCard extends StatelessWidget {
  final StockItem item;

  const StockCard({super.key, required this.item});

  Color get statusColor {
    switch (item.status) {
      case 'PASS':
        return AppColors.green;
      case 'WATCH':
        return AppColors.orange;
      default:
        return AppColors.muted;
    }
  }

  Color get priceColor => item.changePercent >= 0 ? AppColors.red : AppColors.blue;

  String formatPrice(double value) {
    final isInt = value % 1 == 0;
    if (!isInt) {
      final parts = value.toStringAsFixed(2).split('.');
      return '${_comma(parts[0])}.${parts[1]}';
    }
    return _comma(value.toInt().toString());
  }

  String _comma(String digits) {
    final reg = RegExp(r'\B(?=(\d{3})+(?!\d))');
    return digits.replaceAllMapped(reg, (m) => ',');
  }

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        showModalBottomSheet(
          context: context,
          backgroundColor: Colors.transparent,
          isScrollControlled: true,
          builder: (_) => StockDetailSheet(item: item),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.panel,
          borderRadius: BorderRadius.circular(18),
          border: Border.all(color: AppColors.line),
        ),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(item.name, style: const TextStyle(color: AppColors.white, fontSize: 17, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 6),
                  Text('${item.code}  ·  ${item.market}', style: const TextStyle(color: AppColors.muted)),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Text(
                        '현재가 ${formatPrice(item.currentPrice)}',
                        style: TextStyle(color: priceColor, fontWeight: FontWeight.w700),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '${item.changePercent >= 0 ? '+' : ''}${item.changePercent.toStringAsFixed(2)}%',
                        style: TextStyle(color: priceColor),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.15),
                borderRadius: BorderRadius.circular(999),
              ),
              child: Text(item.status, style: TextStyle(color: statusColor, fontWeight: FontWeight.w700)),
            ),
          ],
        ),
      ),
    );
  }
}
