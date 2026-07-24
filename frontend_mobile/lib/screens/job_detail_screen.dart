import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/providers.dart';
import '../theme/app_colors.dart';
import '../providers/job_provider.dart';
import '../widgets/voice_ring.dart';
import '../core/localization.dart';

class JobDetailScreen extends ConsumerStatefulWidget {
  final String jobId;
  const JobDetailScreen({super.key, required this.jobId});

  @override
  ConsumerState<JobDetailScreen> createState() => _JobDetailScreenState();
}

class _JobDetailScreenState extends ConsumerState<JobDetailScreen> {
  bool _isVetting = false;
  bool _isSubmitting = false;
  int _vettingStep = 0;
  final List<String> _voiceAnswers = [];

  List<String> _getQuestions(String lang) {
    switch (lang) {
      case 'hi':
        return [
          "Aapke paas valid Driving License hai?",
          "Aap kabse kaam shuru kar sakte hain?",
          "Bangalore mein aap kahan rehte hain?"
        ];
      case 'kn':
        return [
          "Nimmalli chalana paravanagi (Driving License) ideye?",
          "Neevu yavaginda kelasa prarambhisa bahudu?",
          "Bangalore nalli neevu elli vaasisidira?"
        ];
      default:
        return [
          "Do you have a valid Driving License?",
          "When can you start working?",
          "Where do you live in Bangalore?"
        ];
    }
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(jobProvider.notifier).fetchJobDetail(widget.jobId);
    });
  }

  void _startVetting() {
    setState(() {
      _isVetting = true;
      _vettingStep = 0;
      _voiceAnswers.clear();
    });
  }

  Future<void> _nextStep(List<String> questions) async {
    // Record dummy answer for simulation, in real app this would capture audio path
    _voiceAnswers.add("Recorded Answer for Step $_vettingStep");

    if (_vettingStep < questions.length - 1) {
      setState(() => _vettingStep++);
    } else {
      await _submitApplication();
    }
  }

  Future<void> _submitApplication() async {
    setState(() {
      _isVetting = false;
      _isSubmitting = true;
    });

    try {
      // API call to save the application with voice answers
      await ref.read(applicationProvider.notifier).apply(
        jobId: widget.jobId,
      );
      if (mounted) _showSuccessDialog();
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Failed to submit application. Try again.'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  Future<void> _makeCall(String phoneNumber) async {
    final Uri launchUri = Uri(scheme: 'tel', path: phoneNumber);
    if (await canLaunchUrl(launchUri)) {
      await launchUrl(launchUri);
    }
  }

  void _showSuccessDialog() {
    final lang = ref.read(languageProvider);
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
        title: Row(
          children: [
            const Icon(Icons.check_circle, color: AppColors.success, size: 30),
            const SizedBox(width: 12),
            Text(AppStrings.get('applied', lang), style: const TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        content: Text(
          AppStrings.get('applied_success', lang),
          style: const TextStyle(fontSize: 15, height: 1.5),
        ),
        actions: [
          ElevatedButton.icon(
            onPressed: () {
              Navigator.pop(ctx);
              _makeCall('9876543210');
            },
            icon: const Icon(Icons.call, color: Colors.white),
            label: Text(AppStrings.get('call_hr', lang), 
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.primary,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(jobProvider);
    final interfaceLang = ref.watch(languageProvider);
    final job = state.selectedJob;
    final questions = _getQuestions(interfaceLang);

    if (job == null) return const Scaffold(body: Center(child: CircularProgressIndicator()));

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(job.company?.name ?? 'Details', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Stack(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildJobHeader(job, interfaceLang),
                const SizedBox(height: 32),
                Text(AppStrings.get('job_description', interfaceLang), 
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppColors.primary)),
                const SizedBox(height: 12),
                Text(job.description ?? '', style: TextStyle(fontSize: 15, color: AppColors.textPrimary.withOpacity(0.7), height: 1.6)),
                const SizedBox(height: 120),
              ],
            ),
          ),
          if (_isSubmitting) const Center(child: CircularProgressIndicator()),
          if (_isVetting) _buildVettingOverlay(questions, interfaceLang),
        ],
      ),
      bottomNavigationBar: (_isVetting || _isSubmitting) ? null : _buildBottomAction(interfaceLang),
    );
  }

  Widget _buildJobHeader(dynamic job, String lang) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          Text(job.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.primary)),
          const SizedBox(height: 8),
          Text('₹${job.salaryMin} - ₹${job.salaryMax}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.success)),
        ],
      ),
    );
  }

  Widget _buildVettingOverlay(List<String> questions, String lang) {
    return Container(
      color: AppColors.primary.withOpacity(0.98),
      width: double.infinity,
      height: double.infinity,
      child: SafeArea(
        child: Column(
          children: [
            const Spacer(),
            const VoiceRing(size: 140, state: VoiceRingState.listening),
            const SizedBox(height: 40),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 40),
              child: Text(
                questions[_vettingStep],
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white, fontSize: 26, fontWeight: FontWeight.bold),
              ),
            ),
            const Spacer(),
            Padding(
              padding: const EdgeInsets.all(40),
              child: ElevatedButton(
                onPressed: () => _nextStep(questions),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.secondary,
                  foregroundColor: Colors.black,
                  minimumSize: const Size(double.infinity, 64),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
                child: Text(AppStrings.get('speak_to_answer', lang), 
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomAction(String lang) {
    return Container(
      padding: const EdgeInsets.fromLTRB(24, 12, 24, 32),
      decoration: const BoxDecoration(color: Colors.white),
      child: SafeArea(
        child: ElevatedButton.icon(
          onPressed: _startVetting,
          icon: const Icon(Icons.mic_rounded),
          label: Text(AppStrings.get('bol_kar_apply', lang), 
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.secondary,
            foregroundColor: Colors.black,
            minimumSize: const Size(double.infinity, 64),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          ),
        ),
      ),
    );
  }
}
