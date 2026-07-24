import 'dart:convert';
import 'job_model.dart';
import 'user_model.dart';

enum ApplicationStatus {
  applied,
  underReview,
  shortlisted,
  interviewScheduled,
  selected,
  offered,
  hired,
  rejected,
  withdrawn;

  String get value {
    switch (this) {
      case ApplicationStatus.applied:
        return 'applied';
      case ApplicationStatus.underReview:
        return 'under_review';
      case ApplicationStatus.shortlisted:
        return 'shortlisted';
      case ApplicationStatus.interviewScheduled:
        return 'interview_scheduled';
      case ApplicationStatus.selected:
        return 'selected';
      case ApplicationStatus.offered:
        return 'offered';
      case ApplicationStatus.hired:
        return 'hired';
      case ApplicationStatus.rejected:
        return 'rejected';
      case ApplicationStatus.withdrawn:
        return 'withdrawn';
    }
  }

  static ApplicationStatus fromString(String value) {
    switch (value.toLowerCase()) {
      case 'applied':
        return ApplicationStatus.applied;
      case 'under_review':
        return ApplicationStatus.underReview;
      case 'shortlisted':
        return ApplicationStatus.shortlisted;
      case 'interview_scheduled':
        return ApplicationStatus.interviewScheduled;
      case 'selected':
        return ApplicationStatus.selected;
      case 'offered':
        return ApplicationStatus.offered;
      case 'hired':
        return ApplicationStatus.hired;
      case 'rejected':
        return ApplicationStatus.rejected;
      case 'withdrawn':
        return ApplicationStatus.withdrawn;
      default:
        return ApplicationStatus.applied;
    }
  }
}

class Interview {
  final String? id;
  final String? scheduledAt;
  final String? interviewType;
  final String? location;
  final String? meetingLink;
  final String? notes;
  final String? interviewerName;
  final String? status;

  const Interview({
    this.id,
    this.scheduledAt,
    this.interviewType,
    this.location,
    this.meetingLink,
    this.notes,
    this.interviewerName,
    this.status,
  });

  factory Interview.fromJson(Map<String, dynamic> json) {
    return Interview(
      id: json['id'] as String?,
      scheduledAt: json['scheduled_at'] as String?,
      interviewType: json['interview_type'] as String?,
      location: json['location'] as String?,
      meetingLink: json['meeting_link'] as String?,
      notes: json['notes'] as String?,
      interviewerName: json['interviewer_name'] as String?,
      status: json['status'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'scheduled_at': scheduledAt,
    'interview_type': interviewType,
    'location': location,
    'meeting_link': meetingLink,
    'notes': notes,
    'interviewer_name': interviewerName,
    'status': status,
  };
}

class ApplicationModel {
  final String id;
  final String jobId;
  final String userId;
  final String? employerId;
  final ApplicationStatus status;
  final String? coverLetter;
  final String? resumeUrl;
  final String? voiceResumeUrl;
  final Interview? interview;
  final String? feedback;
  final int? rating;
  final String? rejectionReason;
  final String? notes;
  final bool? isReviewed;
  final DateTime appliedAt;
  final DateTime? reviewedAt;
  final DateTime? shortlistedAt;
  final DateTime? interviewedAt;
  final DateTime? offeredAt;
  final DateTime? hiredAt;
  final DateTime? rejectedAt;
  final DateTime? withdrawnAt;
  final DateTime createdAt;
  final DateTime updatedAt;
  final JobModel? job;
  final UserModel? user;

  const ApplicationModel({
    required this.id,
    required this.jobId,
    required this.userId,
    this.employerId,
    this.status = ApplicationStatus.applied,
    this.coverLetter,
    this.resumeUrl,
    this.voiceResumeUrl,
    this.interview,
    this.feedback,
    this.rating,
    this.rejectionReason,
    this.notes,
    this.isReviewed,
    required this.appliedAt,
    this.reviewedAt,
    this.shortlistedAt,
    this.interviewedAt,
    this.offeredAt,
    this.hiredAt,
    this.rejectedAt,
    this.withdrawnAt,
    required this.createdAt,
    required this.updatedAt,
    this.job,
    this.user,
  });

  factory ApplicationModel.fromJson(Map<String, dynamic> json) {
    return ApplicationModel(
      id: json['id'] as String,
      jobId: json['job_id'] as String,
      userId: json['user_id'] as String,
      employerId: json['employer_id'] as String?,
      status: ApplicationStatus.fromString(
          json['status'] as String? ?? 'applied'),
      coverLetter: json['cover_letter'] as String?,
      resumeUrl: json['resume_url'] as String?,
      voiceResumeUrl: json['voice_resume_url'] as String?,
      interview: json['interview'] != null
          ? Interview.fromJson(json['interview'] as Map<String, dynamic>)
          : null,
      feedback: json['feedback'] as String?,
      rating: json['rating'] as int?,
      rejectionReason: json['rejection_reason'] as String?,
      notes: json['notes'] as String?,
      isReviewed: json['is_reviewed'] as bool?,
      appliedAt: DateTime.parse(json['applied_at'] as String),
      reviewedAt: json['reviewed_at'] != null
          ? DateTime.parse(json['reviewed_at'] as String)
          : null,
      shortlistedAt: json['shortlisted_at'] != null
          ? DateTime.parse(json['shortlisted_at'] as String)
          : null,
      interviewedAt: json['interviewed_at'] != null
          ? DateTime.parse(json['interviewed_at'] as String)
          : null,
      offeredAt: json['offered_at'] != null
          ? DateTime.parse(json['offered_at'] as String)
          : null,
      hiredAt: json['hired_at'] != null
          ? DateTime.parse(json['hired_at'] as String)
          : null,
      rejectedAt: json['rejected_at'] != null
          ? DateTime.parse(json['rejected_at'] as String)
          : null,
      withdrawnAt: json['withdrawn_at'] != null
          ? DateTime.parse(json['withdrawn_at'] as String)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
      job: json['job'] != null
          ? JobModel.fromJson(json['job'] as Map<String, dynamic>)
          : null,
      user: json['user'] != null
          ? UserModel.fromJson(json['user'] as Map<String, dynamic>)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'job_id': jobId,
    'user_id': userId,
    'employer_id': employerId,
    'status': status.value,
    'cover_letter': coverLetter,
    'resume_url': resumeUrl,
    'voice_resume_url': voiceResumeUrl,
    'interview': interview?.toJson(),
    'feedback': feedback,
    'rating': rating,
    'rejection_reason': rejectionReason,
    'notes': notes,
    'is_reviewed': isReviewed,
    'applied_at': appliedAt.toIso8601String(),
    'reviewed_at': reviewedAt?.toIso8601String(),
    'shortlisted_at': shortlistedAt?.toIso8601String(),
    'interviewed_at': interviewedAt?.toIso8601String(),
    'offered_at': offeredAt?.toIso8601String(),
    'hired_at': hiredAt?.toIso8601String(),
    'rejected_at': rejectedAt?.toIso8601String(),
    'withdrawn_at': withdrawnAt?.toIso8601String(),
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
    'job': job?.toJson(),
    'user': user?.toJson(),
  };

  String toJsonString() => json.encode(toJson());

  factory ApplicationModel.fromJsonString(String str) =>
      ApplicationModel.fromJson(
          json.decode(str) as Map<String, dynamic>);

  ApplicationModel copyWith({
    String? id,
    String? jobId,
    String? userId,
    String? employerId,
    ApplicationStatus? status,
    String? coverLetter,
    String? resumeUrl,
    String? voiceResumeUrl,
    Interview? interview,
    String? feedback,
    int? rating,
    String? rejectionReason,
    String? notes,
    bool? isReviewed,
    DateTime? appliedAt,
    DateTime? reviewedAt,
    DateTime? shortlistedAt,
    DateTime? interviewedAt,
    DateTime? offeredAt,
    DateTime? hiredAt,
    DateTime? rejectedAt,
    DateTime? withdrawnAt,
    DateTime? createdAt,
    DateTime? updatedAt,
    JobModel? job,
    UserModel? user,
  }) {
    return ApplicationModel(
      id: id ?? this.id,
      jobId: jobId ?? this.jobId,
      userId: userId ?? this.userId,
      employerId: employerId ?? this.employerId,
      status: status ?? this.status,
      coverLetter: coverLetter ?? this.coverLetter,
      resumeUrl: resumeUrl ?? this.resumeUrl,
      voiceResumeUrl: voiceResumeUrl ?? this.voiceResumeUrl,
      interview: interview ?? this.interview,
      feedback: feedback ?? this.feedback,
      rating: rating ?? this.rating,
      rejectionReason: rejectionReason ?? this.rejectionReason,
      notes: notes ?? this.notes,
      isReviewed: isReviewed ?? this.isReviewed,
      appliedAt: appliedAt ?? this.appliedAt,
      reviewedAt: reviewedAt ?? this.reviewedAt,
      shortlistedAt: shortlistedAt ?? this.shortlistedAt,
      interviewedAt: interviewedAt ?? this.interviewedAt,
      offeredAt: offeredAt ?? this.offeredAt,
      hiredAt: hiredAt ?? this.hiredAt,
      rejectedAt: rejectedAt ?? this.rejectedAt,
      withdrawnAt: withdrawnAt ?? this.withdrawnAt,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      job: job ?? this.job,
      user: user ?? this.user,
    );
  }
}
