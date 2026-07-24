import 'package:image_picker/image_picker.dart';

class ImagePickerHelper {
  final ImagePicker _picker = ImagePicker();

  Future<XFile?> pickFromGallery({
    double maxWidth = 1024,
    double maxHeight = 1024,
    int imageQuality = 80,
  }) async {
    try {
      final file = await _picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: maxWidth,
        maxHeight: maxHeight,
        imageQuality: imageQuality,
      );
      return file;
    } catch (_) {
      return null;
    }
  }

  Future<XFile?> pickFromCamera({
    double maxWidth = 1024,
    double maxHeight = 1024,
    int imageQuality = 80,
  }) async {
    try {
      final file = await _picker.pickImage(
        source: ImageSource.camera,
        maxWidth: maxWidth,
        maxHeight: maxHeight,
        imageQuality: imageQuality,
      );
      return file;
    } catch (_) {
      return null;
    }
  }

  Future<XFile?> pickVideoFromGallery() async {
    try {
      final file = await _picker.pickVideo(source: ImageSource.gallery);
      return file;
    } catch (_) {
      return null;
    }
  }

  Future<List<XFile>> pickMultipleImages({
    double maxWidth = 1024,
    double maxHeight = 1024,
    int imageQuality = 80,
  }) async {
    try {
      final files = await _picker.pickMultiImage(
        maxWidth: maxWidth,
        maxHeight: maxHeight,
        imageQuality: imageQuality,
      );
      return files;
    } catch (_) {
      return [];
    }
  }

  Future<XFile?> pickAudio() async {
    try {
      final file = await _picker.pickMedia();
      return file;
    } catch (_) {
      return null;
    }
  }

  Future<XFile?> pickFile({List<String>? allowedExtensions}) async {
    try {
      final file = await _picker.pickMedia();
      return file;
    } catch (_) {
      return null;
    }
  }

  void clearCache() {
    // ImagePicker does not expose a clear method; cache cleared via OS
  }
}
