import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/providers.dart';
import '../routes/route_names.dart';
import '../theme/app_colors.dart';
import '../theme/app_text_styles.dart';
import '../widgets/shimmer_loading.dart';
import '../widgets/empty_state.dart';
import '../core/utils.dart';

class _Conversation {
  final String id;
  final String name;
  final String? avatarUrl;
  final String lastMessage;
  final DateTime lastMessageTime;
  final int unreadCount;
  final bool isOnline;
  final bool isAiAssistant;

  const _Conversation({
    required this.id,
    required this.name,
    this.avatarUrl,
    required this.lastMessage,
    required this.lastMessageTime,
    this.unreadCount = 0,
    this.isOnline = false,
    this.isAiAssistant = false,
  });
}

class MessagesScreen extends ConsumerStatefulWidget {
  const MessagesScreen({super.key});

  @override
  ConsumerState<MessagesScreen> createState() => _MessagesScreenState();
}

class _MessagesScreenState extends ConsumerState<MessagesScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<_Conversation> _conversations = [];
  List<_Conversation> _filteredConversations = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadConversations();
    });
    _searchController.addListener(_filterConversations);
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadConversations() async {
    setState(() => _isLoading = true);
    try {
      final profileState = ref.read(profileProvider);
      final profile = profileState.employeeProfile;
      final conversations = <_Conversation>[
        _Conversation(
          id: 'ai_assistant',
          name: 'AI Assistant',
          lastMessage: 'Ask me anything about your job search',
          lastMessageTime: DateTime.now(),
          isAiAssistant: true,
          isOnline: true,
        ),
      ];

      for (int i = 0; i < (profile?.experiences.length ?? 0); i++) {
        final exp = profile!.experiences[i];
        if (i < 5) {
          conversations.add(_Conversation(
            id: 'conv_$i',
            name: exp.company,
            lastMessage: 'Thank you for your interest in $exp.role position',
            lastMessageTime: DateTime.now().subtract(Duration(hours: i * 3)),
            unreadCount: i == 0 ? 2 : 0,
            isOnline: i % 2 == 0,
          ));
        }
      }

      setState(() {
        _conversations = conversations;
        _filteredConversations = conversations;
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  void _filterConversations() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      _filteredConversations = _conversations.where((c) {
        return c.name.toLowerCase().contains(query) ||
            c.lastMessage.toLowerCase().contains(query);
      }).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            const Padding(
              padding: EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      'Messages',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Search conversations...',
                  prefixIcon: const Icon(Icons.search_outlined),
                  filled: true,
                  fillColor:
                      Theme.of(context).inputDecorationTheme.fillColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: _isLoading
                  ? _buildLoading()
                  : _filteredConversations.isEmpty
                      ? _searchController.text.isNotEmpty
                          ? const EmptyState(
                              icon: Icons.search_off,
                              title: 'No Conversations Found',
                              message:
                                  'No matches for your search',
                            )
                          : RefreshIndicator(
                              onRefresh: _loadConversations,
                              child: ListView(
                                children: [
                                  const _AIAssistantTile(),
                                  const SizedBox(height: 100),
                                ],
                              ),
                            )
                      : RefreshIndicator(
                          onRefresh: _loadConversations,
                          child: ListView.separated(
                            padding: const EdgeInsets.symmetric(vertical: 8),
                            itemCount: _filteredConversations.length,
                            separatorBuilder: (_, __) =>
                                const Divider(height: 1, indent: 72),
                            itemBuilder: (context, index) {
                              final conv = _filteredConversations[index];
                              return _ConversationTile(
                                conversation: conv,
                                onTap: () => _openConversation(conv),
                              );
                            },
                          ),
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoading() {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: 5,
      itemBuilder: (context, index) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Row(
            children: [
              const ShimmerLoading(width: 48, height: 48, borderRadius: 14),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const ShimmerLoading(
                        width: 120, height: 14, borderRadius: 4),
                    const SizedBox(height: 8),
                    const ShimmerLoading(
                        width: double.infinity, height: 12, borderRadius: 4),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  void _openConversation(_Conversation conv) {
    if (conv.isAiAssistant) {
      context.push(RouteNames.voiceAssistant);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Opening chat with ${conv.name}'),
          backgroundColor: AppColors.primary,
        ),
      );
    }
  }
}

class _ConversationTile extends StatelessWidget {
  final _Conversation conversation;
  final VoidCallback onTap;

  const _ConversationTile({
    required this.conversation,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: conversation.isAiAssistant
          ? Container(
              width: 48,
              height: 48,
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  colors: AppColors.primaryGradient,
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.all(Radius.circular(14)),
              ),
              child: const Icon(Icons.auto_awesome,
                  color: Colors.white, size: 24),
            )
          : Stack(
              children: [
                CircleAvatar(
                  radius: 24,
                  backgroundColor: AppColors.primary.withOpacity(0.1),
                  backgroundImage: conversation.avatarUrl != null
                      ? NetworkImage(conversation.avatarUrl!)
                      : null,
                  child: conversation.avatarUrl == null
                      ? Text(
                          conversation.name.isNotEmpty
                              ? conversation.name[0].toUpperCase()
                              : '?',
                          style: const TextStyle(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w600,
                            fontSize: 18,
                          ),
                        )
                      : null,
                ),
                if (conversation.isOnline)
                  Positioned(
                    bottom: 2,
                    right: 2,
                    child: Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: AppColors.success,
                        shape: BoxShape.circle,
                        border: Border.all(
                            color: Theme.of(context).cardTheme.color ?? Colors.white,
                            width: 2),
                      ),
                    ),
                  ),
              ],
            ),
      title: Text(
        conversation.name,
        style: AppTextStyles.titleSmall,
      ),
      subtitle: Text(
        conversation.lastMessage,
        style: AppTextStyles.bodySmall,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            Formatters.relativeTime(conversation.lastMessageTime),
            style: TextStyle(
              fontSize: 11,
              color: conversation.unreadCount > 0
                  ? AppColors.primary
                  : AppColors.textSecondaryLight,
              fontWeight:
                  conversation.unreadCount > 0 ? FontWeight.w600 : FontWeight.w400,
            ),
          ),
          if (conversation.unreadCount > 0) ...[
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.all(4),
              decoration: const BoxDecoration(
                color: AppColors.primary,
                shape: BoxShape.circle,
              ),
              child: Text(
                '${conversation.unreadCount}',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ],
      ),
      onTap: onTap,
    );
  }
}

class _AIAssistantTile extends StatelessWidget {
  const _AIAssistantTile();

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Container(
        width: 48,
        height: 48,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: AppColors.primaryGradient,
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.all(Radius.circular(14)),
        ),
        child: const Icon(Icons.auto_awesome, color: Colors.white, size: 24),
      ),
      title: const Text(
        'AI Assistant',
        style: AppTextStyles.titleSmall,
      ),
      subtitle: const Text(
        'Ask me anything about your job search',
        style: AppTextStyles.bodySmall,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
      ),
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: AppColors.success.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: const Text(
          'Online',
          style: TextStyle(color: AppColors.success, fontSize: 11),
        ),
      ),
      onTap: () => context.push(RouteNames.voiceAssistant),
    );
  }
}
