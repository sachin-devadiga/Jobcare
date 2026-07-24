import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/voice_session_model.dart';
import '../repositories/voice_repository.dart';
import '../core/error.dart';

class VoiceState {
  final bool isListening;
  final bool isProcessing;
  final String? transcript;
  final String? responseText;
  final String? audioUrl;
  final VoiceCommandResult? lastCommand;
  final Failure? failure;
  final String? recordingPath;
  final double audioAmplitude;

  const VoiceState({
    this.isListening = false,
    this.isProcessing = false,
    this.transcript,
    this.responseText,
    this.audioUrl,
    this.lastCommand,
    this.failure,
    this.recordingPath,
    this.audioAmplitude = 0,
  });

  VoiceState copyWith({
    bool? isListening,
    bool? isProcessing,
    String? transcript,
    String? responseText,
    String? audioUrl,
    VoiceCommandResult? lastCommand,
    Failure? failure,
    String? recordingPath,
    double? audioAmplitude,
  }) {
    return VoiceState(
      isListening: isListening ?? this.isListening,
      isProcessing: isProcessing ?? this.isProcessing,
      transcript: transcript ?? this.transcript,
      responseText: responseText ?? this.responseText,
      audioUrl: audioUrl ?? this.audioUrl,
      lastCommand: lastCommand ?? this.lastCommand,
      failure: failure,
      recordingPath: recordingPath ?? this.recordingPath,
      audioAmplitude: audioAmplitude ?? this.audioAmplitude,
    );
  }
}

class VoiceNotifier extends StateNotifier<VoiceState> {
  final VoiceRepository _voiceRepository;

  VoiceNotifier(this._voiceRepository) : super(const VoiceState());

  Future<bool> requestPermission() async {
    return await _voiceRepository.requestMicrophonePermission();
  }

  Future<void> startRecording() async {
    final hasPermission = await requestPermission();
    if (!hasPermission) {
      state = state.copyWith(
        failure: const Failure(message: ErrorMessages.microphonePermissionDenied),
      );
      return;
    }

    try {
      final path = await _voiceRepository.startRecording();
      state = state.copyWith(
        isListening: true,
        recordingPath: path,
        failure: null,
      );
    } on Failure catch (e) {
      state = state.copyWith(failure: e);
    }
  }

  Future<String?> stopRecording() async {
    try {
      final path = await _voiceRepository.stopRecording();
      if (path != null) {
        state = state.copyWith(
          isListening: false,
          recordingPath: path,
        );
        return path;
      }
    } on Failure catch (e) {
      state = state.copyWith(isListening: false, failure: e);
    }
    state = state.copyWith(isListening: false);
    return null;
  }

  Future<void> cancelRecording() async {
    await _voiceRepository.cancelRecording();
    state = state.copyWith(isListening: false, recordingPath: null);
  }

  void setListening(bool value) {
    state = state.copyWith(isListening: value);
  }

  Future<void> processSpeech({
    required String audioFilePath,
    String language = 'hi',
  }) async {
    state = state.copyWith(isProcessing: true, failure: null);
    try {
      final transcript = await _voiceRepository.speechToText(
        audioFilePath: audioFilePath,
        language: language,
      );
      state = state.copyWith(
        transcript: transcript,
        isProcessing: false,
        isListening: false,
      );
      await processCommand(transcript: transcript);
    } on Failure catch (e) {
      state = state.copyWith(
        isProcessing: false,
        isListening: false,
        failure: e,
      );
    }
  }

  Future<void> processCommand({required String transcript}) async {
    state = state.copyWith(isProcessing: true);
    try {
      final result = await _voiceRepository.processVoiceCommand(
        transcript: transcript,
      );
      String? audioUrl;
      if (result.responseText != null) {
        try {
          audioUrl = await _voiceRepository.textToSpeech(
            text: result.responseText!,
          );
        } catch (_) {}
      }
      state = state.copyWith(
        responseText: result.responseText,
        audioUrl: audioUrl,
        lastCommand: result,
        isProcessing: false,
      );
    } on Failure catch (e) {
      state = state.copyWith(
        isProcessing: false,
        failure: e,
      );
    }
  }

  Future<String?> textToSpeech(String text, {String language = 'hi'}) async {
    try {
      final url = await _voiceRepository.textToSpeech(
        text: text,
        language: language,
      );
      state = state.copyWith(audioUrl: url);
      return url;
    } on Failure catch (e) {
      state = state.copyWith(failure: e);
      return null;
    }
  }

  Future<String?> voiceSearch(String query, {String language = 'hi'}) async {
    try {
      final processed = await _voiceRepository.voiceSearch(
        query: query,
        language: language,
      );
      return processed;
    } on Failure catch (e) {
      state = state.copyWith(failure: e);
      return null;
    }
  }

  void checkAmplitude() {
    _voiceRepository.getAmplitude().then((value) {
      state = state.copyWith(audioAmplitude: value);
    });
  }

  void setTranscript(String transcript) {
    state = state.copyWith(transcript: transcript);
  }

  void clearSession() {
    state = const VoiceState();
  }

  void clearFailure() {
    state = state.copyWith(failure: null);
  }
}
