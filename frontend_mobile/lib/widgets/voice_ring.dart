import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

enum VoiceRingState { idle, listening, processing }

class VoiceRing extends StatefulWidget {
  final double size;
  final VoiceRingState state;

  const VoiceRing({
    super.key,
    this.size = 48,
    this.state = VoiceRingState.idle,
  });

  @override
  State<VoiceRing> createState() => _VoiceRingState();
}

class _VoiceRingState extends State<VoiceRing>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: _durationForState(widget.state),
    );
    _syncAnimation();
  }

  @override
  void didUpdateWidget(VoiceRing oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.state != widget.state) {
      _controller.duration = _durationForState(widget.state);
      _syncAnimation();
    }
  }

  Duration _durationForState(VoiceRingState state) {
    switch (state) {
      case VoiceRingState.idle:
        return Duration.zero;
      case VoiceRingState.listening:
        return const Duration(milliseconds: 1200);
      case VoiceRingState.processing:
        return const Duration(milliseconds: 2000);
    }
  }

  void _syncAnimation() {
    switch (widget.state) {
      case VoiceRingState.idle:
        _controller.stop();
        _controller.value = 0;
      case VoiceRingState.listening:
      case VoiceRingState.processing:
        _controller.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ringWidth = math.max(2.0, widget.size * 0.055);
    final micSize = widget.size * 0.55;
    final innerRadius = widget.size * 0.4;

    Color ringColor;
    Color micColor;

    switch (widget.state) {
      case VoiceRingState.idle:
        ringColor = Colors.transparent;
        micColor = AppColors.navy; // Navy icon on Marigold background
      case VoiceRingState.listening:
        ringColor = AppColors.navy.withOpacity(0.3);
        micColor = AppColors.navy;
      case VoiceRingState.processing:
        ringColor = AppColors.navy.withOpacity(0.2);
        micColor = AppColors.navy;
    }

    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          if (widget.state != VoiceRingState.idle)
            AnimatedBuilder(
              animation: _controller,
              builder: (_, __) => CustomPaint(
                size: Size(widget.size, widget.size),
                painter: _PulseRingsPainter(
                  progress: _controller.value,
                  color: ringColor,
                  innerRadius: innerRadius,
                  ringWidth: ringWidth,
                  pulseCount: widget.state == VoiceRingState.listening ? 3 : 1,
                  maxExpansion: widget.state == VoiceRingState.listening ? 0.35 : 0.08,
                ),
              ),
            ),
          Icon(Icons.mic_rounded, size: micSize, color: micColor),
        ],
      ),
    );
  }
}

class _PulseRingsPainter extends CustomPainter {
  final double progress;
  final Color color;
  final double innerRadius;
  final double ringWidth;
  final int pulseCount;
  final double maxExpansion;

  _PulseRingsPainter({
    required this.progress,
    required this.color,
    required this.innerRadius,
    required this.ringWidth,
    required this.pulseCount,
    required this.maxExpansion,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);

    for (int i = 0; i < pulseCount; i++) {
      final phase = (progress + i / pulseCount) % 1.0;
      final expansion = phase * maxExpansion * innerRadius;
      final radius = innerRadius + expansion;
      final opacity = (1.0 - phase) * 0.45;
      final paint = Paint()
        ..color = color.withOpacity(opacity)
        ..style = PaintingStyle.stroke
        ..strokeWidth = ringWidth;

      canvas.drawCircle(center, radius, paint);
    }
  }

  @override
  bool shouldRepaint(_PulseRingsPainter oldDelegate) =>
      oldDelegate.progress != progress || oldDelegate.color != color;
}
