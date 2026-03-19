import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Scanner App',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(),
      home: const ScannerHome(),
    );
  }
}

class ScannerHome extends StatefulWidget {
  const ScannerHome({super.key});

  @override
  State<ScannerHome> createState() => _ScannerHomeState();
}

class _ScannerHomeState extends State<ScannerHome> {
  List scanResults = [];
  String titleText = '결과 없음';
  bool isLoading = false;

  Future<void> fetchScan(String url, String title) async {
    setState(() {
      isLoading = true;
      titleText = '$title 불러오는 중...';
      scanResults = [];
    });

    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        setState(() {
          titleText = title;
          scanResults = data["result"] ?? [];
        });
      } else {
        setState(() {
          titleText = '오류 발생: ${response.statusCode}';
          scanResults = [];
        });
      }
    } catch (e) {
      setState(() {
        titleText = '서버 연결 실패: $e';
        scanResults = [];
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  Widget scannerButton(String text, VoidCallback onPressed) {
    return SizedBox(
      width: 240,
      child: ElevatedButton(
        onPressed: onPressed,
        child: Text(text),
      ),
    );
  }

  Widget resultCard(Map item) {
    final status = item["status"]?.toString() ?? "-";

    Color badgeColor;
    if (status == "PASS") {
      badgeColor = Colors.green;
    } else if (status == "WATCH") {
      badgeColor = Colors.orange;
    } else {
      badgeColor = Colors.grey;
    }

    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: ListTile(
        title: Text('${item["name"] ?? "-"} (${item["code"] ?? "-"})'),
        subtitle: Text(
          '상태: ${item["status"] ?? "-"}'
          '${item["rr"] != null ? " / RR: ${item["rr"]}" : ""}'
          '${item["entry1"] != null ? " / 진입1: ${item["entry1"]}" : ""}'
          '${item["stop"] != null ? " / 손절: ${item["stop"]}" : ""}'
          '${item["target"] != null ? " / 목표: ${item["target"]}" : ""}',
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: badgeColor,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            status,
            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📊 스캐너 홈'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          const SizedBox(height: 24),

          scannerButton(
            '5.0 스캐너',
            () => fetchScan('http://localhost:8000/scan/50', '5.0 스캐너 결과'),
          ),
          const SizedBox(height: 12),

          scannerButton(
            '5.1 스캐너',
            () => fetchScan('http://localhost:8000/scan/51', '5.1 스캐너 결과'),
          ),
          const SizedBox(height: 12),

          scannerButton(
            '6.0 스캐너',
            () => fetchScan('http://localhost:8000/scan/60', '6.0 스캐너 결과'),
          ),
          const SizedBox(height: 12),

          scannerButton(
            '7.0 스캐너',
            () => fetchScan('http://localhost:8000/scan/70', '7.0 스캐너 결과'),
          ),
          const SizedBox(height: 12),

          scannerButton(
            '9.2 전략',
            () => fetchScan('http://localhost:8000/scan/92', '9.2 전략 결과'),
          ),
          const SizedBox(height: 12),

          scannerButton(
            '🚀 9.3B 실행',
            () => fetchScan('http://localhost:8000/scan/93b', '9.3B 결과'),
          ),

          const SizedBox(height: 24),
          Text(
            titleText,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),

          if (isLoading)
            const Padding(
              padding: EdgeInsets.all(20),
              child: CircularProgressIndicator(),
            ),

          if (!isLoading)
            Expanded(
              child: scanResults.isEmpty
                  ? const Center(child: Text('표시할 데이터가 없습니다'))
                  : ListView.builder(
                      itemCount: scanResults.length,
                      itemBuilder: (context, index) {
                        return resultCard(scanResults[index]);
                      },
                    ),
            ),
        ],
      ),
    );
  }
}