import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:audioplayers/audioplayers.dart';
import '../providers/providers.dart';
import '../theme/app_colors.dart';
import '../widgets/voice_ring.dart';
import '../routes/route_names.dart';
import '../core/localization.dart';

class VoiceAssistantScreen extends ConsumerStatefulWidget {
  const VoiceAssistantScreen({super.key});

  @override
  ConsumerState<VoiceAssistantScreen> createState() => _VoiceAssistantScreenState();
}

class _VoiceAssistantScreenState extends ConsumerState<VoiceAssistantScreen> {
  final AudioPlayer _audioPlayer = AudioPlayer();
  bool _isSpeaking = false;
  String _speakingLanguage = 'hi'; 

  final List<Map<String, String>> _voiceLanguages = [
    {'code': 'hi', 'name': 'Hindi'},
    {'code': 'en', 'name': 'English'},
    {'code': 'kn', 'name': 'Kannada'},
    {'code': 'ta', 'name': 'Tamil'},
    {'code': 'te', 'name': 'Telugu'},
    {'code': 'ml', 'name': 'Malayalam'},
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final appLang = ref.read(languageProvider);
      if (_voiceLanguages.any((l) => l['code'] == appLang)) {
        setState(() => _speakingLanguage = appLang);
      }
      _startAssistant();
    });
    
    _audioPlayer.onPlayerStateChanged.listen((state) {
      if (mounted) setState(() => _isSpeaking = state == PlayerState.playing);
    });
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _startAssistant() async {
    final notifier = ref.read(voiceProvider.notifier);
    await notifier.startRecording();
  }

  void _handleStop() async {
    final notifier = ref.read(voiceProvider.notifier);
    final path = await notifier.stopRecording();
    if (path != null) {
      await notifier.processSpeech(audioFilePath: path, language: _speakingLanguage);
      final state = ref.read(voiceProvider);
      if (state.audioUrl != null) {
        await _audioPlayer.play(UrlSource(state.audioUrl!));
      }
      if (state.lastCommand != null) {
        final action = state.lastCommand!.action;
        final params = state.lastCommand!.parsedData;
        if (action == 'navigate') {
          final target = params?['target']?.toString().toLowerCase();
          if (target == 'profile') context.push(RouteNames.profile);
          else if (target == 'jobs') context.push(RouteNames.jobs);
        } else if (action == 'search' && params?['query'] != null) {
          context.push('${RouteNames.searchResults}?query=${params!['query']}');
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final voiceState = ref.watch(voiceProvider);
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: AppColors.primary,
      body: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                IconButton(
                  icon: const Icon(Icons.close_rounded, color: Colors.white, size: 30),
                  onPressed: () => context.pop(),
                ),
                Text(AppStrings.get('voice_assistant', lang), 
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, letterSpacing: 1.2)),
                IconButton(
                  icon: const Icon(Icons.help_outline_rounded, color: Colors.white70, size: 28),
                  onPressed: () => context.push(RouteNames.voiceHelp),
                ),
              ],
            ),
            const Spacer(),
            GestureDetector(
              onTap: voiceState.isListening ? _handleStop : _startAssistant,
              child: VoiceRing(
                size: 180,
                state: _isSpeaking 
                    ? VoiceRingState.processing 
                    : (voiceState.isListening ? VoiceRingState.listening : VoiceRingState.idle),
              ),
            ),
            const SizedBox(height: 48),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 40),
              child: Text(
                voiceState.isProcessing 
                    ? AppStrings.get('processing', lang) 
                    : (voiceState.responseText ?? voiceState.transcript ?? AppStrings.get('hero_subtitle', lang)),
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
              ),
            ),
            const Spacer(),
            Text(lang == 'hi' ? 'बोलने की भाषा' : (lang == 'kn' ? 'ಮಾತನಾಡುವ ಭಾಷೆ' : 'SPEAKING IN'), 
              style: const TextStyle(color: Colors.white70, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1)),
            const SizedBox(height: 12),
            SizedBox(
              height: 44,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 20),
                itemCount: _voiceLanguages.length,
                itemBuilder: (context, index) {
                  final vLang = _voiceLanguages[index];
                  final isSelected = _speakingLanguage == vLang['code'];
                  return Padding(
                    padding: const EdgeInsets.only(right: 10),
                    child: ChoiceChip(
                      label: Text(vLang['name']!),
                      selected: isSelected,
                      onSelected: (val) {
                        if (val) setState(() => _speakingLanguage = vLang['code']!);
                      },
                      backgroundColor: Colors.white.withOpacity(0.1),
                      selectedColor: AppColors.secondary,
                      labelStyle: TextStyle(
                        color: isSelected ? Colors.black : Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      showCheckmark: false,
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}
