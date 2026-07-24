import '../services/voice_service.dart';
import '../services/api_service.dart';
import '../models/voice_session_model.dart';

class VoiceRepository {
  final VoiceService _voiceService;
  final ApiService _apiService;

  VoiceRepository(this._voiceService, this._apiService);

  Future<bool> requestMicrophonePermission() async {
    return await _voiceService.requestMicrophonePermission();
  }

  Future<String> startRecording({String? fileName}) async {
    return await _voiceService.startRecording(fileName: fileName);
  }

  Future<String?> stopRecording() async {
    return await _voiceService.stopRecording();
  }

  Future<void> cancelRecording() async {
    await _voiceService.cancelRecording();
  }

  Future<String> speechToText({
    required String audioFilePath,
    String language = 'hi',
  }) async {
    return await _voiceService.speechToText(
      audioFilePath: audioFilePath,
      language: language,
    );
  }

  Future<String> textToSpeech({
    required String text,
    String language = 'hi',
  }) async {
    return await _voiceService.textToSpeech(
      text: text,
      language: language,
    );
  }

  Future<VoiceCommandResult> processVoiceCommand({
    required String transcript,
  }) async {
    return await _voiceService.processVoiceCommand(transcript: transcript);
  }

  Future<String> translateText({
    required String text,
    required String sourceLanguage,
    required String targetLanguage,
  }) async {
    return await _voiceService.translateText(
      text: text,
      sourceLanguage: sourceLanguage,
      targetLanguage: targetLanguage,
    );
  }

  Future<String> voiceSearch({
    required String query,
    String language = 'hi',
  }) async {
    return await _voiceService.voiceSearch(
      query: query,
      language: language,
    );
  }

  Future<String> generateVoiceResume({
    required String text,
    String language = 'hi',
  }) async {
    return await _voiceService.generateVoiceResume(
      text: text,
      language: language,
    );
  }

  Future<double> getAmplitude() async {
    final duration = await _voiceService.getAmplitude();
    return duration.inMilliseconds / 100.0;
  }

  Future<bool> checkHealth() async {
    return await _voiceService.checkHealth();
  }

  Future<Map<String, dynamic>> extractProfileFromTranscript({
    required String transcript,
    String language = 'hi',
  }) async {
    try {
      final response = await _apiService.post(
        '/voice/extract-profile/',
        data: {
          'transcript': transcript,
          'language': language,
        },
      );
      final data = response.data as Map<String, dynamic>;
      if (data['success'] == true && data['data'] != null) {
        return data['data'] as Map<String, dynamic>;
      }
      return {};
    } catch (e) {
      return {};
    }
  }
}
