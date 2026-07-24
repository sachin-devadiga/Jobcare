import 'package:permission_handler/permission_handler.dart';

class AppPermissionHandler {
  static Future<bool> requestLocationPermission() async {
    final status = await Permission.location.request();
    return status.isGranted;
  }

  static Future<bool> requestCameraPermission() async {
    final status = await Permission.camera.request();
    return status.isGranted;
  }

  static Future<bool> requestMicrophonePermission() async {
    final status = await Permission.microphone.request();
    return status.isGranted;
  }

  static Future<bool> requestStoragePermission() async {
    final status = await Permission.storage.request();
    return status.isGranted;
  }

  static Future<bool> requestNotificationPermission() async {
    final status = await Permission.notification.request();
    return status.isGranted;
  }

  static Future<bool> requestPhotosPermission() async {
    if (await Permission.photos.isGranted) return true;
    final status = await Permission.photos.request();
    return status.isGranted;
  }

  static Future<bool> requestMediaLibraryPermission() async {
    if (await Permission.mediaLibrary.isGranted) return true;
    final status = await Permission.mediaLibrary.request();
    return status.isGranted;
  }

  static Future<bool> requestPhonePermission() async {
    final status = await Permission.phone.request();
    return status.isGranted;
  }

  static Future<bool> isLocationGranted() async {
    return await Permission.location.isGranted;
  }

  static Future<bool> isMicrophoneGranted() async {
    return await Permission.microphone.isGranted;
  }

  static Future<bool> isCameraGranted() async {
    return await Permission.camera.isGranted;
  }

  static Future<bool> isStorageGranted() async {
    return await Permission.storage.isGranted;
  }

  static Future<Map<Permission, PermissionStatus>> requestMultiple([
    List<Permission> permissions = const [],
  ]) async {
    return await permissions.request();
  }

  static Future<bool> openSettings() async {
    return await openAppSettings();
  }
}
