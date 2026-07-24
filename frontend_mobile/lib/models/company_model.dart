import 'dart:convert';

class CompanyModel {
  final String id;
  final String name;
  final String? description;
  final String? logoUrl;
  final String? website;
  final String? industry;
  final String? companySize;
  final String? foundedYear;
  final String? headquarters;
  final List<String>? locations;
  final double? rating;
  final int reviewCount;
  final int jobCount;
  final bool isVerified;
  final String? about;
  final List<String>? benefits;
  final List<String>? galleryImages;
  final String? socialLinks;
  final DateTime createdAt;
  final DateTime updatedAt;

  const CompanyModel({
    required this.id,
    required this.name,
    this.description,
    this.logoUrl,
    this.website,
    this.industry,
    this.companySize,
    this.foundedYear,
    this.headquarters,
    this.locations,
    this.rating,
    this.reviewCount = 0,
    this.jobCount = 0,
    this.isVerified = false,
    this.about,
    this.benefits,
    this.galleryImages,
    this.socialLinks,
    required this.createdAt,
    required this.updatedAt,
  });

  factory CompanyModel.fromJson(Map<String, dynamic> json) {
    return CompanyModel(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      logoUrl: json['logo_url'] as String?,
      website: json['website'] as String?,
      industry: json['industry'] as String?,
      companySize: json['company_size'] as String?,
      foundedYear: json['founded_year'] as String?,
      headquarters: json['headquarters'] as String?,
      locations: (json['locations'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      rating: (json['rating'] as num?)?.toDouble(),
      reviewCount: json['review_count'] as int? ?? 0,
      jobCount: json['job_count'] as int? ?? 0,
      isVerified: json['is_verified'] as bool? ?? false,
      about: json['about'] as String?,
      benefits: (json['benefits'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      galleryImages: (json['gallery_images'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      socialLinks: json['social_links'] as String?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'description': description,
    'logo_url': logoUrl,
    'website': website,
    'industry': industry,
    'company_size': companySize,
    'founded_year': foundedYear,
    'headquarters': headquarters,
    'locations': locations,
    'rating': rating,
    'review_count': reviewCount,
    'job_count': jobCount,
    'is_verified': isVerified,
    'about': about,
    'benefits': benefits,
    'gallery_images': galleryImages,
    'social_links': socialLinks,
    'created_at': createdAt.toIso8601String(),
    'updated_at': updatedAt.toIso8601String(),
  };

  String toJsonString() => json.encode(toJson());

  factory CompanyModel.fromJsonString(String str) =>
      CompanyModel.fromJson(json.decode(str) as Map<String, dynamic>);

  CompanyModel copyWith({
    String? id,
    String? name,
    String? description,
    String? logoUrl,
    String? website,
    String? industry,
    String? companySize,
    String? foundedYear,
    String? headquarters,
    List<String>? locations,
    double? rating,
    int? reviewCount,
    int? jobCount,
    bool? isVerified,
    String? about,
    List<String>? benefits,
    List<String>? galleryImages,
    String? socialLinks,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return CompanyModel(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      logoUrl: logoUrl ?? this.logoUrl,
      website: website ?? this.website,
      industry: industry ?? this.industry,
      companySize: companySize ?? this.companySize,
      foundedYear: foundedYear ?? this.foundedYear,
      headquarters: headquarters ?? this.headquarters,
      locations: locations ?? this.locations,
      rating: rating ?? this.rating,
      reviewCount: reviewCount ?? this.reviewCount,
      jobCount: jobCount ?? this.jobCount,
      isVerified: isVerified ?? this.isVerified,
      about: about ?? this.about,
      benefits: benefits ?? this.benefits,
      galleryImages: galleryImages ?? this.galleryImages,
      socialLinks: socialLinks ?? this.socialLinks,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}
