import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/services/api_service.dart';
import '../../../models/manifest_model.dart';
import '../../../models/story_model.dart';
import '../../auth/providers/auth_provider.dart';
import '../providers/player_provider.dart';
import '../widgets/player_controls.dart';
import '../widgets/scene_view.dart';

/// FR-A6: Full-screen story player with audio sync and scene transitions.
class PlayerScreen extends StatefulWidget {
  const PlayerScreen({super.key, required this.story});

  final StoryModel story;

  @override
  State<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends State<PlayerScreen> {
  String? _sessionId;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _init());
  }

  Future<void> _init() async {
    final api = context.read<ApiService>();
    final child = context.read<AuthProvider>().child;
    if (child == null) return;

    try {
      // Start analytics session
      final sessionRes = await api.post<Map<String, dynamic>>(
        ApiConstants.startStory(widget.story.id),
        data: {'child_id': child.id, 'language': child.language},
      );
      _sessionId = sessionRes.data!['session_id'] as String;

      // Fetch and parse manifest
      final manifestRes = await Dio().get<String>(widget.story.manifestUrl);
      final manifest = ManifestModel.fromJson(
        jsonDecode(manifestRes.data!) as Map<String, dynamic>,
      );

      await context.read<PlayerProvider>().load(manifest);
      await context.read<PlayerProvider>().play();

      if (mounted) setState(() => _loading = false);
    } catch (e) {
      if (mounted) setState(() {
        _loading = false;
        _error = e.toString();
      });
    }
  }

  Future<void> _exit({bool completed = false}) async {
    final player = context.read<PlayerProvider>();
    final api = context.read<ApiService>();
    if (_sessionId != null) {
      try {
        final endpoint = completed
            ? ApiConstants.completeSession(_sessionId!)
            : ApiConstants.abandonSession(_sessionId!);
        await api.post<void>(endpoint, data: {'scenes_watched': player.scenesWatched});
      } catch (_) {}
    }
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (_error != null) {
      return Scaffold(
        body: Center(child: Text(_error!)),
        appBar: AppBar(),
      );
    }

    final player = context.watch<PlayerProvider>();
    final scene = player.currentScene;

    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          children: [
            if (scene != null) SceneView(scene: scene),
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              child: PlayerControls(
                isPlaying: player.isPlaying,
                onPlayPause: player.togglePlayPause,
                onPrevious: player.previousScene,
                onNext: player.nextScene,
                onReplay: player.replay,
                onExit: () => _exit(completed: player.isComplete),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
