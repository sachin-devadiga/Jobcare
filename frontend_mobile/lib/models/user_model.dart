import 'dart:convert';

enum UserRole {
  employee,
  employer,
  admin;

  String get value {
    switch (this) {
      case UserRole.employee:
        return 'employee';
      case UserRole.employer:
        return 'employer';
      case UserRole.admin:
        return 'admin';
    }
  }

  static UserRole fromString(String value) {
    switch (value.toLowerCase()) {
      case 'employee':
        return UserRole.employee;
      case 'employer':
        return UserRole.employer;
      case 'admin':
        return UserRole.admin;
      default:
        return UserRole.employee;
    }
  }
}

enum AuthProvider {
  email,
  google,
  phone,
  apple;

  String get value {
    switch (this) {
      case AuthProvider.email:
        return 'email';
      case AuthProvider.google:
        return 'google';
      case AuthProvider.phone:
        return 'phone';
      case AuthProvider.apple:
        return 'apple';
    }
  }

  static AuthProvider fromString(String value) {
    switch (value.toLowerCase()) {
      case 'email':
        return AuthProvider.email;
      case 'google':
        return AuthProvider.google;
      case 'phone':
        return AuthProvider.phone;
      case 'apple':
        return AuthProvider.apple;
      default:
        return AuthProvider.email;
    }
  }
}

class UserModel {
  final String id;
  final String email;
  final String? phone;
  final String name;
  final UserRole role;
  final String? profileImage;
  final AuthProvider? authProvider;
  final bool isEmailVerified;
  final bool isPhoneVerified;
  final bool isProfileComplete;
  final String? fcmToken;
  final String? language;
  final DateTime createdAt;
  final DateTime updatedAt;

  const UserModel({
    required this.id,
    required this.email,
    this.phone,
    required this.name,
    required this.role,
    this.profileImage,
    this.authProvider,
    this.isEmailVerified = false,
    this.isPhoneVerified = false,
    this.isProfileComplete = false,
    this.fcmToken,
    this.language,
    required this.createdAt,
    required this.updatedAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String,
      email: json['email'] as String? ?? '',
      phone: json['phone'] as String?,
      name: json['name'] as String? ?? '',
      role: UserRole.fromString(json['role'] as String? ?? 'employee'),
      profileImage: json['profile_image'] as String?,
      authProvider: json['auth_provider'] != null
          ? AuthProvider.fromString(json['auth_provider'] as String)
          : null,
      isEmailVerified: json['is_email_verified'] as bool? ?? false,
      isPhoneVerified: json['is_phone_verified'] as bool? ?? false,
      isProfileComplete: json['is_profile_complete'] as bool? ?? false,
      fcmToken: json['fcm_token'] as String?,
      language: json['language'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'phone': phone,
      'name': name,
      'role': role.value,
      'profile_image': profileImage,
      'auth_provider': authProvider?.value,
      'is_email_verified': isEmailVerified,
      'is_phone_verified': isPhoneVerified,
      'is_profile_complete': isProfileComplete,
      'fcm_token': fcmToken,
      'language': language,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  String toJsonString() => json.encode(toJson());

  factory UserModel.fromJsonString(String str) =>
      UserModel.fromJson(json.decode(str) as Map<String, dynamic>);

  UserModel copyWith({
    String? id,
    String? email,
    String? phone,
    String? name,
    UserRole? role,
    String? profileImage,
    AuthProvider? authProvider,
    bool? isEmailVerified,
    bool? isPhoneVerified,
    bool? isProfileComplete,
    String? fcmToken,
    String? language,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return UserModel(
      id: id ?? this.id,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      name: name ?? this.name,
      role: role ?? this.role,
      profileImage: profileImage ?? this.profileImage,
      authProvider: authProvider ?? this.authProvider,
      isEmailVerified: isEmailVerified ?? this.isEmailVerified,
      isPhoneVerified: isPhoneVerified ?? this.isPhoneVerified,
      isProfileComplete: isProfileComplete ?? this.isProfileComplete,
      fcmToken: fcmToken ?? this.fcmToken,
      language: language ?? this.language,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
