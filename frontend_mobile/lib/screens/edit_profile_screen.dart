import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_cropper/image_cropper.dart';
import '../providers/providers.dart';
import '../theme/app_colors.dart';
import '../widgets/loading_overlay.dart';
import '../core/utils.dart';
import '../core/localization.dart';

class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _bioController = TextEditingController();
  final _cityController = TextEditingController();
  final _stateController = TextEditingController();
  final _salaryController = TextEditingController();
  String _selectedJobType = 'full_time';
  bool _isAvailable = true;
  bool _isSaving = false;
  String? _profileImagePath;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final profile = ref.read(profileProvider).employeeProfile;
      if (profile != null) {
        _nameController.text = profile.fullName ?? '';
        _phoneController.text = profile.phone ?? '';
        _bioController.text = profile.bio ?? '';
        _cityController.text = profile.city ?? '';
        _stateController.text = profile.state ?? '';
        _salaryController.text = profile.expectedSalary ?? '';
        _selectedJobType = profile.preferredJobType ?? 'full_time';
        _isAvailable = profile.isAvailable;
      }
    });
  }

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _bioController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _salaryController.dispose();
    super.dispose();
  }

  Future<void> _pickAndCropImage() async {
    try {
      final result = await FilePicker.pickFiles(type: FileType.image, allowMultiple: false);
      if (result != null && result.files.single.path != null) {
        final cropped = await ImageCropper().cropImage(
          sourcePath: result.files.single.path!,
          uiSettings: [
            AndroidUiSettings(
              toolbarTitle: 'Crop Photo',
              toolbarColor: AppColors.primary,
              toolbarWidgetColor: Colors.white,
              initAspectRatio: CropAspectRatioPreset.square,
              lockAspectRatio: true,
            ),
          ],
        );
        if (cropped != null) setState(() => _profileImagePath = cropped.path);
      }
    } catch (_) {}
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSaving = true);
    try {
      await ref.read(profileProvider.notifier).updateEmployeeProfile(
            fullName: _nameController.text.trim(),
            phone: _phoneController.text.trim(),
            bio: _bioController.text.trim(),
            city: _cityController.text.trim(),
            usrState: _stateController.text.trim(),
            expectedSalary: _salaryController.text.trim(),
            preferredJobType: _selectedJobType,
            isAvailable: _isAvailable,
          );
      if (_profileImagePath != null) {
        await ref.read(profileProvider.notifier).uploadProfileImage(_profileImagePath!);
      }
      if (mounted) context.pop();
    } catch (_) {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileState = ref.watch(profileProvider);
    final lang = ref.watch(languageProvider);

    return LoadingOverlay(
      isLoading: _isSaving || profileState.isUpdating,
      child: Scaffold(
        backgroundColor: Colors.white,
        appBar: AppBar(
          backgroundColor: AppColors.primary,
          title: Text(AppStrings.get('edit_profile', lang), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          iconTheme: const IconThemeData(color: Colors.white),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Stack(
                    children: [
                      CircleAvatar(
                        radius: 60,
                        backgroundColor: AppColors.surface,
                        backgroundImage: _profileImagePath != null 
                          ? FileImage(File(_profileImagePath!)) 
                          : (profileState.employeeProfile?.profileImage != null ? NetworkImage(profileState.employeeProfile!.profileImage!) : null) as ImageProvider?,
                        child: _profileImagePath == null && profileState.employeeProfile?.profileImage == null
                          ? const Icon(Icons.person, size: 60, color: AppColors.primary)
                          : null,
                      ),
                      Positioned(
                        bottom: 0,
                        right: 0,
                        child: GestureDetector(
                          onTap: _pickAndCropImage,
                          child: Container(
                            padding: const EdgeInsets.all(8),
                            decoration: const BoxDecoration(color: AppColors.primary, shape: BoxShape.circle),
                            child: const Icon(Icons.camera_alt, color: Colors.white, size: 20),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                Center(
                  child: TextButton(
                    onPressed: _pickAndCropImage,
                    child: Text(AppStrings.get('change_photo', lang), style: const TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ),
                const SizedBox(height: 32),
                _buildLabel(AppStrings.get('full_name', lang)),
                TextFormField(controller: _nameController, decoration: _inputDecoration(lang == 'en' ? 'Your name' : (lang == 'hi' ? 'आपका नाम' : 'ನಿಮ್ಮ ಹೆಸರು')), validator: (v) => v!.isEmpty ? 'Required' : null),
                const SizedBox(height: 20),
                _buildLabel(AppStrings.get('phone_number', lang)),
                TextFormField(controller: _phoneController, keyboardType: TextInputType.phone, decoration: _inputDecoration('98765 43210', prefix: '+91 ')),
                const SizedBox(height: 20),
                _buildLabel(AppStrings.get('city', lang)),
                TextFormField(controller: _cityController, decoration: _inputDecoration(lang == 'en' ? 'e.g. Bangalore' : (lang == 'hi' ? 'जैसे: दिल्ली' : 'ಉದಾ: ಬೆಂಗಳೂರು'))),
                const SizedBox(height: 20),
                _buildLabel(AppStrings.get('expected_salary', lang)),
                TextFormField(controller: _salaryController, keyboardType: TextInputType.number, decoration: _inputDecoration(lang == 'en' ? 'e.g. 25000' : (lang == 'hi' ? 'जैसे: 25000' : 'ಉದಾ: 25000'), prefix: '₹ ')),
                const SizedBox(height: 40),
                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _save,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      elevation: 0,
                    ),
                    child: Text(AppStrings.get('save_profile', lang), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  ),
                ),
                const SizedBox(height: 100), 
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLabel(String text) => Padding(
    padding: const EdgeInsets.only(bottom: 8, left: 4),
    child: Text(text, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
  );

  InputDecoration _inputDecoration(String hint, {String? prefix}) => InputDecoration(
    hintText: hint,
    prefixText: prefix,
    prefixStyle: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary),
    filled: true,
    fillColor: AppColors.surface,
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
  );
}
