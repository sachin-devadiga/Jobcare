import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../theme/app_colors.dart';
import '../providers/providers.dart';
import '../core/localization.dart';

class HelpSupportScreen extends ConsumerStatefulWidget {
  const HelpSupportScreen({super.key});

  @override
  ConsumerState<HelpSupportScreen> createState() => _HelpSupportScreenState();
}

class _HelpSupportScreenState extends ConsumerState<HelpSupportScreen> {
  String _selectedCategory = 'All';

  @override
  Widget build(BuildContext context) {
    final lang = ref.watch(languageProvider);
    final categories = {
      'en': ['All', 'Jobs', 'Voice', 'Account'],
      'hi': ['सभी', 'नौकरी', 'वॉयस', 'अकाउंट'],
      'kn': ['ಎಲ್ಲಾ', 'ಕೆಲಸಗಳು', 'ಧ್ವನಿ', 'ಖಾತೆ'],
    }[lang] ?? ['All', 'Jobs', 'Voice', 'Account'];

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: AppColors.primary,
        title: Text(lang == 'hi' ? 'मदद और सपोर्ट' : (lang == 'kn' ? 'ಸಹಾಯ ಮತ್ತು ಬೆಂಬಲ' : 'Help & Support'), 
          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Column(
        children: [
          _buildCategoryBar(categories),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildContactCard(
                  title: lang == 'hi' ? 'हमें ईमेल करें' : (lang == 'kn' ? 'ನಮಗೆ ಇಮೇಲ್ ಮಾಡಿ' : 'Email Us'),
                  subtitle: 'support@jobcare.com',
                  icon: Icons.email_outlined,
                  onTap: () => _launch(Uri(scheme: 'mailto', path: 'support@jobcare.com')),
                ),
                _buildContactCard(
                  title: lang == 'hi' ? 'व्हाट्सएप चैट' : (lang == 'kn' ? 'ವಾಟ್ಸಾಪ್ ಚಾಟ್' : 'WhatsApp Support'),
                  subtitle: '+91 9876543210',
                  icon: Icons.chat_outlined,
                  onTap: () => _launch(Uri.parse('https://wa.me/919876543210')),
                ),
                const SizedBox(height: 24),
                Text(lang == 'hi' ? 'अक्सर पूछे जाने वाले सवाल' : (lang == 'kn' ? 'ಪದೇ ಪದೇ ಕೇಳಲಾಗುವ ಪ್ರಶ್ನೆಗಳು' : 'Common Questions'), 
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.primary)),
                const SizedBox(height: 12),
                _buildFaqTile(lang == 'hi' ? 'नौकरी के लिए अप्लाई कैसे करें?' : (lang == 'kn' ? 'ಕೆಲಸಕ್ಕೆ ಅರ್ಜಿ ಸಲ್ಲಿಸುವುದು ಹೇಗೆ?' : 'How to apply?')),
                _buildFaqTile(lang == 'hi' ? 'वॉयस सर्च कैसे काम करता है?' : (lang == 'kn' ? 'ಧ್ವನಿ ಹುಡುಕಾಟ ಹೇಗೆ ಕೆಲಸ ಮಾಡುತ್ತದೆ?' : 'How voice search works?')),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryBar(List<String> categories) {
    return Container(
      height: 50,
      margin: const EdgeInsets.symmetric(vertical: 16),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final isSelected = _selectedCategory == categories[index];
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(categories[index]),
              selected: isSelected,
              onSelected: (val) => setState(() => _selectedCategory = categories[index]),
              selectedColor: AppColors.primary,
              labelStyle: TextStyle(color: isSelected ? Colors.white : AppColors.primary, fontWeight: FontWeight.bold),
              backgroundColor: AppColors.primary.withOpacity(0.05),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20), side: BorderSide.none),
              showCheckmark: false,
            ),
          );
        },
      ),
    );
  }

  Widget _buildContactCard({required String title, required String subtitle, required IconData icon, required VoidCallback onTap}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: ListTile(
        leading: Icon(icon, color: AppColors.primary),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.open_in_new, size: 18, color: Colors.grey),
        onTap: onTap,
      ),
    );
  }

  Future<void> _launch(Uri uri) async {
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication) && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Unable to open support link.')));
    }
  }

  Widget _buildFaqTile(String question) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      title: Text(question, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
      trailing: const Icon(Icons.add, size: 20, color: AppColors.primary),
      onTap: () => showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(title: Text(question), content: const Text('For help with this topic, contact JobCare support.'), actions: [TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close'))]),
      ),
    );
  }
}
