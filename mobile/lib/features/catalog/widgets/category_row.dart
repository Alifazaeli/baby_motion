import 'package:flutter/material.dart';

import '../../../models/category_model.dart';
import '../../../models/story_model.dart';
import 'story_card.dart';

/// FR-A4: A horizontal scrolling row of story cards within a category.
class CategoryRow extends StatelessWidget {
  const CategoryRow({super.key, required this.category, required this.stories});

  final CategoryModel category;
  final List<StoryModel> stories;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 8),
          child: Text(category.name, style: Theme.of(context).textTheme.titleLarge),
        ),
        SizedBox(
          height: 220,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            itemCount: stories.length,
            itemBuilder: (context, i) => StoryCard(story: stories[i]),
          ),
        ),
      ],
    );
  }
}
