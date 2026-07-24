import 'dart:convert';

class Experience {
  final String id;
  final String company;
  final String role;
  final String? description;
  final DateTime startDate;
  final DateTime? endDate;
  final bool isCurrent;
  final String? location;

  const Experience({
    required this.id,
    required this.company,
    required this.role,
    this.description,
    required this.startDate,
    this.endDate,
    this.isCurrent = false,
    this.location,
  });

  factory Experience.fromJson(Map<String, dynamic> json) {
    return Experience(
      id: json['id'] as String,
      company: json['company'] as String,
      role: json['role'] as String,
      description: json['description'] as String?,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: json['end_date'] != null
          ? DateTime.parse(json['end_date'] as String)
          : null,
      isCurrent: json['is_current'] as bool? ?? false,
      location: json['location'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'company': company,
    'role': role,
    'description': description,
    'start_date': startDate.toIso8601String(),
    'end_date': endDate?.toIso8601String(),
    'is_current': isCurrent,
    'location': location,
  };
}

class Education {
  final String id;
  final String institution;
  final String degree;
  final String? field;
  final DateTime startDate;
  final DateTime? endDate;
  final bool isCurrent;
  final String? grade;
  final String? description;

  const Education({
    required this.id,
    required this.institution,
    required this.degree,
    this.field,
    required this.startDate,
    this.endDate,
    this.isCurrent = false,
    this.grade,
    this.description,
  });

  factory Education.fromJson(Map<String, dynamic> json) {
    return Education(
      id: json['id'] as String,
      institution: json['institution'] as String,
      degree: json['degree'] as String,
      field: json['field'] as String?,
      startDate: DateTime.parse(json['start_date'] as String),
      endDate: json['end_date'] != null
          ? DateTime.parse(json['end_date'] as String)
          : null,
      isCurrent: json['is_current'] as bool? ?? false,
      grade: json['grade'] as String?,
      description: json['description'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'institution': institution,
    'degree': degree,
    'field': field,
    'start_date': startDate.toIso8601String(),
    'end_date': endDate?.toIso8601String(),
    'is_current': isCurrent,
    'grade': grade,
    'description': description,
  };
}

class Certificate {
  final String id;
  final String name;
  final String? issuingOrganization;
  final DateTime? issueDate;
  final DateTime? expiryDate;
  final String? credentialId;
  final String? credentialUrl;

  const Certificate({
    required this.id,
    required this.name,
    this.issuingOrganization,
    this.issueDate,
    this.expiryDate,
    this.credentialId,
    this.credentialUrl,
  });

  factory Certificate.fromJson(Map<String, dynamic> json) {
    return Certificate(
      id: json['id'] as String,
      name: json['name'] as String,
      issuingOrganization: json['issuing_organization'] as String?,
      issueDate: json['issue_date'] != null
          ? DateTime.parse(json['issue_date'] as String)
          : null,
      expiryDate: json['expiry_date'] != null
          ? DateTime.parse(json['expiry_date'] as String)
          : null,
      credentialId: json['credential_id'] as String?,
      credentialUrl: json['credential_url'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'issuing_organization': issuingOrganization,
    'issue_date': issueDate?.toIso8601String(),
    'expiry_date': expiryDate?.toIso8601String(),
    'credential_id': credentialId,
    'credential_url': credentialUrl,
  };
}

class Language {
  final String id;
  final String name;
  final String proficiency;

  const Language({
    required this.id,
    required this.name,
    this.proficiency = 'beginner',
  });

  factory Language.fromJson(Map<String, dynamic> json) {
    return Language(
      id: json['id'] as String,
      name: json['name'] as String,
      proficiency: json['proficiency'] as String? ?? 'beginner',
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'proficiency': proficiency,
  };
}

class EmployeeProfileModel {
  final String id;
  final String userId;
  final String? fullName;
  final String? phone;
  final String? profileImage;
  final String? bio;
  final String? dateOfBirth;
  final String? gender;
  final String? address;
  final String? city;
  final String? state;
  final String? pincode;
  final double? latitude;
  final double? longitude;
  final List<String> skills;
  final List<Experience> experiences;
  final List<Education> education;
  final List<Certificate> certificates;
  final List<Language> languages;
  final String? resumeUrl;
  final String? voiceResumeUrl;
  final String? resumeText;
  final String? expectedSalary;
  final String? preferredJobType;
  final List<String> preferredLocations;
  final bool isAvailable;
  final String? noticePeriod;
  final double profileCompletionScore;
  final DateTime createdAt;
  final DateTime updatedAt;

  const EmployeeProfileModel({
    required this.id,
    required this.userId,
    this.fullName,
    this.phone,
    this.profileImage,
    this.bio,
    this.dateOfBirth,
    this.gender,
    this.address,
    this.city,
    this.state,
    this.pincode,
    this.latitude,
    this.longitude,
    this.skills = const [],
    this.experiences = const [],
    this.education = const [],
    this.certificates = const [],
    this.languages = const [],
    this.resumeUrl,
    this.voiceResumeUrl,
    this.resumeText,
    this.expectedSalary,
    this.preferredJobType,
    this.preferredLocations = const [],
    this.isAvailable = true,
    this.noticePeriod,
    this.profileCompletionScore = 0,
    required this.createdAt,
    required this.updatedAt,
  });

  double get completionScore {
    int score = 0;
    int total = 10;

    if (fullName != null && fullName!.isNotEmpty) score++;
    if (phone != null && phone!.isNotEmpty) score++;
    if (profileImage != null) score++;
    if (bio != null && bio!.isNotEmpty) score++;
    if (skills.isNotEmpty) score++;
    if (experiences.isNotEmpty) score++;
    if (education.isNotEmpty) score++;
    if (resumeUrl != null) score++;
    if (expectedSalary != null) score++;
    if (city != null && city!.isNotEmpty) score++;

    return score / total;
  }

  factory EmployeeProfileModel.fromJson(Map<String, dynamic> json) {
    return EmployeeProfileModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      fullName: json['full_name'] as String?,
      phone: json['phone'] as String?,
      profileImage: json['profile_image'] as String?,
      bio: json['bio'] as String?,
      dateOfBirth: json['date_of_birth'] as String?,
      gender: json['gender'] as String?,
      address: json['address'] as String?,
      city: json['city'] as String?,
      state: json['state'] as String?,
      pincode: json['pincode'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      skills: (json['skills'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      experiences: (json['experiences'] as List<dynamic>?)
              ?.map((e) => Experience.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      education: (json['education'] as List<dynamic>?)
              ?.map((e) => Education.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      certificates: (json['certificates'] as List<dynamic>?)
              ?.map((e) => Certificate.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      languages: (json['languages'] as List<dynamic>?)
              ?.map((e) => Language.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      resumeUrl: json['resume_url'] as String?,
      voiceResumeUrl: json['voice_resume_url'] as String?,
      resumeText: json['resume_text'] as String?,
      expectedSalary: json['expected_salary'] as String?,
      preferredJobType: json['preferred_job_type'] as String?,
      preferredLocations: (json['preferred_locations'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      isAvailable: json['is_available'] as bool? ?? true,
      noticePeriod: json['notice_period'] as String?,
      profileCompletionScore:
          (json['profile_completion_score'] as num?)?.toDouble() ?? 0,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'user_id': userId,
    'full_name': fullName,
    'phone': phone,
    'profile_image': profileImage,
    'bio': bio,
    'date_of_birth': dateOfBirth,
    'gender': gender,
    'address': address,
    'city': city,
    'state': state,
    'pincode': pincode,
    'latitude': latitude,
    'longitude': longitude,
    'skills': skills,
    'experiences': experiences.map((e) => e.toJson()).toList(),
    'education': education.map((e) => e.toJson()).toList(),
    'certificates': certificates.map((e) => e.toJson()).toList(),
    'languages': languages.map((e) => e.toJson()).toList(),
    'resume_url': resumeUrl,
    'voice_resume_url': voiceResumeUrl,
    'resume_text': resumeText,
    'expected_salary': expectedSalary,
    'preferred_job_type': preferredJobType,
    'preferred_locations': preferredLocations,
    'is_available': isAvailable,
    'notice_period': noticePeriod,
    'profile_completion_score': profileCompletionScore,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
  };

  String toJsonString() => json.encode(toJson());

  factory EmployeeProfileModel.fromJsonString(String str) =>
      EmployeeProfileModel.fromJson(
          json.decode(str) as Map<String, dynamic>);

  EmployeeProfileModel copyWith({
    String? id,
    String? userId,
    String? fullName,
    String? phone,
    String? profileImage,
    String? bio,
    String? dateOfBirth,
    String? gender,
    String? address,
    String? city,
    String? state,
    String? pincode,
    double? latitude,
    double? longitude,
    List<String>? skills,
    List<Experience>? experiences,
    List<Education>? education,
    List<Certificate>? certificates,
    List<Language>? languages,
    String? resumeUrl,
    String? voiceResumeUrl,
    String? resumeText,
    String? expectedSalary,
    String? preferredJobType,
    List<String>? preferredLocations,
    bool? isAvailable,
    String? noticePeriod,
    double? profileCompletionScore,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return EmployeeProfileModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      fullName: fullName ?? this.fullName,
      phone: phone ?? this.phone,
      profileImage: profileImage ?? this.profileImage,
      bio: bio ?? this.bio,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      gender: gender ?? this.gender,
      address: address ?? this.address,
      city: city ?? this.city,
      state: state ?? this.state,
      pincode: pincode ?? this.pincode,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      skills: skills ?? this.skills,
      experiences: experiences ?? this.experiences,
      education: education ?? this.education,
      certificates: certificates ?? this.certificates,
      languages: languages ?? this.languages,
      resumeUrl: resumeUrl ?? this.resumeUrl,
      voiceResumeUrl: voiceResumeUrl ?? this.voiceResumeUrl,
      resumeText: resumeText ?? this.resumeText,
      expectedSalary: expectedSalary ?? this.expectedSalary,
      preferredJobType: preferredJobType ?? this.preferredJobType,
      preferredLocations: preferredLocations ?? this.preferredLocations,
      isAvailable: isAvailable ?? this.isAvailable,
      noticePeriod: noticePeriod ?? this.noticePeriod,
      profileCompletionScore:
          profileCompletionScore ?? this.profileCompletionScore,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
