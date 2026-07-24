import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/storage_service.dart';

class LanguageNotifier extends StateNotifier<String> {
  final StorageService _storageService;

  LanguageNotifier(this._storageService) : super('en') {
    _loadLanguage();
  }

  Future<void> _loadLanguage() async {
    final lang = await _storageService.getLanguage();
    if (lang != null && lang.isNotEmpty) {
      state = lang;
    }
  }

  Future<void> setLanguage(String code) async {
    state = code;
    await _storageService.setLanguage(code);
  }
}
