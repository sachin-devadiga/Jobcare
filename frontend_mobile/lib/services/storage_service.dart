import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class StorageService {
  final FlutterSecureStorage _storage;
  static const _prefix = 'jobcare_';

  const StorageService(this._storage);

  Future<void> write(String key, String value) async {
    await _storage.write(key: '$_prefix$key', value: value);
  }

  Future<String?> read(String key) async {
    return await _storage.read(key: '$_prefix$key');
  }

  Future<void> delete(String key) async {
    await _storage.delete(key: '$_prefix$key');
  }

  Future<bool> contains(String key) async {
    final value = await _storage.containsKey(key: '$_prefix$key');
    return value;
  }

  Future<void> clear() async {
    await _storage.deleteAll();
  }

  Future<void> writeToken(String token) async {
    await write('auth_token', token);
  }

  Future<String?> readToken() async {
    return await read('auth_token');
  }

  Future<void> deleteToken() async {
    await delete('auth_token');
  }

  Future<void> writeRefreshToken(String token) async {
    await write('refresh_token', token);
  }

  Future<String?> readRefreshToken() async {
    return await read('refresh_token');
  }

  Future<void> deleteRefreshToken() async {
    await delete('refresh_token');
  }

  Future<void> saveUserData(String userData) async {
    await write('user_data', userData);
  }

  Future<String?> readUserData() async {
    return await read('user_data');
  }

  Future<void> clearUserData() async {
    await delete('user_data');
  }

  Future<void> setThemeMode(String mode) async {
    await write('theme_mode', mode);
  }

  Future<String?> getThemeMode() async {
    return await read('theme_mode');
  }

  Future<void> setLanguage(String language) async {
    await write('language', language);
  }

  Future<String?> getLanguage() async {
    return await read('language');
  }

  Future<void> setOnboardingSeen() async {
    await write('onboarding_seen', 'true');
  }

  Future<bool> isOnboardingSeen() async {
    final value = await read('onboarding_seen');
    return value == 'true';
  }

  Future<void> saveFcmToken(String token) async {
    await write('fcm_token', token);
  }

  Future<String?> readFcmToken() async {
    return await read('fcm_token');
  }

  Future<void> saveSavedJobs(List<String> jobIds) async {
    await write('saved_jobs', jobIds.join(','));
  }

  Future<List<String>> readSavedJobs() async {
    final value = await read('saved_jobs');
    if (value == null || value.isEmpty) return [];
    return value.split(',').where((id) => id.isNotEmpty).toList();
  }

  Future<void> addSavedJob(String jobId) async {
    final jobs = await readSavedJobs();
    if (!jobs.contains(jobId)) {
      jobs.add(jobId);
      await saveSavedJobs(jobs);
    }
  }

  Future<void> removeSavedJob(String jobId) async {
    final jobs = await readSavedJobs();
    jobs.remove(jobId);
    await saveSavedJobs(jobs);
  }

  Future<bool> isJobSaved(String jobId) async {
    final jobs = await readSavedJobs();
    return jobs.contains(jobId);
  }

  Future<void> saveRecentSearch(String query) async {
    final searches = await readRecentSearches();
    searches.remove(query);
    searches.insert(0, query);
    if (searches.length > 10) {
      searches.removeLast();
    }
    await write('recent_searches', searches.join('|||'));
  }

  Future<List<String>> readRecentSearches() async {
    final value = await read('recent_searches');
    if (value == null || value.isEmpty) return [];
    return value.split('|||');
  }

  Future<void> clearRecentSearches() async {
    await delete('recent_searches');
  }

  Future<void> setNotificationSetting(String key, bool value) async {
    final settings = await read('notification_settings');
    final map = settings != null
        ? Map<String, dynamic>.from(
            String.fromCharCodes(settings.codeUnits) as Map)
        : <String, dynamic>{};
    map[key] = value;
    await write('notification_settings', map.toString());
  }

  Future<Map<String, bool>> getNotificationSettings() async {
    final value = await read('notification_settings');
    if (value == null) return {};
    try {
      return Map<String, bool>.from(
          String.fromCharCodes(value.codeUnits) as Map);
    } catch (_) {
      return {};
    }
  }
}
