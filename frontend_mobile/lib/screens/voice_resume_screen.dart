import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import '../theme/app_colors.dart';
import '../widgets/voice_ring.dart';
import '../providers/providers.dart';
import '../core/error.dart';
import '../core/localization.dart';

class VoiceResumeScreen extends ConsumerStatefulWidget {
  const VoiceResumeScreen({super.key});

  @override
  ConsumerState<VoiceResumeScreen> createState() => _VoiceResumeScreenState();
}

class _VoiceResumeScreenState extends ConsumerState<VoiceResumeScreen> {
  final AudioRecorder _recorder = AudioRecorder();
  bool _isRecording = false;
  bool _isProcessing = false;
  String? _transcript;
  Map<String, dynamic>? _extractedData;
  String? _voiceResumeFilePath;
  String? _voiceResumeUrl;
  Timer? _amplitudeTimer;

  @override
  void initState() {
    super.initState();
    _amplitudeTimer = Timer.periodic(const Duration(milliseconds: 100), (_) {
      if (mounted) {
        setState(() {});
      }
    });
  }

  @override
  void dispose() {
    _amplitudeTimer?.cancel();
    _recorder.dispose();
    super.dispose();
  }

  Future<void> _toggleRecording() async {
    if (_isProcessing) return;
    if (_isRecording) {
      await _stopAndProcess();
    } else {
      await _startRecording();
    }
    if (mounted) setState(() {});
  }

  Future<void> _startRecording() async {
    if (_isProcessing || _isRecording) return;
    final available = await _recorder.hasPermission();
    if (!available) {
      if (mounted) {
        setState(() {
          _isRecording = false;
          _isProcessing = false;
        });
      }
      return;
    }

    final directory = await getTemporaryDirectory();
    final filePath = '${directory.path}/voice_resume_${DateTime.now().millisecondsSinceEpoch}.m4a';

    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.aacLc,
        bitRate: 128000,
        sampleRate: 44100,
        numChannels: 1,
      ),
      path: filePath,
    );

    setState(() {
      _isRecording = true;
      _voiceResumeFilePath = filePath;
    });
  }

  Future<void> _stopAndProcess() async {
    await _recorder.stop();
    setState(() {
      _isRecording = false;
    });

    if (_voiceResumeFilePath == null) return;

    await _processVoiceResume(_voiceResumeFilePath!);
    setState(() {
      _voiceResumeFilePath = null;
    });
  }

  int _processId = 0;

  Future<void> _processVoiceResume(String audioFilePath) async {
    final myId = ++_processId;
    setState(() {
      _isProcessing = true;
      _transcript = null;
      _extractedData = null;
    });

    try {
      // Step 1: Convert speech to text using Sarvam AI
      final transcript = await ref
          .read(voiceServiceProvider)
          .speechToText(
        audioFilePath: audioFilePath,
        language: ref.read(languageProvider),
      );
      if (transcript.isEmpty) {
        throw const Failure(
          message:
              'No speech was recognized. Speak clearly and closer to the microphone, and avoid background noise.',
        );
      }

      if (myId != _processId) return;
      setState(() {
        _transcript = transcript;
      });

      // Step 2: Extract structured profile data from transcript using LLM
      final extractResponse = await ref
          .read(apiServiceProvider)
          .post('voice/extract-profile/', data: {
        'transcript': transcript,
        'language': ref.read(languageProvider),
      });
      final extractData = extractResponse.data as Map<String, dynamic>;

      if ((extractData['success'] ?? false) == false) {
        throw Exception('Profile extraction failed: ${extractData['message']}');
      }

      if (myId != _processId) return;
      final extractedData = extractData['data'] ?? extractData;
      setState(() {
        _extractedData = extractedData as Map<String, dynamic>;
      });

      // Step 3: Upload voice resume to get the URL
      final uploadResponse = await ref
          .read(profileServiceProvider)
          .uploadVoiceResume(audioFilePath);

      if (myId != _processId) return;
      setState(() {
        _voiceResumeUrl = uploadResponse;
      });

    } catch (e) {
      if (myId != _processId) return;
      debugPrint('Voice resume processing error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e is Failure ? e.message : 'Error processing voice: $e'),
          ),
        );
      }
    } finally {
      if (myId == _processId && mounted) {
        setState(() {
          _isProcessing = false;
        });
      }
    }
  }

  Widget _buildTranscriptCard(String lang) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(16)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            lang == 'hi' ? 'हमने यह सुना' : (lang == 'kn' ? 'ನಾವು ಕೇಳಿಸಿಕೊಂಡದ್ದು' : 'WHAT WE HEARD'),
            style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.2, color: Colors.grey)
          ),
          const SizedBox(height: 10),
          Text("\"$_transcript\"", style: const TextStyle(fontSize: 16, fontStyle: FontStyle.italic, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _buildExtractedDataCard(String lang) {
    final languages = (_extractedData?['languages'] as List<dynamic>?)
            ?.map((l) => l.toString())
            .join(', ') ??
        '';
    return Container(
      margin: const EdgeInsets.only(top: 20),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.primary.withOpacity(0.2), width: 1.5),
      ),
      child: Column(
        children: [
          _buildInfoRow(Icons.work_rounded,
              lang == 'hi' ? 'अनुभव' : (lang == 'kn' ? 'ಅನುಭವ' : 'Experience'),
              (_extractedData?['experience_years'] ?? 0).toString()),
          const Divider(height: 20),
          _buildInfoRow(Icons.person_pin_circle_rounded,
              lang == 'hi' ? 'प्रोफाइल' : (lang == 'kn' ? 'ಪ್ರೊಫೈಲ್' : 'Profile'),
              (_extractedData?['role'] ?? '').toString()),
          const Divider(height: 20),
          _buildInfoRow(Icons.language,
              lang == 'hi' ? 'भाषाएं' : (lang == 'kn' ? 'ಭಾಷೆ' : 'Languages'),
              languages),
        ],
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, color: AppColors.primary, size: 20),
        const SizedBox(width: 12),
        Text('$label: ', style: const TextStyle(fontWeight: FontWeight.bold)),
        Text(value),
      ],
    );
  }

  Widget _buildBottomButton(String lang) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 40),
      child: ElevatedButton(
        onPressed: _transcript != null && _extractedData != null
            ? () => _saveVoiceResume(lang)
            : _toggleRecording,
        style: ElevatedButton.styleFrom(
          backgroundColor: _transcript != null && _extractedData != null
              ? AppColors.primary
              : AppColors.secondary,
          foregroundColor: _transcript != null && _extractedData != null
              ? Colors.white
              : Colors.black,
          minimumSize: const Size(double.infinity, 60),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        child: Text(
          _transcript != null && _extractedData != null
              ? (lang == 'hi' ? 'प्रोफाइल में सेव करें' : (lang == 'kn' ? 'ಪ್ರೊಫೈಲ್‌ಗೆ ಉಳಿಸಿ' : 'SAVE TO PROFILE'))
                  : (_isRecording
                      ? (lang == 'hi' ? 'रिकॉर्डिंग रोकें' : (lang == 'kn' ? 'ರೆಕಾರ್ಡಿಂಗ್ ನಿಲ್ಲಿಸಿ' : 'STOP RECORDING'))
                  : (lang == 'hi' ? 'बोलना शुरू करें' : (lang == 'kn' ? 'ಮಾತನಾಡಲು ಪ್ರಾರಂಭಿಸಿ' : 'START SPEAKING'))),
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }

  Future<void> _saveVoiceResume(String lang) async {
    if (_extractedData == null || _voiceResumeUrl == null) return;

    try {
      final skills = (_extractedData?['skills'] as List<dynamic>?)
          ?.map((s) => s.toString())
          .toList();
      final languages = (_extractedData?['languages'] as List<dynamic>?)
          ?.map((l) => l.toString())
          .toList();
      final years = _extractedData?['experience_years'];
      await ref.read(profileServiceProvider).updateEmployeeProfile(
        skills: skills,
        languages: languages,
        experienceYears: years is num ? years.toInt() : null,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(lang == 'hi' ? 'वॉइस रिज्यूमे सहेजा गया' : 'Voice resume saved successfully')),
        );
        context.pop();
      }
    } catch (e) {
      debugPrint('Save voice resume error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e is Failure ? e.message : 'Error saving voice resume: $e'),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = ref.watch(languageProvider);
    
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(AppStrings.get('voice_resume', lang), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  const SizedBox(height: 20),
                  Text(
                    _isRecording
                        ? (lang == 'hi' ? 'आपकी बात सुन रहे हैं...' : (lang == 'kn' ? 'ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದ್ದೇನೆ...' : 'Listening to you...'))
                        : (lang == 'hi' ? 'बोलकर प्रोफाइल बनाएं' : (lang == 'kn' ? 'ಧ್ವನಿಯ ಮೂಲಕ ಪ್ರೊಫೈಲ್ ರಚಿಸಿ' : 'Build Profile with Voice')),
                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: AppColors.primary),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    lang == 'hi' 
                        ? 'अपने काम के अनुभव और कौशल के बारे में अपनी भाषा में बताएं।' 
                        : (lang == 'kn' ? 'ನಿಮ್ಮ ಕೆಲಸದ ಅನುಭವ ಮತ್ತು ಕೌಶಲ್ಯಗಳ ಬಗ್ಗೆ ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ತಿಳಿಸಿ.' : 'Tell us about your work experience and skills in your own language.'),
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 15, color: Colors.grey),
                  ),
                  const SizedBox(height: 60),
                  
                  // Central Voice UI
                  GestureDetector(
                    onTap: _toggleRecording,
                    child: VoiceRing(
                      size: 160,
                      state: _isRecording ? VoiceRingState.listening : VoiceRingState.idle,
                    ),
                  ),
                  
                  const SizedBox(height: 60),
                  
                  if (_transcript != null) _buildTranscriptCard(lang),
                  if (_extractedData != null) _buildExtractedDataCard(lang),
                ],
              ),
            ),
          ),
          _buildBottomButton(lang),
        ],
      ),
    );
  }
}