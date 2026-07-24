import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import '../core/theme.dart';

class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double borderRadius;
  final double blur;
  final double opacity;
  final VoidCallback? onTap;

  const GlassCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.margin,
    this.borderRadius = 16,
    this.blur = 10,
    this.opacity = 0.15,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final decoration = AppTheme.glassDecoration(
      blur: blur,
      opacity: opacity,
      borderRadius: borderRadius,
    );

    return Container(
      margin: margin,
      decoration: decoration,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: onTap,
            child: Padding(
              padding: padding!,
              child: BackdropFilter(
                filter: ui.ImageFilter.blur(
                  sigmaX: blur / 2,
                  sigmaY: blur / 2,
                ),
                child: child,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
