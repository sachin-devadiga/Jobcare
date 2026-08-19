import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:pinput/pinput.dart';
import '../providers/providers.dart';
import '../providers/auth_provider.dart';
import '../routes/route_names.dart';
import '../theme/app_colors.dart';
import '../core/utils.dart';
import '../core/localization.dart';

class SignupScreen extends ConsumerStatefulWidget {
  const SignupScreen({super.key});

  @override
  ConsumerState<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends ConsumerState<SignupScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _otpController = TextEditingController();
  bool _otpSent = false;
  bool _isSendingOtp = false;

  @override
  void dispose() {
    _nameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _sendOtp() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSendingOtp = true);
    final notifier = ref.read(authProvider.notifier);
    await notifier.sendOtp(_phoneController.text.trim(), email: _emailController.text.trim());
    if (!mounted) return;
    setState(() {
      _isSendingOtp = false;
      final state = ref.read(authProvider);
      if (state.failure != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(state.failure!.message), backgroundColor: Colors.red),
        );
        _otpSent = false;
      } else {
        _otpSent = true;
      }
    });
  }

  void _verifyOtp(String pin) {
    ref.read(authProvider.notifier).verifyOtp(_phoneController.text.trim(), pin).then((_) {
      if (mounted && ref.read(authProvider).status == AuthStatus.authenticated) {
        context.go(RouteNames.home);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.primary),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _otpSent ? AppStrings.get('verify_otp', lang) : AppStrings.get('create_account', lang),
              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w900, color: AppColors.primary),
            ),
            const SizedBox(height: 8),
            Text(
              _otpSent 
                ? AppStrings.get('enter_otp', lang) 
                : (lang == 'hi' ? 'हर दिन नौकरी पाने वाले हजारों श्रमिकों से जुड़ें' : (lang == 'kn' ? 'ಪ್ರತಿದಿನ ಕೆಲಸ ಹುಡುಕುವ ಸಾವಿರಾರು ಉದ್ಯೋಗಿಗಳೊಂದಿಗೆ ಸೇರಿ' : 'Join thousands of workers finding jobs daily')),
              style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 40),
            Form(
              key: _formKey,
              child: _otpSent ? _buildOtpSection(lang) : _buildDetailsSection(lang),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailsSection(String lang) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildLabel(AppStrings.get('full_name', lang)),
        TextFormField(
          controller: _nameController,
          decoration: _inputDecoration(lang == 'hi' ? 'अपना नाम लिखें' : (lang == 'kn' ? 'ನಿಮ್ಮ ಹೆಸರು ಬರೆಯಿರಿ' : 'Enter your name')),
          validator: (v) => v!.isEmpty ? 'Required' : null,
        ),
        const SizedBox(height: 20),
        _buildLabel(AppStrings.get('phone_number', lang)),
        TextFormField(
          controller: _phoneController,
          keyboardType: TextInputType.phone,
          decoration: _inputDecoration('98765 43210', prefix: '+91 '),
          validator: (v) => v!.length < 10 ? 'Invalid' : null,
        ),
        const SizedBox(height: 20),
        _buildLabel(AppStrings.get('email_address', lang)),
        TextFormField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          autocorrect: false,
          decoration: _inputDecoration('you@example.com'),
          validator: (v) => (v == null || v.isEmpty || !v.contains('@') || !v.contains('.'))
              ? 'Enter a valid email address'
              : null,
        ),
        const SizedBox(height: 40),
        SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton(
            onPressed: _sendOtp,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              elevation: 0,
            ),
            child: _isSendingOtp 
              ? const CircularProgressIndicator(color: Colors.white)
              : Text(AppStrings.get('continue', lang), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
          ),
        ),
      ],
    );
  }

  Widget _buildOtpSection(String lang) {
    return Column(
      children: [
        Pinput(
          length: 6,
          controller: _otpController,
          onCompleted: _verifyOtp,
          defaultPinTheme: PinTheme(
            width: 50, height: 56,
            textStyle: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.primary),
            decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(12)),
          ),
        ),
        const SizedBox(height: 32),
        TextButton(
          onPressed: () => setState(() => _otpSent = false),
          child: Text(
            lang == 'hi' ? 'फ़ोन नंबर बदलें' : (lang == 'kn' ? 'ಫೋನ್ ಸಂಖ್ಯೆ ಬದಲಾಯಿಸಿ' : 'Change Phone Number'),
            style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold)
          ),
        ),
      ],
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
