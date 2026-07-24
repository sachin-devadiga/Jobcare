import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/chat_provider.dart';
import '../providers/providers.dart';
import '../theme/app_colors.dart';
import '../widgets/shimmer_loading.dart';
import '../widgets/empty_state.dart';

class ChatListScreen extends ConsumerStatefulWidget {
  const ChatListScreen({super.key});

  @override
  ConsumerState<ChatListScreen> createState() => _ChatListScreenState();
}

class _ChatListScreenState extends ConsumerState<ChatListScreen> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(chatProvider.notifier).loadConversations();
      ref.read(chatProvider.notifier).connect();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);
    final currentUserId = ref.watch(authProvider).user?.id;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        elevation: 0,
        title: const Text('Messages', 
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
      ),
      body: Column(
        children: [
          Container(
            color: AppColors.primary,
            padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
              child: TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Search chats...',
                  hintStyle: TextStyle(color: Colors.grey.shade400, fontSize: 14),
                  prefixIcon: const Icon(Icons.search, color: AppColors.primary),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(vertical: 12),
                ),
                onChanged: (val) => ref.read(chatProvider.notifier).loadConversations(search: val),
              ),
            ),
          ),
          Expanded(
            child: chatState.isLoading
                ? _buildLoading()
                : chatState.conversations.isEmpty
                    ? const EmptyState(
                        icon: Icons.chat_bubble_outline_rounded,
                        title: 'No Messages',
                        message: 'Start talking with employers to get hired!',
                      )
                    : RefreshIndicator(
                        onRefresh: () async => ref.read(chatProvider.notifier).loadConversations(),
                        child: ListView.separated(
                          padding: const EdgeInsets.symmetric(vertical: 8),
                          itemCount: chatState.conversations.length,
                          separatorBuilder: (_, __) => const Divider(height: 1, indent: 80, color: Color(0xFFF1F5F9)),
                          itemBuilder: (context, index) {
                            final conv = chatState.conversations[index];
                            return _ConversationTile(
                              conversation: conv,
                              isMe: currentUserId == conv.lastMessage?.senderId,
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoading() {
    return ListView.builder(
      padding: const EdgeInsets.all(20),
      itemCount: 5,
      itemBuilder: (context, index) => Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: Row(
          children: [
            const ShimmerLoading(width: 50, height: 50, borderRadius: 25),
            const SizedBox(width: 12),
            Expanded(child: Column(children: [const ShimmerLoading(width: 100, height: 12), const SizedBox(height: 8), const ShimmerLoading(width: double.infinity, height: 10)]))
          ],
        ),
      ),
    );
  }
}

class _ConversationTile extends StatelessWidget {
  final dynamic conversation;
  final bool isMe;

  const _ConversationTile({required this.conversation, required this.isMe});

  @override
  Widget build(BuildContext context) {
    final name = conversation.otherParticipant?['name'] ?? 'Employer';
    final hasUnread = conversation.unreadCount > 0;

    return ListTile(
      onTap: () => context.push('/chat/${conversation.id}', extra: {'name': name}),
      leading: CircleAvatar(
        radius: 28,
        backgroundColor: AppColors.surface,
        child: Text(name[0].toUpperCase(), style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)),
      ),
      title: Text(name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
      subtitle: Text(
        '${isMe ? "You: " : ""}${conversation.lastMessage?.content ?? "No messages"}',
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: TextStyle(color: hasUnread ? AppColors.textPrimary : AppColors.textSecondary, fontWeight: hasUnread ? FontWeight.w600 : FontWeight.normal),
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          const Text('12:30 PM', style: TextStyle(fontSize: 11, color: Colors.grey)),
          if (hasUnread)
            Container(
              margin: const EdgeInsets.only(top: 4),
              padding: const EdgeInsets.all(6),
              decoration: const BoxDecoration(color: AppColors.primary, shape: BoxShape.circle),
              child: Text('${conversation.unreadCount}', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
            ),
        ],
      ),
    );
  }
}
