class IndexInfo {
  final String name;
  final double value;
  final double changePercent;

  IndexInfo({
    required this.name,
    required this.value,
    required this.changePercent,
  });

  factory IndexInfo.fromJson(Map<String, dynamic> json) {
    return IndexInfo(
      name: json['name'] ?? '',
      value: (json['value'] ?? 0).toDouble(),
      changePercent: (json['change_percent'] ?? 0).toDouble(),
    );
  }
}

class ScannerMeta {
  final String key;
  final String title;
  final String description;
  final String updatedAt;
  final String summaryText;

  ScannerMeta({
    required this.key,
    required this.title,
    required this.description,
    required this.updatedAt,
    required this.summaryText,
  });

  factory ScannerMeta.fromJson(Map<String, dynamic> json) {
    return ScannerMeta(
      key: json['key'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      updatedAt: json['updated_at'] ?? '',
      summaryText: json['summary_text'] ?? '',
    );
  }
}

class StockItem {
  final String code;
  final String name;
  final String status;
  final String market;
  final double currentPrice;
  final double changePercent;
  final String scannerType;
  final double? entry1;
  final double? stop;
  final double? target1;
  final double? rr;
  final String? comment;

  StockItem({
    required this.code,
    required this.name,
    required this.status,
    required this.market,
    required this.currentPrice,
    required this.changePercent,
    required this.scannerType,
    this.entry1,
    this.stop,
    this.target1,
    this.rr,
    this.comment,
  });

  factory StockItem.fromJson(Map<String, dynamic> json) {
    String market = json['market'] ?? 'UNKNOWN';

    if (market == 'UNKNOWN') {
      final code = (json['code'] ?? '').toString();
      if (code.startsWith('0')) {
        market = 'KOSPI';
      } else {
        market = 'KOSDAQ';
      }
    }

    return StockItem(
      code: json['code'] ?? '',
      name: json['name'] ?? '',
      status: json['status'] ?? '',
      market: market,
      currentPrice: (json['current_price'] ?? 0).toDouble(),
      changePercent: (json['change_percent'] ?? 0).toDouble(),
      scannerType: json['scanner_type'] ?? '',
      entry1: json['entry1'] != null ? (json['entry1'] as num).toDouble() : null,
      stop: json['stop'] != null ? (json['stop'] as num).toDouble() : null,
      target1: json['target1'] != null ? (json['target1'] as num).toDouble() : null,
      rr: json['rr'] != null ? (json['rr'] as num).toDouble() : null,
      comment: json['comment'],
    );
  }
}

class ScannerResponse {
  final ScannerMeta meta;
  final List<StockItem> result;
  final Map<String, dynamic>? summary;
  final Map<String, dynamic>? strategy;
  final String updatedAt;

  ScannerResponse({
    required this.meta,
    required this.result,
    required this.summary,
    required this.strategy,
    required this.updatedAt,
  });

  factory ScannerResponse.fromJson(Map<String, dynamic> json) {
    return ScannerResponse(
      meta: ScannerMeta.fromJson(json['meta'] ?? {}),
      result: ((json['result'] ?? []) as List).map((e) => StockItem.fromJson(e)).toList(),
      summary: json['summary'] as Map<String, dynamic>?,
      strategy: json['strategy'] as Map<String, dynamic>?,
      updatedAt: json['updated_at'] ?? '',
    );
  }
}
