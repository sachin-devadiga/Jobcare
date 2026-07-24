import 'dart:io';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import '../core/constants.dart';
import '../core/error.dart';
import '../models/voice_session_model.dart';

class VoiceService {
  final Dio _dio;
  final AudioRecorder _recorder = AudioRecorder();
  String? _recordingPath;

  VoiceService()
      : _dio = Dio(
          BaseOptions(
            baseUrl: AppConstants.sarvamBaseUrl,
            connectTimeout: AppConstants.apiTimeout,
            receiveTimeout: AppConstants.apiTimeout,
            headers: {
              'Content-Type': 'application/json',
              'api-subscription-key': AppConstants.sarvamApiKey,
            },
          ),
        );

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
      final response = await _dio.post(
        '/speech-to-text',
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
        ),
      );
      final data = response.data as Map<String, dynamic>;
      return data['transcript'] as String? ?? '';
    } on DioException catch (e) {
      throw handleException(e.error);
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
      final response = await _dio.post(
        '/text-to-speech',
        data: {
          'text': text,
          'language': language,
          'speaker': speaker,
          'pitch': pitch,
          'pace': pace,
          'loudness': loudness,
        },
      );
      final data = response.data as Map<String, dynamic>;
      return data['audio_url'] as String? ?? '';
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<VoiceCommandResult> processVoiceCommand({
    required String transcript,
  }) async {
    try {
      final response = await _dio.post(
        '/voice/process-command',
        data: {'transcript': transcript},
      );
      final data = response.data as Map<String, dynamic>;
      return VoiceCommandResult.fromJson(data);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<String> translateText({
    required String text,
    required String sourceLanguage,
    required String targetLanguage,
  }) async {
    try {
      final response = await _dio.post(
        '/translate',
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
    }
  }

  Future<List<String>> detectLanguage(String text) async {
    try {
      final response = await _dio.post(
        '/language-detection',
        data: {'text': text},
      );
      final data = response.data as Map<String, dynamic>;
      final languages = data['languages'] as List<dynamic>;
      return languages.map((e) => e as String).toList();
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<String> voiceSearch({
    required String query,
    String language = 'hi',
  }) async {
    try {
      final response = await _dio.post(
        '/voice/search',
        data: {
          'query': query,
          'language': language,
        },
      );
      final data = response.data as Map<String, dynamic>;
      return data['processed_query'] as String? ?? query;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<bool> checkHealth() async {
    try {
      final response = await _dio.get('/health');
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
    } catch (e) {
      throw handleException(e);
    }
  }

  void dispose() {
    _recorder.dispose();
  }
}
