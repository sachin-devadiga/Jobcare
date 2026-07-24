import 'dart:convert';

class CategoryModel {
  final String id;
  final String name;
  final String? icon;
  final String? imageUrl;
  final String? color;
  final int jobCount;
  final bool isActive;
  final int sortOrder;
  final DateTime createdAt;
  final DateTime updatedAt;

  const CategoryModel({
    required this.id,
    required this.name,
    this.icon,
    this.imageUrl,
    this.color,
    this.jobCount = 0,
    this.isActive = true,
    this.sortOrder = 0,
    required this.createdAt,
    required this.updatedAt,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    return CategoryModel(
      id: json['id'] as String,
      name: json['name'] as String,
      icon: json['icon'] as String?,
      imageUrl: json['image_url'] as String?,
      color: json['color'] as String?,
      jobCount: json['job_count'] as int? ?? 0,
      isActive: json['is_active'] as bool? ?? true,
      sortOrder: json['sort_order'] as int? ?? 0,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'icon': icon,
    'image_url': imageUrl,
    'color': color,
    'job_count': jobCount,
    'is_active': isActive,
    'sort_order': sortOrder,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
  };

  String toJsonString() => json.encode(toJson());

  factory CategoryModel.fromJsonString(String str) =>
      CategoryModel.fromJson(json.decode(str) as Map<String, dynamic>);

  CategoryModel copyWith({
    String? id,
    String? name,
    String? icon,
    String? imageUrl,
    String? color,
    int? jobCount,
    bool? isActive,
    int? sortOrder,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return CategoryModel(
      id: id ?? this.id,
      name: name ?? this.name,
      icon: icon ?? this.icon,
      imageUrl: imageUrl ?? this.imageUrl,
      color: color ?? this.color,
      jobCount: jobCount ?? this.jobCount,
      isActive: isActive ?? this.isActive,
      sortOrder: sortOrder ?? this.sortOrder,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
