import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/chat_provider.dart';
import '../providers/providers.dart';
import '../theme/app_colors.dart';
import '../core/localization.dart';

class ChatScreen extends ConsumerStatefulWidget {
  final String conversationId;
  final String? otherName;

  const ChatScreen({super.key, required this.conversationId, this.otherName});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  String _voiceLang = 'hi';

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
      ref.read(chatProvider.notifier).loadMessages(widget.conversationId);
      _voiceLang = ref.read(languageProvider);
    });
  }

  void _showVoiceLangPicker(String lang) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              lang == 'hi' ? 'किस भाषा में बोलें?' : (lang == 'kn' ? 'ಯಾವ ಭಾಷೆಯಲ್ಲಿ ಮಾತನಾಡಬೇಕು?' : 'Speak in which language?'),
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              children: _voiceLanguages.map((l) => ChoiceChip(
                label: Text(l['name']!),
                selected: _voiceLang == l['code'],
                onSelected: (val) {
                  if (val) setState(() => _voiceLang = l['code']!);
                  Navigator.pop(context);
                },
              )).toList(),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final messages = chatState.messages[widget.conversationId] ?? [];
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(widget.otherName ?? 'Employer', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final isMe = messages[index].senderId == ref.read(authProvider).user?.id;
                return _MessageBubble(content: messages[index].content, isMe: isMe);
              },
            ),
          ),
          _buildInputArea(lang),
        ],
      ),
    );
  }

  Widget _buildInputArea(String lang) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 32),
      decoration: BoxDecoration(color: Colors.white, border: Border(top: BorderSide(color: Colors.grey.shade100))),
      child: Row(
        children: [
          GestureDetector(
            onTap: () => _showVoiceLangPicker(lang),
            child: Container(
              padding: const EdgeInsets.all(10),
              decoration: const BoxDecoration(color: AppColors.secondary, shape: BoxShape.circle),
              child: const Icon(Icons.mic_rounded, color: Colors.black, size: 24),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: _messageController,
              decoration: InputDecoration(
                hintText: lang == 'hi' ? 'मैसेज टाइप करें...' : (lang == 'kn' ? 'ಸಂದೇಶ ಟೈಪ್ ಮಾಡಿ...' : 'Type a message...'),
                filled: true,
                fillColor: AppColors.surface,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(24), borderSide: BorderSide.none),
              ),
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: const Icon(Icons.send_rounded, color: AppColors.primary),
            onPressed: () {
              if (_messageController.text.isNotEmpty) {
                ref.read(chatProvider.notifier).sendMessage(widget.conversationId, _messageController.text);
                _messageController.clear();
              }
            },
          ),
        ],
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final String content;
  final bool isMe;
  const _MessageBubble({required this.content, required this.isMe});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: isMe ? AppColors.primary : const Color(0xFFF1F5F9),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(content, style: TextStyle(color: isMe ? Colors.white : Colors.black, fontSize: 15)),
      ),
    );
  }
}
