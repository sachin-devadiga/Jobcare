import 'dart:convert';
import 'company_model.dart';

enum JobType {
  fullTime,
  partTime,
  contract,
  freelance,
  internship,
  temporary;

  String get value {
    switch (this) {
      case JobType.fullTime:
        return 'full_time';
      case JobType.partTime:
        return 'part_time';
      case JobType.contract:
        return 'contract';
      case JobType.freelance:
        return 'freelance';
      case JobType.internship:
        return 'internship';
      case JobType.temporary:
        return 'temporary';
    }
  }

  static JobType fromString(String value) {
    switch (value.toLowerCase()) {
      case 'full_time':
        return JobType.fullTime;
      case 'part_time':
        return JobType.partTime;
      case 'contract':
        return JobType.contract;
      case 'freelance':
        return JobType.freelance;
      case 'internship':
        return JobType.internship;
      case 'temporary':
        return JobType.temporary;
      default:
        return JobType.fullTime;
    }
  }
}

enum ShiftType {
  day,
  night,
  rotating,
  flexible;

  String get value {
    switch (this) {
      case ShiftType.day:
        return 'day';
      case ShiftType.night:
        return 'night';
      case ShiftType.rotating:
        return 'rotating';
      case ShiftType.flexible:
        return 'flexible';
    }
  }

  static ShiftType fromString(String value) {
    switch (value.toLowerCase()) {
      case 'day':
        return ShiftType.day;
      case 'night':
        return ShiftType.night;
      case 'rotating':
        return ShiftType.rotating;
      case 'flexible':
        return ShiftType.flexible;
      default:
        return ShiftType.day;
    }
  }
}

enum SalaryType {
  fixed,
  range,
  negotiable;

  String get value {
    switch (this) {
      case SalaryType.fixed:
        return 'fixed';
      case SalaryType.range:
        return 'range';
      case SalaryType.negotiable:
        return 'negotiable';
    }
  }

  static SalaryType fromString(String value) {
    switch (value.toLowerCase()) {
      case 'fixed':
        return SalaryType.fixed;
      case 'range':
        return SalaryType.range;
      case 'negotiable':
        return SalaryType.negotiable;
      default:
        return SalaryType.fixed;
    }
  }
}

enum JobUrgency {
  immediate,
  urgent,
  normal,
  flexible;

  String get value {
    switch (this) {
      case JobUrgency.immediate:
        return 'immediate';
      case JobUrgency.urgent:
        return 'urgent';
      case JobUrgency.normal:
        return 'normal';
      case JobUrgency.flexible:
        return 'flexible';
    }
  }

  static JobUrgency fromString(String value) {
    switch (value.toLowerCase()) {
      case 'immediate':
        return JobUrgency.immediate;
      case 'urgent':
        return JobUrgency.urgent;
      case 'normal':
        return JobUrgency.normal;
      case 'flexible':
        return JobUrgency.flexible;
      default:
        return JobUrgency.normal;
    }
  }
}

enum JobStatus {
  active,
  closed,
  paused,
  draft,
  expired;

  String get value {
    switch (this) {
      case JobStatus.active:
        return 'active';
      case JobStatus.closed:
        return 'closed';
      case JobStatus.paused:
        return 'paused';
      case JobStatus.draft:
        return 'draft';
      case JobStatus.expired:
        return 'expired';
    }
  }

  static JobStatus fromString(String value) {
    switch (value.toLowerCase()) {
      case 'active':
        return JobStatus.active;
      case 'closed':
        return JobStatus.closed;
      case 'paused':
        return JobStatus.paused;
      case 'draft':
        return JobStatus.draft;
      case 'expired':
        return JobStatus.expired;
      default:
        return JobStatus.active;
    }
  }
}

class JobModel {
  final String id;
  final String employerId;
  final String companyId;
  final String title;
  final String? description;
  final List<String>? responsibilities;
  final List<String>? requirements;
  final List<String>? preferredQualifications;
  final JobType jobType;
  final ShiftType shiftType;
  final SalaryType salaryType;
  final double? salaryMin;
  final double? salaryMax;
  final String? salaryCurrency;
  final String? salaryPeriod;
  final JobUrgency urgency;
  final JobStatus status;
  final String? experienceLevel;
  final int? experienceMin;
  final int? experienceMax;
  final String? educationRequired;
  final List<String>? requiredSkills;
  final List<String>? preferredSkills;
  final String? location;
  final double? latitude;
  final double? longitude;
  final String? city;
  final String? state;
  final String? pincode;
  final int openPositions;
  final int applicantsCount;
  final String? categoryId;
  final String? categoryName;
  final List<String>? benefits;
  final String? applicationDeadline;
  final String? interviewProcess;
  final bool isRemote;
  final bool isFeatured;
  final bool isUrgent;
  final CompanyModel? company;
  final bool? isSaved;
  final bool? hasApplied;
  final DateTime createdAt;
  final DateTime updatedAt;

  const JobModel({
    required this.id,
    required this.employerId,
    required this.companyId,
    required this.title,
    this.description,
    this.responsibilities,
    this.requirements,
    this.preferredQualifications,
    this.jobType = JobType.fullTime,
    this.shiftType = ShiftType.day,
    this.salaryType = SalaryType.fixed,
    this.salaryMin,
    this.salaryMax,
    this.salaryCurrency,
    this.salaryPeriod,
    this.urgency = JobUrgency.normal,
    this.status = JobStatus.active,
    this.experienceLevel,
    this.experienceMin,
    this.experienceMax,
    this.educationRequired,
    this.requiredSkills,
    this.preferredSkills,
    this.location,
    this.latitude,
    this.longitude,
    this.city,
    this.state,
    this.pincode,
    this.openPositions = 1,
    this.applicantsCount = 0,
    this.categoryId,
    this.categoryName,
    this.benefits,
    this.applicationDeadline,
    this.interviewProcess,
    this.isRemote = false,
    this.isFeatured = false,
    this.isUrgent = false,
    this.company,
    this.isSaved,
    this.hasApplied,
    required this.createdAt,
    required this.updatedAt,
  });

  factory JobModel.fromJson(Map<String, dynamic> json) {
    return JobModel(
      id: json['id'] as String,
      employerId: json['employer_id'] as String,
      companyId: json['company_id'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      responsibilities: (json['responsibilities'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      requirements: (json['requirements'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      preferredQualifications: (json['preferred_qualifications'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      jobType: JobType.fromString(json['job_type'] as String? ?? 'full_time'),
      shiftType: ShiftType.fromString(json['shift_type'] as String? ?? 'day'),
      salaryType: SalaryType.fromString(json['salary_type'] as String? ?? 'fixed'),
      salaryMin: (json['salary_min'] as num?)?.toDouble(),
      salaryMax: (json['salary_max'] as num?)?.toDouble(),
      salaryCurrency: json['salary_currency'] as String?,
      salaryPeriod: json['salary_period'] as String?,
      urgency: JobUrgency.fromString(json['urgency'] as String? ?? 'normal'),
      status: JobStatus.fromString(json['status'] as String? ?? 'active'),
      experienceLevel: json['experience_level'] as String?,
      experienceMin: json['experience_min'] as int?,
      experienceMax: json['experience_max'] as int?,
      educationRequired: json['education_required'] as String?,
      requiredSkills: (json['required_skills'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      preferredSkills: (json['preferred_skills'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      location: json['location'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      city: json['city'] as String?,
      state: json['state'] as String?,
      pincode: json['pincode'] as String?,
      openPositions: json['open_positions'] as int? ?? 1,
      applicantsCount: json['applicants_count'] as int? ?? 0,
      categoryId: json['category_id'] as String?,
      categoryName: json['category_name'] as String?,
      benefits: (json['benefits'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      applicationDeadline: json['application_deadline'] as String?,
      interviewProcess: json['interview_process'] as String?,
      isRemote: json['is_remote'] as bool? ?? false,
      isFeatured: json['is_featured'] as bool? ?? false,
      isUrgent: json['is_urgent'] as bool? ?? false,
      company: json['company'] != null
          ? CompanyModel.fromJson(json['company'] as Map<String, dynamic>)
          : null,
      isSaved: json['is_saved'] as bool?,
      hasApplied: json['has_applied'] as bool?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'employer_id': employerId,
    'company_id': companyId,
    'title': title,
    'description': description,
    'responsibilities': responsibilities,
    'requirements': requirements,
    'preferred_qualifications': preferredQualifications,
    'job_type': jobType.value,
    'shift_type': shiftType.value,
    'salary_type': salaryType.value,
    'salary_min': salaryMin,
    'salary_max': salaryMax,
    'salary_currency': salaryCurrency,
    'salary_period': salaryPeriod,
    'urgency': urgency.value,
    'status': status.value,
    'experience_level': experienceLevel,
    'experience_min': experienceMin,
    'experience_max': experienceMax,
    'education_required': educationRequired,
    'required_skills': requiredSkills,
    'preferred_skills': preferredSkills,
    'location': location,
    'latitude': latitude,
    'longitude': longitude,
    'city': city,
    'state': state,
    'pincode': pincode,
    'open_positions': openPositions,
    'applicants_count': applicantsCount,
    'category_id': categoryId,
    'category_name': categoryName,
    'benefits': benefits,
    'application_deadline': applicationDeadline,
    'interview_process': interviewProcess,
    'is_remote': isRemote,
    'is_featured': isFeatured,
    'is_urgent': isUrgent,
    'company': company?.toJson(),
    'is_saved': isSaved,
    'has_applied': hasApplied,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
  };

  String toJsonString() => json.encode(toJson());

  factory JobModel.fromJsonString(String str) =>
      JobModel.fromJson(json.decode(str) as Map<String, dynamic>);

  JobModel copyWith({
    String? id,
    String? employerId,
    String? companyId,
    String? title,
    String? description,
    List<String>? responsibilities,
    List<String>? requirements,
    List<String>? preferredQualifications,
    JobType? jobType,
    ShiftType? shiftType,
    SalaryType? salaryType,
    double? salaryMin,
    double? salaryMax,
    String? salaryCurrency,
    String? salaryPeriod,
    JobUrgency? urgency,
    JobStatus? status,
    String? experienceLevel,
    int? experienceMin,
    int? experienceMax,
    String? educationRequired,
    List<String>? requiredSkills,
    List<String>? preferredSkills,
    String? location,
    double? latitude,
    double? longitude,
    String? city,
    String? state,
    String? pincode,
    int? openPositions,
    int? applicantsCount,
    String? categoryId,
    String? categoryName,
    List<String>? benefits,
    String? applicationDeadline,
    String? interviewProcess,
    bool? isRemote,
    bool? isFeatured,
    bool? isUrgent,
    CompanyModel? company,
    bool? isSaved,
    bool? hasApplied,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return JobModel(
      id: id ?? this.id,
      employerId: employerId ?? this.employerId,
      companyId: companyId ?? this.companyId,
      title: title ?? this.title,
      description: description ?? this.description,
      responsibilities: responsibilities ?? this.responsibilities,
      requirements: requirements ?? this.requirements,
      preferredQualifications:
          preferredQualifications ?? this.preferredQualifications,
      jobType: jobType ?? this.jobType,
      shiftType: shiftType ?? this.shiftType,
      salaryType: salaryType ?? this.salaryType,
      salaryMin: salaryMin ?? this.salaryMin,
      salaryMax: salaryMax ?? this.salaryMax,
      salaryCurrency: salaryCurrency ?? this.salaryCurrency,
      salaryPeriod: salaryPeriod ?? this.salaryPeriod,
      urgency: urgency ?? this.urgency,
      status: status ?? this.status,
      experienceLevel: experienceLevel ?? this.experienceLevel,
      experienceMin: experienceMin ?? this.experienceMin,
      experienceMax: experienceMax ?? this.experienceMax,
      educationRequired: educationRequired ?? this.educationRequired,
      requiredSkills: requiredSkills ?? this.requiredSkills,
      preferredSkills: preferredSkills ?? this.preferredSkills,
      location: location ?? this.location,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      city: city ?? this.city,
      state: state ?? this.state,
      pincode: pincode ?? this.pincode,
      openPositions: openPositions ?? this.openPositions,
      applicantsCount: applicantsCount ?? this.applicantsCount,
      categoryId: categoryId ?? this.categoryId,
      categoryName: categoryName ?? this.categoryName,
      benefits: benefits ?? this.benefits,
      applicationDeadline: applicationDeadline ?? this.applicationDeadline,
      interviewProcess: interviewProcess ?? this.interviewProcess,
      isRemote: isRemote ?? this.isRemote,
      isFeatured: isFeatured ?? this.isFeatured,
      isUrgent: isUrgent ?? this.isUrgent,
      company: company ?? this.company,
      isSaved: isSaved ?? this.isSaved,
      hasApplied: hasApplied ?? this.hasApplied,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
