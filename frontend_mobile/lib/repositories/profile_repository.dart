import '../services/profile_service.dart';
import '../models/employee_profile_model.dart';
import '../models/employer_profile_model.dart';

class ProfileRepository {
  final ProfileService _profileService;

  ProfileRepository(this._profileService);

  Future<EmployeeProfileModel> getEmployeeProfile() async {
    return await _profileService.getEmployeeProfile();
  }

  Future<EmployerProfileModel> getEmployerProfile() async {
    return await _profileService.getEmployerProfile();
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
    return await _profileService.updateEmployeeProfile(
      fullName: fullName,
      phone: phone,
      bio: bio,
      dateOfBirth: dateOfBirth,
      gender: gender,
      address: address,
      city: city,
      state: state,
      pincode: pincode,
      latitude: latitude,
      longitude: longitude,
      skills: skills,
      education: education,
      experiences: experiences,
      expectedSalary: expectedSalary,
      preferredJobType: preferredJobType,
      preferredLocations: preferredLocations,
      isAvailable: isAvailable,
      noticePeriod: noticePeriod,
    );
  }

  Future<EmployerProfileModel> updateEmployerProfile({
    String? fullName,
    String? designation,
    String? phone,
    String? companyId,
    String? companyName,
  }) async {
    return await _profileService.updateEmployerProfile(
      fullName: fullName,
      designation: designation,
      phone: phone,
      companyId: companyId,
      companyName: companyName,
    );
  }

  Future<String> uploadProfileImage(String filePath) async {
    return await _profileService.uploadProfileImage(filePath);
  }

  Future<String> uploadResume(String filePath) async {
    return await _profileService.uploadResume(filePath);
  }

  Future<String> uploadVoiceResume(String filePath) async {
    return await _profileService.uploadVoiceResume(filePath);
  }

  Future<void> deleteResume() async {
    await _profileService.deleteResume();
  }

  Future<void> deleteVoiceResume() async {
    await _profileService.deleteVoiceResume();
  }

  Future<void> addExperience(Map<String, dynamic> experience) async {
    await _profileService.addExperience(experience);
  }

  Future<void> deleteExperience(String id) async {
    await _profileService.deleteExperience(id);
  }

  Future<void> addEducation(Map<String, dynamic> education) async {
    await _profileService.addEducation(education);
  }

  Future<void> deleteEducation(String id) async {
    await _profileService.deleteEducation(id);
  }
}
