import 'dart:convert';

enum PaymentStatus {
  pending,
  success,
  failed,
  refunded,
  cancelled;

  String get value {
    switch (this) {
      case PaymentStatus.pending:
        return 'pending';
      case PaymentStatus.success:
        return 'success';
      case PaymentStatus.failed:
        return 'failed';
      case PaymentStatus.refunded:
        return 'refunded';
      case PaymentStatus.cancelled:
        return 'cancelled';
    }
  }

  static PaymentStatus fromString(String value) {
    switch (value.toLowerCase()) {
      case 'pending':
        return PaymentStatus.pending;
      case 'success':
        return PaymentStatus.success;
      case 'failed':
        return PaymentStatus.failed;
      case 'refunded':
        return PaymentStatus.refunded;
      case 'cancelled':
        return PaymentStatus.cancelled;
      default:
        return PaymentStatus.pending;
    }
  }
}

class PaymentModel {
  final String id;
  final String userId;
  final String? subscriptionId;
  final double amount;
  final String currency;
  final PaymentStatus status;
  final String? paymentMethod;
  final String? transactionId;
  final String? orderId;
  final String? invoiceUrl;
  final String? description;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime updatedAt;

  const PaymentModel({
    required this.id,
    required this.userId,
    this.subscriptionId,
    required this.amount,
    this.currency = 'INR',
    this.status = PaymentStatus.pending,
    this.paymentMethod,
    this.transactionId,
    this.orderId,
    this.invoiceUrl,
    this.description,
    this.metadata,
    required this.createdAt,
    required this.updatedAt,
  });

  factory PaymentModel.fromJson(Map<String, dynamic> json) {
    return PaymentModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      subscriptionId: json['subscription_id'] as String?,
      amount: (json['amount'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'INR',
      status: PaymentStatus.fromString(
          json['status'] as String? ?? 'pending'),
      paymentMethod: json['payment_method'] as String?,
      transactionId: json['transaction_id'] as String?,
      orderId: json['order_id'] as String?,
      invoiceUrl: json['invoice_url'] as String?,
      description: json['description'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'user_id': userId,
    'subscription_id': subscriptionId,
    'amount': amount,
    'currency': currency,
    'status': status.value,
    'payment_method': paymentMethod,
    'transaction_id': transactionId,
    'order_id': orderId,
    'invoice_url': invoiceUrl,
    'description': description,
    'metadata': metadata,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
  };
}

class SubscriptionPlan {
  final String id;
  final String name;
  final String description;
  final double price;
  final String currency;
  final String duration;
  final List<String> features;
  final bool isPopular;
  final bool isActive;
  final int? jobPostLimit;
  final int? candidateViewLimit;
  final bool hasVoiceResume;
  final bool hasPrioritySupport;
  final bool hasAnalytics;
  final DateTime createdAt;

  const SubscriptionPlan({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    this.currency = 'INR',
    required this.duration,
    required this.features,
    this.isPopular = false,
    this.isActive = true,
    this.jobPostLimit,
    this.candidateViewLimit,
    this.hasVoiceResume = false,
    this.hasPrioritySupport = false,
    this.hasAnalytics = false,
    required this.createdAt,
  });

  factory SubscriptionPlan.fromJson(Map<String, dynamic> json) {
    return SubscriptionPlan(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String,
      price: (json['price'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'INR',
      duration: json['duration'] as String,
      features: (json['features'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      isPopular: json['is_popular'] as bool? ?? false,
      isActive: json['is_active'] as bool? ?? true,
      jobPostLimit: json['job_post_limit'] as int?,
      candidateViewLimit: json['candidate_view_limit'] as int?,
      hasVoiceResume: json['has_voice_resume'] as bool? ?? false,
      hasPrioritySupport: json['has_priority_support'] as bool? ?? false,
      hasAnalytics: json['has_analytics'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'description': description,
    'price': price,
    'currency': currency,
    'duration': duration,
    'features': features,
    'is_popular': isPopular,
    'is_active': isActive,
    'job_post_limit': jobPostLimit,
    'candidate_view_limit': candidateViewLimit,
    'has_voice_resume': hasVoiceResume,
    'has_priority_support': hasPrioritySupport,
    'has_analytics': hasAnalytics,
    'created_at': createdAt.toIso8601String(),
  };
}

class SubscriptionModel {
  final String id;
  final String userId;
  final String planId;
  final String? planName;
  final SubscriptionPlan? plan;
  final String status;
  final DateTime startDate;
  final DateTime endDate;
  final DateTime? cancelledAt;
  final bool isAutoRenew;
  final int? jobPostsUsed;
  final int? candidateViewsUsed;
  final DateTime createdAt;
  final DateTime updatedAt;

  const SubscriptionModel({
    required this.id,
    required this.userId,
    required this.planId,
    this.planName,
    this.plan,
    this.status = 'active',
    required this.startDate,
    required this.endDate,
    this.cancelledAt,
    this.isAutoRenew = false,
    this.jobPostsUsed,
    this.candidateViewsUsed,
    required this.createdAt,
    required this.updatedAt,
  });

  factory SubscriptionModel.fromJson(Map<String, dynamic> json) {
    return SubscriptionModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      planId: json['plan_id'] as String,
      planName: json['plan_name'] as String?,
      plan: json['plan'] != null
          ? SubscriptionPlan.fromJson(
              json['plan'] as Map<String, dynamic>)
          : null,
      status: json['status'] as String? ?? 'active',
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: DateTime.parse(json['end_date'] as String),
      cancelledAt: json['cancelled_at'] != null
          ? DateTime.parse(json['cancelled_at'] as String)
          : null,
      isAutoRenew: json['is_auto_renew'] as bool? ?? false,
      jobPostsUsed: json['job_posts_used'] as int?,
      candidateViewsUsed: json['candidate_views_used'] as int?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'user_id': userId,
    'plan_id': planId,
    'plan_name': planName,
    'plan': plan?.toJson(),
    'status': status,
    'start_date': startDate.toIso8601String(),
    'end_date': endDate.toIso8601String(),
    'cancelled_at': cancelledAt?.toIso8601String(),
    'is_auto_renew': isAutoRenew,
    'job_posts_used': jobPostsUsed,
    'candidate_views_used': candidateViewsUsed,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
  };
}
