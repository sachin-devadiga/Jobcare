import 'dart:io';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import '../core/error.dart';
import '../models/voice_session_model.dart';
import 'api_service.dart';

class VoiceService {
  final ApiService _apiService;
  final AudioRecorder _recorder = AudioRecorder();
  String? _recordingPath;

  VoiceService(this._apiService);

  Future<bool> requestMicrophonePermission() async {
    final available = await _recorder.hasPermission();
    return available;
  }

  Future<String> startRecording({String? fileName}) async {
    final directory = await getTemporaryDirectory();
    final filePath = '${directory.path}/${fileName ?? 'voice_${DateTime.now().millisecondsSinceEpoch}.m4a'}';
    _recordingPath = filePath;

    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.aacLc,
        bitRate: 128000,
        sampleRate: 44100,
        numChannels: 1,
      ),
      path: filePath,
    );

    return filePath;
  }

  Future<String?> stopRecording() async {
    final path = _recordingPath;
    _recordingPath = null;
    try {
      await _recorder.stop();
      return path;
    } catch (e) {
      return null;
    }
  }

  Future<void> cancelRecording() async {
    _recordingPath = null;
    try {
      await _recorder.cancel();
    } catch (_) {}
  }

  Future<Duration> getAmplitude() async {
    try {
      final recording = await _recorder.isRecording();
      if (recording) {
        final amplitude = await _recorder.getAmplitude();
        return Duration(milliseconds: (amplitude.current * 100).toInt());
      }
    } catch (_) {}
    return Duration.zero;
  }

  Future<bool> isRecording() async {
    return await _recorder.isRecording();
  }

  Future<String> speechToText({
    required String audioFilePath,
    String language = 'hi',
    bool withDiarization = false,
  }) async {
    try {
      final file = File(audioFilePath);
      if (!await file.exists()) {
        throw const Failure(message: 'Audio file not found');
      }

      final formData = FormData.fromMap({
        'audio': await MultipartFile.fromFile(
          audioFilePath,
          filename: 'audio.m4a',
        ),
        'language': language,
        'with_diarization': withDiarization,
      });
      final response = await _apiService.upload(
        'voice/speech-to-text/',
        data: formData,
      );
      final data = response.data as Map<String, dynamic>;
      final payload = data['data'] as Map<String, dynamic>?;
      return payload?['text'] as String? ?? '';
    } on DioException catch (e) {
      throw handleException(e.error);
    } catch (e) {
      throw handleException(e);
    }
  }

  Future<String> textToSpeech({
    required String text,
    String language = 'hi',
    String speaker = 'default',
    double pitch = 1.0,
    double pace = 1.0,
    double loudness = 1.0,
  }) async {
    try {
      final response = await _apiService.post(
        'voice/text-to-speech/',
        data: {
          'text': text,
          'language': language,
          'voice': speaker,
          'pace': pace,
        },
      );
      final data = response.data as Map<String, dynamic>;
      final payload = data['data'] as Map<String, dynamic>?;
      return payload?['audio_url'] as String? ?? '';
    } on DioException catch (e) {
      throw handleException(e.error);
    } catch (e) {
      throw handleException(e);
    }
  }

  Future<VoiceCommandResult> processVoiceCommand({
    required String transcript,
  }) async {
    try {
      final response = await _apiService.post(
        'voice/navigate/',
        data: {'query': transcript},
      );
      final data = response.data as Map<String, dynamic>;
      return VoiceCommandResult.fromJson(
        data['data'] as Map<String, dynamic>? ?? data,
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    } catch (e) {
      throw handleException(e);
    }
  }

  Future<String> translateText({
    required String text,
    required String sourceLanguage,
    required String targetLanguage,
  }) async {
    try {
      final response = await _apiService.post(
        'voice/translate/',
        data: {
          'text': text,
          'source_language': sourceLanguage,
          'target_language': targetLanguage,
        },
      );
      final data = response.data as Map<String, dynamic>;
      return data['translated_text'] as String? ?? '';
    } on DioException catch (e) {
      throw handleException(e.error);
    } catch (e) {
      throw handleException(e);
    }
  }

  Future<List<String>> detectLanguage(String text) async {
    try {
      final response = await _apiService.post(
        'voice/language-detection/',
        data: {'text': text},
      );
      final data = response.data as Map<String, dynamic>;
      final languages = data['languages'] as List<dynamic>;
      return languages.map((e) => e as String).toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    } catch (e) {
      throw handleException(e);
    }
  }

  Future<String> voiceSearch({
    required String query,
    String language = 'hi',
  }) async {
    try {
      final response = await _apiService.post(
        'voice/search/',
        data: {
          'query': query,
          'language': language,
        },
      );
      final data = response.data as Map<String, dynamic>;
      final payload = data['data'] as Map<String, dynamic>?;
      return payload?['query'] as String? ?? query;
    } on DioException catch (e) {
      throw handleException(e.error);
    } catch (e) {
      throw handleException(e);
    }
  }

  Future<bool> checkHealth() async {
    try {
      final response = await _apiService.get('health/');
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<String> generateVoiceResume({
    required String text,
    String language = 'hi',
  }) async {
    return await textToSpeech(
      text: text,
      language: language,
      speaker: 'default',
    );
  }

  static Future<void> saveAudioToFile({
    required String audioUrl,
    required String filePath,
  }) async {
    try {
      final response = await Dio().download(audioUrl, filePath);
      if (response.statusCode != 200) {
        throw const Failure(message: 'Failed to download audio file');
      }
    } on DioException catch (e) {
      throw handleException(e.error);
    } catch (e) {
      throw handleException(e);
    }
  }

  void dispose() {
    _recorder.dispose();
  }
}
