import 'package:dio/dio.dart';
import '../core/error.dart';
import 'api_service.dart';
import '../models/employee_profile_model.dart';
import '../models/employer_profile_model.dart';

class ProfileService {
  final ApiService _apiService;

  ProfileService(this._apiService);

  Future<EmployeeProfileModel> getEmployeeProfile() async {
    try {
      final response = await _apiService.get('/users/profile/');
      final data = response.data as Map<String, dynamic>;
      return EmployeeProfileModel.fromJson(data['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        final now = DateTime.now();
        return EmployeeProfileModel(
          id: '',
          userId: '',
          createdAt: now,
          updatedAt: now,
        );
      }
      throw handleException(e.error);
    }
  }

  Future<EmployerProfileModel> getEmployerProfile() async {
    try {
      final response = await _apiService.get('/profile/employer');
      final data = response.data as Map<String, dynamic>;
      return EmployerProfileModel.fromJson(
          data['profile'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<EmployeeProfileModel> updateEmployeeProfile({
    String? fullName,
    String? phone,
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
    List<Map<String, dynamic>>? education,
    List<Map<String, dynamic>>? experiences,
    String? expectedSalary,
    String? preferredJobType,
    List<String>? preferredLocations,
    bool? isAvailable,
    String? noticePeriod,
  }) async {
    try {
      final body = <String, dynamic>{};
      if (fullName != null) body['full_name'] = fullName;
      if (phone != null) body['phone'] = phone;
      if (bio != null) body['bio'] = bio;
      if (dateOfBirth != null) body['date_of_birth'] = dateOfBirth;
      if (gender != null) body['gender'] = gender;
      if (address != null) body['address'] = address;
      if (city != null) body['city'] = city;
      if (state != null) body['state'] = state;
      if (pincode != null) body['pincode'] = pincode;
      if (latitude != null) body['latitude'] = latitude;
      if (longitude != null) body['longitude'] = longitude;
      if (skills != null) body['skills'] = skills;
      if (education != null) body['education'] = education;
      if (experiences != null) body['experiences'] = experiences;
      if (expectedSalary != null) body['expected_salary'] = expectedSalary;
      if (preferredJobType != null) {
        body['preferred_job_type'] = preferredJobType;
      }
      if (preferredLocations != null) {
        body['preferred_locations'] = preferredLocations;
      }
      if (isAvailable != null) body['is_available'] = isAvailable;
      if (noticePeriod != null) body['notice_period'] = noticePeriod;

      final response = await _apiService.put(
        '/users/profile/',
        data: body,
      );
      final data = response.data as Map<String, dynamic>;
      return EmployeeProfileModel.fromJson(data['data'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<EmployerProfileModel> updateEmployerProfile({
    String? fullName,
    String? designation,
    String? phone,
    String? companyId,
    String? companyName,
  }) async {
    try {
      final body = <String, dynamic>{};
      if (fullName != null) body['full_name'] = fullName;
      if (designation != null) body['designation'] = designation;
      if (phone != null) body['phone'] = phone;
      if (companyId != null) body['company_id'] = companyId;
      if (companyName != null) body['company_name'] = companyName;

      final response = await _apiService.put(
        '/profile/employer',
        data: body,
      );
      final data = response.data as Map<String, dynamic>;
      return EmployerProfileModel.fromJson(
          data['profile'] as Map<String, dynamic>);
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<String> uploadProfileImage(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(filePath),
      });
      final response = await _apiService.upload(
        '/profile/image',
        data: formData,
      );
      final data = response.data as Map<String, dynamic>;
      return data['image_url'] as String;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<String> uploadResume(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'resume': await MultipartFile.fromFile(filePath),
      });
      final response = await _apiService.upload(
        '/profile/resume',
        data: formData,
      );
      final data = response.data as Map<String, dynamic>;
      return data['resume_url'] as String;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<String> uploadVoiceResume(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'voice_resume': await MultipartFile.fromFile(
          filePath,
          filename: 'voice_resume.wav',
        ),
      });
      final response = await _apiService.upload(
        '/profile/voice-resume',
        data: formData,
      );
      final data = response.data as Map<String, dynamic>;
      return data['voice_resume_url'] as String;
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> deleteResume() async {
    try {
      await _apiService.delete('/profile/resume');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> deleteVoiceResume() async {
    try {
      await _apiService.delete('/profile/voice-resume');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> addExperience(Map<String, dynamic> experience) async {
    try {
      await _apiService.post(
        '/profile/experience',
        data: experience,
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> updateExperience(String id, Map<String, dynamic> experience) async {
    try {
      await _apiService.put(
        '/profile/experience/$id',
        data: experience,
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> deleteExperience(String id) async {
    try {
      await _apiService.delete('/profile/experience/$id');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> addEducation(Map<String, dynamic> education) async {
    try {
      await _apiService.post(
        '/profile/education',
        data: education,
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> updateEducation(String id, Map<String, dynamic> education) async {
    try {
      await _apiService.put(
        '/profile/education/$id',
        data: education,
      );
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }

  Future<void> deleteEducation(String id) async {
    try {
      await _apiService.delete('/profile/education/$id');
    } on DioException catch (e) {
      throw handleException(e.error);
    }
  }
}
