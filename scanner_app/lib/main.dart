import 'package:flutter/material.dart';
import 'models/scanner_models.dart';
import 'services/api_service.dart';
import 'theme/app_theme.dart';
import 'widgets/index_banner.dart';
import 'widgets/scanner_button_grid.dart';
import 'widgets/scanner_header.dart';
import 'widgets/stock_card.dart';
import 'widgets/summary_panel.dart';

void main() {
  runApp(const LeadingScannerApp());
}

class LeadingScannerApp extends StatelessWidget {
  const LeadingScannerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: '리딩 스캐너',
      theme: AppTheme.dark(),
      home: const LeadingScannerHomePage(),
    );
  }
}

class LeadingScannerHomePage extends StatefulWidget {
  const LeadingScannerHomePage({super.key});

  @override
  State<LeadingScannerHomePage> createState() => _LeadingScannerHomePageState();
}

class _LeadingScannerHomePageState extends State<LeadingScannerHomePage> {
  final ApiService api = ApiService('https://scanner-server-1.onrender.com');

  String selectedScanner = '93b';
  String selectedMarket = 'ALL';
  bool loading = true;
  ScannerResponse? scanner;
  Map<String, IndexInfo> indexes = {};

  @override
  void initState() {
    super.initState();
    loadAll();
  }

  Future<void> loadAll() async {
    setState(() => loading = true);
    try {
      final fetchedIndexes = await api.fetchIndexes();
      final fetchedScanner = await api.fetchScanner(selectedScanner, market: selectedMarket);
      setState(() {
        indexes = fetchedIndexes;
        scanner = fetchedScanner;
      });
    } finally {
      setState(() => loading = false);
    }
  }

  Future<void> selectScanner(String key) async {
    selectedScanner = key;
    await loadAll();
  }

  Future<void> selectMarket(String market) async {
    selectedMarket = market;
    await loadAll();
  }

  @override
  Widget build(BuildContext context) {
    final current = scanner;

    return Scaffold(
      appBar: AppBar(
        title: const Text('리딩 스캐너'),
      ),
      body: SafeArea(
        child: loading && current == null
            ? const Center(child: CircularProgressIndicator())
            : RefreshIndicator(
                onRefresh: loadAll,
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    IndexBanner(indexes: indexes),
                    const SizedBox(height: 16),
                    ScannerButtonGrid(
                      selectedKey: selectedScanner,
                      onSelect: selectScanner,
                    ),
                    const SizedBox(height: 16),
                    _marketTabs(),
                    const SizedBox(height: 16),
                    if (current != null) ...[
                      ScannerHeader(
                        title: current.meta.title,
                        updatedAt: current.updatedAt,
                      ),
                      const SizedBox(height: 16),
                      SummaryPanel(
                        title: '스캐너 설명',
                        body: current.meta.description,
                      ),
                      const SizedBox(height: 16),
                      SummaryPanel(
                        title: '집계 요약',
                        body: _buildSummaryText(current),
                      ),
                      const SizedBox(height: 16),
                      if (current.result.isEmpty)
                        Container(
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: AppColors.panel,
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: AppColors.line),
                          ),
                          child: const Text(
                            '표시할 결과가 없습니다.',
                            style: TextStyle(color: AppColors.muted),
                          ),
                        )
                      else
                        ...current.result.map((item) => StockCard(item: item)),
                    ],
                  ],
                ),
              ),
      ),
    );
  }

  Widget _marketTabs() {
    Widget chip(String key, String label) {
      final selected = key == selectedMarket;
      return Expanded(
        child: InkWell(
          onTap: () => selectMarket(key),
          child: Container(
            padding: const EdgeInsets.symmetric(vertical: 12),
            decoration: BoxDecoration(
              color: selected ? AppColors.blue.withOpacity(0.15) : AppColors.panel,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: selected ? AppColors.blue : AppColors.line),
            ),
            child: Center(
              child: Text(
                label,
                style: TextStyle(
                  color: selected ? AppColors.white : AppColors.muted,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ),
        ),
      );
    }

    return Row(
      children: [
        chip('ALL', '전체'),
        const SizedBox(width: 8),
        chip('KOSPI', '코스피'),
        const SizedBox(width: 8),
        chip('KOSDAQ', '코스닥'),
      ],
    );
  }

  String _buildSummaryText(ScannerResponse data) {
    if (data.summary != null && data.summary!.isNotEmpty) {
      final s = data.summary!;
      return [
        if (s['date'] != null) '기준일시: ${s['date']}',
        if (s['total_candidates'] != null) '전체 후보 수: ${s['total_candidates']}',
        if (s['pass_count'] != null) 'PASS 수: ${s['pass_count']}',
        if (s['watch_count'] != null) 'WATCH 수: ${s['watch_count']}',
        if (s['skip_count'] != null) 'SKIP 수: ${s['skip_count']}',
      ].join('\n');
    }

    if (data.strategy != null && data.strategy!.isNotEmpty) {
      final s = data.strategy!;
      return [
        if (s['date'] != null) '기준일시: ${s['date']}',
        if (s['market_mode'] != null) '시장 상태: ${s['market_mode']}',
        if (s['recommended_scanners'] != null) '추천 스캐너: ${(s['recommended_scanners'] as List).join(', ')}',
        if (s['position_size'] != null) '권장 비중: ${s['position_size']}',
        if (s['strategy_type'] != null) '매매 스타일: ${s['strategy_type']}',
        if (s['comment'] != null) '코멘트: ${s['comment']}',
      ].join('\n');
    }

    return data.meta.summaryText;
  }
}
