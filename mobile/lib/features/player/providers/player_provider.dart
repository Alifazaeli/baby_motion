import 'package:flutter/foundation.dart';
import 'package:just_audio/just_audio.dart';

import '../../../models/manifest_model.dart';

/// Manages audio playback and scene advancement for the story player (FR-A6).
class PlayerProvider extends ChangeNotifier {
  PlayerProvider() : _player = AudioPlayer();

  final AudioPlayer _player;

  ManifestModel? _manifest;
  int _currentSceneIndex = 0;
  bool _isPlaying = false;
  int _scenesWatched = 0;

  ManifestModel? get manifest => _manifest;
  int get currentSceneIndex => _currentSceneIndex;
  bool get isPlaying => _isPlaying;
  int get scenesWatched => _scenesWatched;
  SceneModel? get currentScene =>
      _manifest != null && _currentSceneIndex < _manifest!.scenes.length
          ? _manifest!.scenes[_currentSceneIndex]
          : null;

  Future<void> load(ManifestModel manifest) async {
    _manifest = manifest;
    _currentSceneIndex = 0;
    _scenesWatched = 0;
    await _player.setUrl(manifest.audioUrl);
    _player.positionStream.listen(_onPositionChanged);
    notifyListeners();
  }

  void _onPositionChanged(Duration position) {
    final scene = currentScene;
    if (scene == null) return;
    if (position.inMilliseconds / 1000 >= scene.audioEndSec) {
      if (_currentSceneIndex < _manifest!.scenes.length - 1) {
        _currentSceneIndex++;
        _scenesWatched = _currentSceneIndex + 1;
        notifyListeners();
      }
    }
  }

  Future<void> play() async {
    await _player.play();
    _isPlaying = true;
    notifyListeners();
  }

  Future<void> pause() async {
    await _player.pause();
    _isPlaying = false;
    notifyListeners();
  }

  Future<void> togglePlayPause() async {
    _isPlaying ? await pause() : await play();
  }

  Future<void> previousScene() async {
    if (_currentSceneIndex > 0) {
      _currentSceneIndex--;
      final scene = currentScene!;
      await _player.seek(Duration(milliseconds: (scene.audioStartSec * 1000).toInt()));
      notifyListeners();
    }
  }

  Future<void> nextScene() async {
    if (_manifest != null && _currentSceneIndex < _manifest!.scenes.length - 1) {
      _currentSceneIndex++;
      _scenesWatched = _currentSceneIndex + 1;
      final scene = currentScene!;
      await _player.seek(Duration(milliseconds: (scene.audioStartSec * 1000).toInt()));
      notifyListeners();
    }
  }

  Future<void> replay() async {
    _currentSceneIndex = 0;
    await _player.seek(Duration.zero);
    await play();
    notifyListeners();
  }

  bool get isComplete =>
      _manifest != null && _currentSceneIndex >= _manifest!.scenes.length - 1 && !_isPlaying;

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }
}
