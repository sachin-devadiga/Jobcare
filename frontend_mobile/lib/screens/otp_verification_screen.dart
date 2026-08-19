import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:pin_code_fields/pin_code_fields.dart';
import '../providers/providers.dart';
import '../providers/auth_provider.dart';
import '../routes/route_names.dart';
import '../theme/app_colors.dart';
import '../core/localization.dart';

class OtpVerificationScreen extends ConsumerStatefulWidget {
  final String? phone;

  const OtpVerificationScreen({
    super.key,
    this.phone,
  });

  @override
  ConsumerState<OtpVerificationScreen> createState() => _OtpVerificationScreenState();
}

class _OtpVerificationScreenState extends ConsumerState<OtpVerificationScreen> {
  int _resendTimer = 30;
  bool _canResend = false;
  bool _isVerifying = false;
  final _otpController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _startResendTimer();
  }

  void _startResendTimer() {
    setState(() {
      _canResend = false;
      _resendTimer = 30;
    });
    Future.doWhile(() async {
      await Future.delayed(const Duration(seconds: 1));
      if (!mounted) return false;
      setState(() {
        if (_resendTimer > 0) {
          _resendTimer--;
        } else {
          _canResend = true;
        }
      });
      return _resendTimer > 0;
    });
  }

  @override
  void dispose() {
    _otpController.dispose();
    super.dispose();
  }

  Future<void> _verifyOtp(String otp) async {
    if (otp.length != 6) return;
    setState(() => _isVerifying = true);

    try {
      if (widget.phone != null) {
        await ref.read(authProvider.notifier).verifyOtp(widget.phone!, otp);
      }

      if (!mounted) return;
      final authState = ref.read(authProvider);
      if (authState.status == AuthStatus.authenticated) {
        context.go(RouteNames.home);
      }
    } catch (_) {} finally {
      if (mounted) setState(() => _isVerifying = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = ref.watch(languageProvider);
    final displayPhone = widget.phone != null ? '+91 ${widget.phone}' : '';

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
            const SizedBox(height: 20),
            Text(
              AppStrings.get('verify_otp', lang),
              style: const TextStyle(fontSize: 30, fontWeight: FontWeight.w900, color: AppColors.primary),
            ),
            const SizedBox(height: 12),
            Text(
              '${AppStrings.get('otp_description', lang)} $displayPhone',
              style: TextStyle(fontSize: 16, color: Colors.grey.shade600, height: 1.5),
            ),
            const SizedBox(height: 40),
            PinCodeTextField(
              appContext: context,
              length: 6,
              controller: _otpController,
              onCompleted: _verifyOtp,
              pinTheme: PinTheme(
                shape: PinCodeFieldShape.box,
                borderRadius: BorderRadius.circular(12),
                fieldHeight: 56,
                fieldWidth: 46,
                activeColor: AppColors.primary,
                selectedColor: AppColors.primary,
                inactiveColor: AppColors.surface,
                activeFillColor: AppColors.surface,
                selectedFillColor: Colors.white,
                inactiveFillColor: AppColors.surface,
              ),
              enableActiveFill: true,
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _isVerifying ? null : () => _verifyOtp(_otpController.text),
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                child: _isVerifying 
                  ? const CircularProgressIndicator(color: Colors.white) 
                  : Text(AppStrings.get('verify', lang), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 32),
            Center(
              child: Column(
                children: [
                  Text(AppStrings.get('didnt_receive', lang), style: TextStyle(color: Colors.grey.shade600)),
                  const SizedBox(height: 8),
                  _canResend
                    ? TextButton(
                        onPressed: () => _startResendTimer(),
                        child: Text(AppStrings.get('resend', lang), style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary)),
                      )
                    : Text('${AppStrings.get('resend_in', lang)} $_resendTimer s', style: const TextStyle(color: Colors.grey)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
