import 'dart:convert';

class EmployerProfileModel {
  final String id;
  final String userId;
  final String? fullName;
  final String? designation;
  final String? phone;
  final String? profileImage;
  final String? companyId;
  final String? companyName;
  final bool isVerified;
  final DateTime createdAt;
  final DateTime updatedAt;

  const EmployerProfileModel({
    required this.id,
    required this.userId,
    this.fullName,
    this.designation,
    this.phone,
    this.profileImage,
    this.companyId,
    this.companyName,
    this.isVerified = false,
    required this.createdAt,
    required this.updatedAt,
  });

  factory EmployerProfileModel.fromJson(Map<String, dynamic> json) {
    return EmployerProfileModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      fullName: json['full_name'] as String?,
      designation: json['designation'] as String?,
      phone: json['phone'] as String?,
      profileImage: json['profile_image'] as String?,
      companyId: json['company_id'] as String?,
      companyName: json['company_name'] as String?,
      isVerified: json['is_verified'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'user_id': userId,
    'full_name': fullName,
    'designation': designation,
    'phone': phone,
    'profile_image': profileImage,
    'company_id': companyId,
    'company_name': companyName,
    'is_verified': isVerified,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
  };

  String toJsonString() => json.encode(toJson());

  factory EmployerProfileModel.fromJsonString(String str) =>
      EmployerProfileModel.fromJson(
          json.decode(str) as Map<String, dynamic>);

  EmployerProfileModel copyWith({
    String? id,
    String? userId,
    String? fullName,
    String? designation,
    String? phone,
    String? profileImage,
    String? companyId,
    String? companyName,
    bool? isVerified,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return EmployerProfileModel(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      fullName: fullName ?? this.fullName,
      designation: designation ?? this.designation,
      phone: phone ?? this.phone,
      profileImage: profileImage ?? this.profileImage,
      companyId: companyId ?? this.companyId,
      companyName: companyName ?? this.companyName,
      isVerified: isVerified ?? this.isVerified,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
