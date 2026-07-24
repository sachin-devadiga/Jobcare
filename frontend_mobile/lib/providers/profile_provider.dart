import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/employee_profile_model.dart';
import '../models/employer_profile_model.dart';
import '../repositories/profile_repository.dart';
import '../core/error.dart';

class ProfileState {
  final EmployeeProfileModel? employeeProfile;
  final EmployerProfileModel? employerProfile;
  final bool isLoading;
  final bool isUpdating;
  final bool isUploading;
  final Failure? failure;
  final String? successMessage;

  const ProfileState({
    this.employeeProfile,
    this.employerProfile,
    this.isLoading = false,
    this.isUpdating = false,
    this.isUploading = false,
    this.failure,
    this.successMessage,
  });

  ProfileState copyWith({
    EmployeeProfileModel? employeeProfile,
    EmployerProfileModel? employerProfile,
    bool? isLoading,
    bool? isUpdating,
    bool? isUploading,
    Failure? failure,
    String? successMessage,
  }) {
    return ProfileState(
      employeeProfile: employeeProfile ?? this.employeeProfile,
      employerProfile: employerProfile ?? this.employerProfile,
      isLoading: isLoading ?? this.isLoading,
      isUpdating: isUpdating ?? this.isUpdating,
      isUploading: isUploading ?? this.isUploading,
      failure: failure,
      successMessage: successMessage,
    );
  }
}

class ProfileNotifier extends StateNotifier<ProfileState> {
  final ProfileRepository _profileRepository;

  ProfileNotifier(this._profileRepository) : super(const ProfileState());

  Future<void> fetchEmployeeProfile() async {
    state = state.copyWith(isLoading: true);
    try {
      final profile = await _profileRepository.getEmployeeProfile();
      state = state.copyWith(
        employeeProfile: profile,
        isLoading: false,
        failure: null,
      );
    } on Failure catch (e) {
      state = state.copyWith(isLoading: false, failure: e);
    }
  }

  Future<void> fetchEmployerProfile() async {
    state = state.copyWith(isLoading: true);
    try {
      final profile = await _profileRepository.getEmployerProfile();
      state = state.copyWith(
        employerProfile: profile,
        isLoading: false,
        failure: null,
      );
    } on Failure catch (e) {
      state = state.copyWith(isLoading: false, failure: e);
    }
  }

  Future<void> updateEmployeeProfile({
    String? fullName,
    String? phone,
    String? bio,
    String? dateOfBirth,
    String? gender,
    String? address,
    String? city,
    String? usrState,
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
    state = state.copyWith(isUpdating: true, failure: null);
    try {
      final profile = await _profileRepository.updateEmployeeProfile(
        fullName: fullName,
        phone: phone,
        bio: bio,
        dateOfBirth: dateOfBirth,
        gender: gender,
        address: address,
        city: city,
        state: usrState,
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
      state = state.copyWith(
        employeeProfile: profile,
        isUpdating: false,
        successMessage: 'Profile updated successfully',
      );
    } on Failure catch (e) {
      state = state.copyWith(isUpdating: false, failure: e);
    }
  }

  Future<String?> uploadProfileImage(String filePath) async {
    state = state.copyWith(isUploading: true, failure: null);
    try {
      final imageUrl = await _profileRepository.uploadProfileImage(filePath);
      final updatedProfile = state.employeeProfile?.copyWith(
        profileImage: imageUrl,
      );
      state = state.copyWith(
        employeeProfile: updatedProfile,
        isUploading: false,
        successMessage: 'Profile image updated',
      );
      return imageUrl;
    } on Failure catch (e) {
      state = state.copyWith(isUploading: false, failure: e);
      return null;
    }
  }

  Future<String?> uploadResume(String filePath) async {
    state = state.copyWith(isUploading: true, failure: null);
    try {
      final resumeUrl = await _profileRepository.uploadResume(filePath);
      final updatedProfile = state.employeeProfile?.copyWith(
        resumeUrl: resumeUrl,
      );
      state = state.copyWith(
        employeeProfile: updatedProfile,
        isUploading: false,
        successMessage: 'Resume uploaded successfully',
      );
      return resumeUrl;
    } on Failure catch (e) {
      state = state.copyWith(isUploading: false, failure: e);
      return null;
    }
  }

  Future<String?> uploadVoiceResume(String filePath) async {
    state = state.copyWith(isUploading: true, failure: null);
    try {
      final voiceUrl =
          await _profileRepository.uploadVoiceResume(filePath);
      final updatedProfile = state.employeeProfile?.copyWith(
        voiceResumeUrl: voiceUrl,
      );
      state = state.copyWith(
        employeeProfile: updatedProfile,
        isUploading: false,
        successMessage: 'Voice resume uploaded successfully',
      );
      return voiceUrl;
    } on Failure catch (e) {
      state = state.copyWith(isUploading: false, failure: e);
      return null;
    }
  }

  Future<void> addExperience(Map<String, dynamic> experience) async {
    try {
      await _profileRepository.addExperience(experience);
      await fetchEmployeeProfile();
    } on Failure catch (e) {
      state = state.copyWith(failure: e);
    }
  }

  Future<void> deleteExperience(String id) async {
    try {
      await _profileRepository.deleteExperience(id);
      await fetchEmployeeProfile();
    } on Failure catch (e) {
      state = state.copyWith(failure: e);
    }
  }

  Future<void> addEducation(Map<String, dynamic> education) async {
    try {
      await _profileRepository.addEducation(education);
      await fetchEmployeeProfile();
    } on Failure catch (e) {
      state = state.copyWith(failure: e);
    }
  }

  Future<void> deleteEducation(String id) async {
    try {
      await _profileRepository.deleteEducation(id);
      await fetchEmployeeProfile();
    } on Failure catch (e) {
      state = state.copyWith(failure: e);
    }
  }

  void clearFailure() {
    state = state.copyWith(failure: null);
  }

  void clearSuccess() {
    state = state.copyWith(successMessage: null);
  }
}
