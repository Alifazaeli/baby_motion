import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

import '../../../models/story_model.dart';

/// FR-A4: Tappable card showing story cover, title, and duration.
class StoryCard extends StatelessWidget {
  const StoryCard({super.key, required this.story});

  final StoryModel story;

  @override
  Widget build(BuildContext context) {
    final minutes = (story.durationSeconds / 60).ceil();
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: () => Navigator.of(context).pushNamed('/story', arguments: story),
      child: Container(
        width: 150,
        margin: const EdgeInsets.symmetric(horizontal: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: CachedNetworkImage(
                imageUrl: story.coverUrl,
                height: 150,
                width: 150,
                fit: BoxFit.cover,
                placeholder: (_, __) => Container(
                  color: theme.colorScheme.surfaceVariant,
                  child: const Center(child: CircularProgressIndicator()),
                ),
                errorWidget: (_, __, ___) => Container(
                  color: theme.colorScheme.surfaceVariant,
                  child: const Icon(Icons.auto_stories, size: 48),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(story.title, maxLines: 2, overflow: TextOverflow.ellipsis,
                style: theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w700)),
            Text('$minutes min', style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            )),
          ],
        ),
      ),
    );
  }
}
