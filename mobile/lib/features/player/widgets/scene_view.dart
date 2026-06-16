import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

import '../../../models/manifest_model.dart';

/// Full-screen scene image with text overlay.
class SceneView extends StatelessWidget {
  const SceneView({super.key, required this.scene});

  final SceneModel scene;

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 600),
      child: Stack(
        key: ValueKey(scene.index),
        fit: StackFit.expand,
        children: [
          CachedNetworkImage(imageUrl: scene.imageUrl, fit: BoxFit.cover),
          Positioned(
            bottom: 80,
            left: 24,
            right: 24,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              decoration: BoxDecoration(
                color: Colors.black54,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                scene.text,
                style: const TextStyle(color: Colors.white, fontSize: 22, height: 1.4),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
