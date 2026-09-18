import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';

import '../vpn/cc_channel.dart';
import 'settings_storage.dart';

/// Lightweight daily traffic journal. Keeps today and yesterday only.
/// Daily totals come from status deltas; per-app totals come from
/// connection deltas when the core provides a package name.
class TrafficJournal extends ChangeNotifier {
  TrafficJournal._();
  static final TrafficJournal I = TrafficJournal._();

  static const _storageKey = 'traffic_journal_v2';

  Timer? _saveTimer;
  Timer? _notifyTimer;

  final Map<String, _JournalDay> _days = {};
  final Map<String, _ConnectionTotals> _lastConnections = {};

  bool _started = false;
  bool _loaded = false;
  late DateTime _startedAt;

  int _counterBaselineUp = 0;
  int _counterBaselineDown = 0;
  int _currentUpload = 0;
  int _currentDownload = 0;

  // Status snapshots are coalesced on the native side, so per-tick
  // uplink/downlink values can be skipped. Use cumulative totals instead.
  bool _statusTotalInitialized = false;
  int _lastStatusTotalUp = 0;
  int _lastStatusTotalDown = 0;

  Future<void> start() async {
    if (_started) return;
    _started = true;
    _startedAt = DateTime.now();
    await _load();
    CcChannel.instance.status.listen(_onStatus);
    CcChannel.instance.connections.listen(_onConnections);
  }

  int get currentUpload => _currentUpload;
  int get currentDownload => _currentDownload;

  int displayedUpload(int current) =>
      current >= _counterBaselineUp ? current - _counterBaselineUp : current;

  int displayedDownload(int current) =>
      current >= _counterBaselineDown ? current - _counterBaselineDown : current;

  int displayedTotal(int currentUp, int currentDown) =>
      displayedUpload(currentUp) + displayedDownload(currentDown);

  void resetCounter(int currentUp, int currentDown) {
    _counterBaselineUp = currentUp;
    _counterBaselineDown = currentDown;
    notifyListeners();
  }

  JournalSnapshot get today {
    _rotateIfNeeded();
    final day = _days[_dayKey(DateTime.now())] ?? _JournalDay();
    final apps = day.apps.entries.map((e) => JournalAppStat(
      packageName: e.key,
      upload: e.value.upload,
      download: e.value.download,
    )).toList(growable: false);
    return JournalSnapshot(
      upload: day.upload,
      download: day.download,
      apps: apps,
    );
  }

  void _onStatus(CcStatus status) {
    _currentUpload = status.uplinkTotal;
    _currentDownload = status.downlinkTotal;
    if (!_loaded) return;
    _rotateIfNeeded();

    // Do not accumulate status.uplink/downlink: those are interval deltas and
    // the native SnapshotEmitter may coalesce several status snapshots.
    // Cumulative totals let us recover the full difference even when snapshots
    // in between were dropped.
    if (!_statusTotalInitialized) {
      _lastStatusTotalUp = status.uplinkTotal;
      _lastStatusTotalDown = status.downlinkTotal;
      _statusTotalInitialized = true;
      _scheduleNotify();
      return;
    }

    final deltaUp =
        _positiveDelta(status.uplinkTotal, _lastStatusTotalUp);
    final deltaDown =
        _positiveDelta(status.downlinkTotal, _lastStatusTotalDown);
    _lastStatusTotalUp = status.uplinkTotal;
    _lastStatusTotalDown = status.downlinkTotal;

    final day = _todayDay();
    day.upload += deltaUp;
    day.download += deltaDown;
    _scheduleSave();
    _scheduleNotify();
  }

  void _onConnections(List<CcConnection> connections) {
    if (!_loaded) return;
    _rotateIfNeeded();

    for (final connection in connections) {
      final current = _ConnectionTotals(
        upload: connection.uplink,
        download: connection.downlink,
      );
      final previous = _lastConnections[connection.id];

      final firstSeenAfterStart =
          connection.createdAt <= 0 ||
          connection.createdAt >= _startedAt.millisecondsSinceEpoch;
      final deltaUp = previous == null
          ? (firstSeenAfterStart ? current.upload : 0)
          : _positiveDelta(current.upload, previous.upload);
      final deltaDown = previous == null
          ? (firstSeenAfterStart ? current.download : 0)
          : _positiveDelta(current.download, previous.download);

      _lastConnections[connection.id] = current;

      final packageName = connection.packageName.trim();
      if (packageName.isEmpty || (deltaUp == 0 && deltaDown == 0)) continue;

      final app = _todayDay().apps.putIfAbsent(packageName, _JournalApp.new);
      app.upload += deltaUp;
      app.download += deltaDown;
    }

    _scheduleSave();
    _scheduleNotify();
  }

  _JournalDay _todayDay() {
    final key = _dayKey(DateTime.now());
    return _days.putIfAbsent(key, _JournalDay.new);
  }

  void _rotateIfNeeded() {
    final now = DateTime.now();
    final today = _dayKey(now);
    final yesterday = _dayKey(DateTime(now.year, now.month, now.day - 1));
    _days.removeWhere((key, _) => key != today && key != yesterday);
    _days.putIfAbsent(today, _JournalDay.new);
  }

  String _dayKey(DateTime date) =>
      '${date.year.toString().padLeft(4, '0')}-'
      '${date.month.toString().padLeft(2, '0')}-'
      '${date.day.toString().padLeft(2, '0')}';

  int _positiveDelta(int current, int previous) =>
      current < previous ? current : current - previous;

  void _scheduleNotify() {
    if (_notifyTimer != null) return;
    _notifyTimer = Timer(const Duration(milliseconds: 500), () {
      _notifyTimer = null;
      notifyListeners();
    });
  }

  void _scheduleSave() {
    if (_saveTimer != null) return;
    _saveTimer = Timer(const Duration(seconds: 3), () async {
      _saveTimer = null;
      await _save();
    });
  }

  Future<void> _load() async {
    final raw = await SettingsStorage.getVar(_storageKey, '');
    if (raw.isNotEmpty) {
      try {
        final decoded = jsonDecode(raw);
        if (decoded is Map && decoded['days'] is Map) {
          final days = decoded['days'] as Map;
          for (final entry in days.entries) {
            if (entry.value is Map) {
              _days[entry.key.toString()] = _JournalDay.fromJson(entry.value as Map);
            }
          }
        }
      } catch (_) {
        _days.clear();
      }
    }
    _rotateIfNeeded();
    _loaded = true;
  }

  Future<void> _save() async {
    if (!_loaded) return;
    _rotateIfNeeded();
    final payload = {
      'days': {
        for (final entry in _days.entries) entry.key: entry.value.toJson(),
      },
    };
    await SettingsStorage.setVar(_storageKey, jsonEncode(payload));
  }
}

class JournalSnapshot {
  const JournalSnapshot({
    required this.upload,
    required this.download,
    required this.apps,
  });

  final int upload;
  final int download;
  final List<JournalAppStat> apps;

  int get total => upload + download;

  List<JournalAppStat> get topApps {
    final sorted = [...apps]..sort((a, b) => b.total.compareTo(a.total));
    return sorted.take(5).toList(growable: false);
  }
}

class JournalAppStat {
  const JournalAppStat({
    required this.packageName,
    required this.upload,
    required this.download,
  });

  final String packageName;
  final int upload;
  final int download;

  int get total => upload + download;
}

class _JournalDay {
  _JournalDay();

  int upload = 0;
  int download = 0;
  final Map<String, _JournalApp> apps = {};

  factory _JournalDay.fromJson(Map value) {
    final day = _JournalDay();
    day.upload = _asInt(value['upload']);
    day.download = _asInt(value['download']);
    final apps = value['apps'];
    if (apps is Map) {
      for (final entry in apps.entries) {
        if (entry.value is Map) {
          day.apps[entry.key.toString()] = _JournalApp.fromJson(entry.value as Map);
        }
      }
    }
    return day;
  }

  Map<String, Object?> toJson() => {
    'upload': upload,
    'download': download,
    'apps': {
      for (final entry in apps.entries) entry.key: entry.value.toJson(),
    },
  };

  static int _asInt(Object? value) =>
      value is num ? value.toInt() : int.tryParse('$value') ?? 0;
}

class _JournalApp {
  _JournalApp();

  int upload = 0;
  int download = 0;

  _JournalApp.fromJson(Map value)
      : upload = _JournalDay._asInt(value['upload']),
        download = _JournalDay._asInt(value['download']);

  Map<String, Object?> toJson() => {
    'upload': upload,
    'download': download,
  };
}

class _ConnectionTotals {
  const _ConnectionTotals({
    required this.upload,
    required this.download,
  });

  final int upload;
  final int download;
}
