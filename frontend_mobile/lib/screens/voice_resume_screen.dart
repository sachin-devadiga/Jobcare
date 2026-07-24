import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../theme/app_colors.dart';
import '../widgets/voice_ring.dart';
import '../providers/providers.dart';
import '../core/localization.dart';

class VoiceResumeScreen extends ConsumerStatefulWidget {
  const VoiceResumeScreen({super.key});

  @override
  ConsumerState<VoiceResumeScreen> createState() => _VoiceResumeScreenState();
}

class _VoiceResumeScreenState extends ConsumerState<VoiceResumeScreen> {
  bool _isRecording = false;
  bool _isProcessing = false;
  String? _transcript;
  Map<String, dynamic>? _extractedData;

  void _toggleRecording() async {
    if (_isRecording) {
      setState(() {
        _isRecording = false;
        _isProcessing = true;
      });
      // Simulate processing delay
      await Future.delayed(const Duration(seconds: 2));
      if (mounted) {
        setState(() {
          _isProcessing = false;
          _transcript = "I have 5 years of experience in heavy vehicle driving and I know Bangalore routes well.";
          _extractedData = {"experience": "5 Years", "role": "Driver", "location": "Bangalore"};
        });
      }
    } else {
      setState(() {
        _isRecording = true;
        _transcript = null;
        _extractedData = null;
      });
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
                      : (lang == 'hi' ? 'बोलकर प्रोफाइल बनाएं' : (lang == 'kn' ? 'ಧ್ವನಿ ಮೂಲಕ ಪ್ರೊಫೈಲ್ ನಿರ್ಮಿಸಿ' : 'Build Profile with Voice')),
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
                      state: _isProcessing ? VoiceRingState.processing : (_isRecording ? VoiceRingState.listening : VoiceRingState.idle),
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
          _buildInfoRow(Icons.work_rounded, lang == 'hi' ? 'अनुभव' : (lang == 'kn' ? 'ಅನುಭವ' : 'Experience'), _extractedData!['experience']),
          const Divider(height: 20),
          _buildInfoRow(Icons.person_pin_circle_rounded, lang == 'hi' ? 'प्रोफाइल' : (lang == 'kn' ? 'ಪ್ರೊಫೈಲ್' : 'Profile'), _extractedData!['role']),
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
        onPressed: _transcript != null ? () => Navigator.of(context).pop() : _toggleRecording,
        style: ElevatedButton.styleFrom(
          backgroundColor: _transcript != null ? AppColors.primary : AppColors.secondary,
          foregroundColor: _transcript != null ? Colors.white : Colors.black,
          minimumSize: const Size(double.infinity, 60),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
        child: Text(
          _transcript != null 
            ? (lang == 'hi' ? 'प्रोफाइल में सेव करें' : (lang == 'kn' ? 'ಪ್ರೊಫೈಲ್‌ಗೆ ಉಳಿಸಿ' : 'SAVE TO PROFILE'))
            : (_isRecording 
                ? (lang == 'hi' ? 'रिकॉर्डिंग रोकें' : (lang == 'kn' ? 'ರೆಕಾರ್ಡಿಂಗ್ ನಿಲ್ಲಿಸಿ' : 'STOP RECORDING')) 
                : (lang == 'hi' ? 'बोलना शुरू करें' : (lang == 'kn' ? 'ಮಾತನಾಡಲು ಪ್ರಾರಂಭಿಸಿ' : 'START SPEAKING'))), 
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      ),
    );
  }
}
