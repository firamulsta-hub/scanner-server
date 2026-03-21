import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/scanner_models.dart';

class ApiService {
  final String baseUrl;

  ApiService(this.baseUrl);

  Future<Map<String, IndexInfo>> fetchIndexes() async {
    final response = await http.get(Uri.parse('$baseUrl/indexes'));
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return data.map((key, value) => MapEntry(key, IndexInfo.fromJson(value)));
  }

  Future<ScannerResponse> fetchScanner(String scannerKey, {String market = 'ALL'}) async {
    final query = market == 'ALL' ? '' : '?market=$market';
    final response = await http.get(Uri.parse('$baseUrl/scan/$scannerKey$query'));
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return ScannerResponse.fromJson(data);
  }
}
