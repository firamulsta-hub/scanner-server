import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/scanner_models.dart';

class ApiService {
  final String baseUrl;

  ApiService(this.baseUrl);

  Map<String, IndexInfo>? _cachedIndexes;
  final Map<String, ScannerResponse> _cachedScanners = {};

  Future<Map<String, IndexInfo>> fetchIndexes() async {
    if (_cachedIndexes != null) return _cachedIndexes!;

    final response = await http.get(Uri.parse('$baseUrl/indexes'));
    final data = jsonDecode(response.body) as Map<String, dynamic>;

    _cachedIndexes =
        data.map((key, value) => MapEntry(key, IndexInfo.fromJson(value)));

    return _cachedIndexes!;
  }

  Future<ScannerResponse> fetchScanner(String scannerKey,
      {String market = 'ALL'}) async {
    final cacheKey = '$scannerKey::$market';
    if (_cachedScanners[cacheKey] != null) {
      return _cachedScanners[cacheKey]!;
    }

    final query = market == 'ALL' ? '' : '?market=$market';
    final response =
        await http.get(Uri.parse('$baseUrl/scan/$scannerKey$query'));

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final result = ScannerResponse.fromJson(data);

    _cachedScanners[cacheKey] = result;
    return result;
  }
}
