import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import '../theme/app_colors.dart';

class RatingBarWidget extends StatelessWidget {
  final double rating;
  final double itemSize;
  final bool readOnly;
  final ValueChanged<double>? onRatingUpdate;

  const RatingBarWidget({
    super.key,
    this.rating = 0,
    this.itemSize = 20,
    this.readOnly = true,
    this.onRatingUpdate,
  });

  @override
  Widget build(BuildContext context) {
    return RatingBar.builder(
      initialRating: rating,
      minRating: 1,
      direction: Axis.horizontal,
      allowHalfRating: true,
      itemCount: 5,
      itemSize: itemSize,
      unratedColor: Colors.grey.shade200,
      itemBuilder: (context, _) => const Icon(
        Icons.star_rounded,
        color: AppColors.secondary, // Amber color for Apna style stars
      ),
      onRatingUpdate: onRatingUpdate ?? (_) {},
      ignoreGestures: readOnly,
    );
  }
}
