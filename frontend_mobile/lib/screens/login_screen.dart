import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:pinput/pinput.dart';
import '../providers/providers.dart';
import '../providers/auth_provider.dart';
import '../routes/route_names.dart';
import '../theme/app_colors.dart';
import '../core/localization.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _otpController = TextEditingController();
  final _nameController = TextEditingController();
  
  @override
  void dispose() {
    _phoneController.dispose();
    _emailController.dispose();
    _otpController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _onGetOtp() async {
    final phone = _phoneController.text.trim().replaceAll(RegExp(r'[\s\-]'), '');
    if (phone.length < 10) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter a 10-digit number')),
      );
      return;
    }
    final email = _emailController.text.trim();
    if (email.isEmpty || !email.contains('@') || !email.contains('.')) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Enter a valid email address')),
      );
      return;
    }
    FocusScope.of(context).unfocus();
    final notifier = ref.read(authProvider.notifier);
    await notifier.sendOtp(phone, email: email);
    if (!mounted) return;
    final s = ref.read(authProvider);
    if (s.failure != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(s.failure!.message), backgroundColor: Colors.red),
      );
    }
  }

  Future<void> _onVerifyOtp(String pin) async {
    final phone = _phoneController.text.trim().replaceAll(RegExp(r'[\s\-]'), '');
    FocusScope.of(context).unfocus();
    final notifier = ref.read(authProvider.notifier);
    await notifier.verifyOtp(phone, pin);
    if (!mounted) return;
    final s = ref.read(authProvider);
    if (s.status == AuthStatus.authenticated && !s.isNewUser) {
      context.go(RouteNames.home);
    } else if (s.failure != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(s.failure!.message), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final lang = ref.watch(languageProvider);

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.primary),
          onPressed: () {
            if (authState.otpSent) ref.read(authProvider.notifier).resetOtp();
            else context.go(RouteNames.languageSelection);
          },
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 10),
            // Header Section
            Text(
              authState.isNewUser 
                  ? (lang == 'hi' ? 'आपका नाम?' : 'Enter Name') 
                  : (authState.otpSent ? AppStrings.get('verify_otp', lang) : AppStrings.get('welcome_title', lang)),
              style: const TextStyle(fontSize: 30, fontWeight: FontWeight.w900, color: AppColors.primary, letterSpacing: -0.5),
            ),
            const SizedBox(height: 12),
            Text(
              authState.isNewUser
                  ? 'Complete your profile to find jobs'
                  : (authState.otpSent ? '${AppStrings.get('otp_description', lang)} ${_emailController.text}' : AppStrings.get('find_job_today', lang)),
              style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
            ),
            const SizedBox(height: 40),

            // DYNAMIC CONTENT BASED ON STATE
            if (authState.isNewUser)
              _buildNameView(authState, lang)
            else if (authState.otpSent)
              _buildOtpView(authState, lang)
            else
              _buildPhoneView(authState, lang),

            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPhoneView(AuthState authState, String lang) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(AppStrings.get('phone_number', lang), style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        TextField(
          controller: _phoneController,
          keyboardType: TextInputType.phone,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          decoration: InputDecoration(
            hintText: '98765 43210',
            prefixIcon: const Padding(padding: EdgeInsets.all(14), child: Text('+91 ', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.primary))),
            filled: true,
            fillColor: AppColors.surface,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 20),
        Text(AppStrings.get('email_address', lang), style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        TextField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          autocorrect: false,
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          decoration: InputDecoration(
            hintText: 'you@example.com',
            prefixIcon: const Padding(padding: EdgeInsets.all(14), child: Icon(Icons.mail_outline, color: AppColors.primary)),
            filled: true,
            fillColor: AppColors.surface,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 32),
        SizedBox(
          width: double.infinity,
          height: 60,
          child: ElevatedButton(
            onPressed: authState.isLoginLoading ? null : _onGetOtp,
            child: authState.isLoginLoading 
              ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 3)) 
              : Text(AppStrings.get('get_otp', lang), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ),
        ),
      ],
    );
  }

  Widget _buildOtpView(AuthState authState, String lang) {
    return Column(
      children: [
        Pinput(
          length: 6,
          controller: _otpController,
          onCompleted: _onVerifyOtp,
          defaultPinTheme: PinTheme(
            width: 56, height: 60,
            textStyle: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.primary),
            decoration: BoxDecoration(color: AppColors.surface, borderRadius: BorderRadius.circular(12)),
          ),
        ),
        const SizedBox(height: 40),
        if (authState.isLoginLoading)
           const CircularProgressIndicator(color: AppColors.primary)
        else ...[
          TextButton(
            onPressed: _onGetOtp,
            child: Text(AppStrings.get('resend_otp', lang), style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary)),
          ),
          TextButton(
            onPressed: () => ref.read(authProvider.notifier).resetOtp(),
            child: Text(lang == 'hi' ? 'नंबर बदलें' : 'Change Number', style: const TextStyle(color: Colors.grey)),
          ),
        ]
      ],
    );
  }

  Widget _buildNameView(AuthState authState, String lang) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(AppStrings.get('full_name', lang), style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        TextField(
          controller: _nameController,
          autofocus: true,
          decoration: InputDecoration(
            hintText: 'Rahul Sharma',
            filled: true,
            fillColor: AppColors.surface,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 32),
        SizedBox(
          width: double.infinity,
          height: 60,
          child: ElevatedButton(
            onPressed: authState.isLoginLoading ? null : () {
              ref.read(authProvider.notifier).updateName(_nameController.text.trim());
              context.go(RouteNames.home);
            },
            child: const Text('CONTINUE', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ),
        ),
      ],
    );
  }
}
