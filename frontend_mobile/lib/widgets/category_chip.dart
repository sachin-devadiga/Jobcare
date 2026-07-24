import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/category_model.dart';
import '../theme/app_colors.dart';
import '../providers/providers.dart';

class CategoryChip extends ConsumerWidget {
  final CategoryModel category;
  final VoidCallback? onTap;

  const CategoryChip({
    super.key,
    required this.category,
    this.onTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lang = ref.watch(languageProvider);
    
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 100,
        margin: const EdgeInsets.only(right: 16, top: 4, bottom: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: AppColors.primary.withOpacity(0.04),
              blurRadius: 10,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 54,
              height: 54,
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(18),
              ),
              child: Icon(
                _getCategoryIcon(category.name),
                color: AppColors.primary,
                size: 26,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              _getLocalizedCategoryName(category.name, lang),
              style: const TextStyle(
                fontWeight: FontWeight.w800,
                fontSize: 13,
                color: AppColors.primary,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 2),
            Text(
              lang == 'en' ? '${category.jobCount} Jobs' : (lang == 'hi' ? '${category.jobCount} नौकरियां' : '${category.jobCount} ಕೆಲಸಗಳು'),
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: AppColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getLocalizedCategoryName(String name, String lang) {
    if (lang == 'en') return name;
    
    final map = {
      'Construction': {'hi': 'निर्माण', 'kn': 'ನಿರ್ಮಾಣ'},
      'Delivery': {'hi': 'डिलीवरी', 'kn': 'ಡೆಲಿವರಿ'},
      'Driver': {'hi': 'ड्राइवर', 'kn': 'ಚಾಲಕ'},
      'Cleaning': {'hi': 'सफाई', 'kn': 'ಶುಚಿಗೊಳಿಸುವಿಕೆ'},
      'Security': {'hi': 'सुरक्षा', 'kn': 'ಭದ್ರತೆ'},
      'Cooking': {'hi': 'खाना बनाना', 'kn': 'ಅಡುಗೆ'},
      'Warehouse': {'hi': 'गोदाम', 'kn': 'ಗೋದಾಮು'},
      'Factory': {'hi': 'फैक्ट्री', 'kn': 'ಕಾರ್ಖಾನೆ'},
      'Retail': {'hi': 'रिटेल', 'kn': 'ಚಿಲ್ಲರೆ ಮಾರಾಟ'},
    };
    
    return map[name]?[lang] ?? name;
  }

  IconData _getCategoryIcon(String name) {
    switch (name.toLowerCase()) {
      case 'construction': return Icons.construction_rounded;
      case 'delivery': return Icons.delivery_dining_rounded;
      case 'driver': return Icons.directions_car_rounded;
      case 'cleaning': return Icons.cleaning_services_rounded;
      case 'security': return Icons.security_rounded;
      case 'cooking': return Icons.restaurant_rounded;
      case 'plumbing': return Icons.plumbing_rounded;
      case 'electrical': return Icons.electrical_services_rounded;
      case 'warehouse': return Icons.inventory_2_rounded;
      case 'factory': return Icons.factory_rounded;
      case 'retail': return Icons.store_rounded;
      default: return Icons.work_rounded;
    }
  }
}
