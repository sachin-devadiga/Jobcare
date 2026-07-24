import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/providers.dart';
import '../models/notification_model.dart';
import '../theme/app_colors.dart';
import '../widgets/shimmer_loading.dart';
import '../widgets/empty_state.dart';

class NotificationsScreen extends ConsumerStatefulWidget {
  const NotificationsScreen({super.key});

  @override
  ConsumerState<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(notificationProvider.notifier).fetchNotifications(refresh: true);
    });
  }

  @override
  Widget build(BuildContext context) {
    final notifState = ref.watch(notificationProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        elevation: 0,
        title: const Text('Notifications', 
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          if (notifState.notifications.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_sweep_outlined),
              onPressed: () => ref.read(notificationProvider.notifier).clearAll(),
            ),
        ],
      ),
      body: notifState.isLoading && notifState.notifications.isEmpty
          ? _buildLoading()
          : notifState.notifications.isEmpty
              ? const EmptyState(
                  icon: Icons.notifications_none_rounded,
                  title: 'All Caught Up!',
                  message: 'You have no new notifications.',
                )
              : RefreshIndicator(
                  onRefresh: () async => ref.read(notificationProvider.notifier).fetchNotifications(refresh: true),
                  child: ListView.separated(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    itemCount: notifState.notifications.length,
                    separatorBuilder: (_, __) => const Divider(height: 1, indent: 72, color: Color(0xFFF1F5F9)),
                    itemBuilder: (context, index) {
                      final notification = notifState.notifications[index];
                      return _NotificationTile(notification: notification);
                    },
                  ),
                ),
    );
  }

  Widget _buildLoading() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 6,
      itemBuilder: (context, index) => Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: Row(
          children: [
            const ShimmerLoading(width: 44, height: 44, borderRadius: 22),
            const SizedBox(width: 12),
            Expanded(child: Column(children: [const ShimmerLoading(width: 150, height: 12), const SizedBox(height: 8), const ShimmerLoading(width: double.infinity, height: 10)]))
          ],
        ),
      ),
    );
  }
}

class _NotificationTile extends StatelessWidget {
  final NotificationModel notification;
  const _NotificationTile({required this.notification});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      leading: Container(
        width: 44, height: 44,
        decoration: BoxDecoration(
          color: notification.isRead ? AppColors.surface : AppColors.primary.withOpacity(0.1),
          shape: BoxShape.circle,
        ),
        child: Icon(
          _getIcon(notification.type),
          color: notification.isRead ? Colors.grey : AppColors.primary,
          size: 20,
        ),
      ),
      title: Text(notification.title, 
        style: TextStyle(fontWeight: notification.isRead ? FontWeight.normal : FontWeight.bold, fontSize: 14)),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(notification.body, style: TextStyle(color: Colors.grey.shade600, fontSize: 13), maxLines: 2, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 4),
           Text(_relativeTime(notification.createdAt), style: TextStyle(color: Colors.grey.shade400, fontSize: 11)),
        ],
      ),
      trailing: !notification.isRead ? Container(width: 8, height: 8, decoration: const BoxDecoration(color: AppColors.secondary, shape: BoxShape.circle)) : null,
    );
  }

  String _relativeTime(DateTime dt) {
    final diff = DateTime.now().difference(dt);
    if (diff.inDays > 365) return '${diff.inDays ~/ 365}y ago';
    if (diff.inDays > 30) return '${diff.inDays ~/ 30}mo ago';
    if (diff.inDays > 0) return '${diff.inDays}d ago';
    if (diff.inHours > 0) return '${diff.inHours}h ago';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m ago';
    return 'just now';
  }

  IconData _getIcon(NotificationType type) {
    switch (type) {
      case NotificationType.jobAlert: return Icons.work_rounded;
      case NotificationType.applicationUpdate: return Icons.assignment_turned_in_rounded;
      case NotificationType.interviewSchedule: return Icons.calendar_today_rounded;
      case NotificationType.message: return Icons.chat_rounded;
      default: return Icons.notifications_rounded;
    }
  }
}
