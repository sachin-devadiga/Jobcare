import 'dart:convert';

enum NotificationType {
  jobAlert,
  applicationUpdate,
  interviewSchedule,
  message,
  profileUpdate,
  payment,
  subscription,
  promotion,
  system,
  reminder;

  String get value {
    switch (this) {
      case NotificationType.jobAlert:
        return 'job_alert';
      case NotificationType.applicationUpdate:
        return 'application_update';
      case NotificationType.interviewSchedule:
        return 'interview_schedule';
      case NotificationType.message:
        return 'message';
      case NotificationType.profileUpdate:
        return 'profile_update';
      case NotificationType.payment:
        return 'payment';
      case NotificationType.subscription:
        return 'subscription';
      case NotificationType.promotion:
        return 'promotion';
      case NotificationType.system:
        return 'system';
      case NotificationType.reminder:
        return 'reminder';
    }
  }

  static NotificationType fromString(String value) {
    switch (value.toLowerCase()) {
      case 'job_alert':
        return NotificationType.jobAlert;
      case 'application_update':
        return NotificationType.applicationUpdate;
      case 'interview_schedule':
        return NotificationType.interviewSchedule;
      case 'message':
        return NotificationType.message;
      case 'profile_update':
        return NotificationType.profileUpdate;
      case 'payment':
        return NotificationType.payment;
      case 'subscription':
        return NotificationType.subscription;
      case 'promotion':
        return NotificationType.promotion;
      case 'system':
        return NotificationType.system;
      case 'reminder':
        return NotificationType.reminder;
      default:
        return NotificationType.system;
    }
  }
}

class NotificationModel {
  final String id;
  final String userId;
  final NotificationType type;
  final String title;
  final String body;
  final String? imageUrl;
  final String? data;
  final String? actionLink;
  final bool isRead;
  final DateTime createdAt;

  const NotificationModel({
    required this.id,
    required this.userId,
    required this.type,
    required this.title,
    required this.body,
    this.imageUrl,
    this.data,
    this.actionLink,
    this.isRead = false,
    required this.createdAt,
  });

  factory NotificationModel.fromJson(Map<String, dynamic> json) {
    return NotificationModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      type: NotificationType.fromString(
          json['type'] as String? ?? 'system'),
      title: json['title'] as String,
      body: json['body'] as String,
      imageUrl: json['image_url'] as String?,
      data: json['data'] as String?,
      actionLink: json['action_link'] as String?,
      isRead: json['is_read'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'user_id': userId,
    'type': type.value,
    'title': title,
    'body': body,
    'image_url': imageUrl,
    'data': data,
    'action_link': actionLink,
    'is_read': isRead,
    'created_at': createdAt.toIso8601String(),
  };

  String toJsonString() => json.encode(toJson());

  factory NotificationModel.fromJsonString(String str) =>
      NotificationModel.fromJson(
          json.decode(str) as Map<String, dynamic>);

  NotificationModel copyWith({
    String? id,
    String? userId,
    NotificationType? type,
    String? title,
    String? body,
    String? imageUrl,
    String? data,
    String? actionLink,
    bool? isRead,
    DateTime? createdAt,
  }) {
    return NotificationModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      type: type ?? this.type,
      title: title ?? this.title,
      body: body ?? this.body,
      imageUrl: imageUrl ?? this.imageUrl,
      data: data ?? this.data,
      actionLink: actionLink ?? this.actionLink,
      isRead: isRead ?? this.isRead,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
