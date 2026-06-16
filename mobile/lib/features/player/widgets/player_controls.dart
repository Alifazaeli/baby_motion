import 'package:flutter/material.dart';

/// FR-A6: Player controls: play/pause, previous/next scene, replay, exit.
class PlayerControls extends StatelessWidget {
  const PlayerControls({
    super.key,
    required this.isPlaying,
    required this.onPlayPause,
    required this.onPrevious,
    required this.onNext,
    required this.onReplay,
    required this.onExit,
  });

  final bool isPlaying;
  final VoidCallback onPlayPause;
  final VoidCallback onPrevious;
  final VoidCallback onNext;
  final VoidCallback onReplay;
  final VoidCallback onExit;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.bottomCenter,
          end: Alignment.topCenter,
          colors: [Colors.black87, Colors.transparent],
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _ControlButton(icon: Icons.close, onTap: onExit, tooltip: 'Exit'),
          _ControlButton(icon: Icons.skip_previous, onTap: onPrevious, tooltip: 'Previous'),
          _ControlButton(
            icon: isPlaying ? Icons.pause_circle_filled : Icons.play_circle_filled,
            onTap: onPlayPause,
            size: 64,
            tooltip: isPlaying ? 'Pause' : 'Play',
          ),
          _ControlButton(icon: Icons.skip_next, onTap: onNext, tooltip: 'Next'),
          _ControlButton(icon: Icons.replay, onTap: onReplay, tooltip: 'Replay'),
        ],
      ),
    );
  }
}

class _ControlButton extends StatelessWidget {
  const _ControlButton({
    required this.icon,
    required this.onTap,
    required this.tooltip,
    this.size = 44,
  });

  final IconData icon;
  final VoidCallback onTap;
  final String tooltip;
  final double size;

  @override
  Widget build(BuildContext context) => IconButton(
        icon: Icon(icon, color: Colors.white, size: size),
        onPressed: onTap,
        tooltip: tooltip,
        constraints: BoxConstraints(minWidth: size, minHeight: size),
      );
}
