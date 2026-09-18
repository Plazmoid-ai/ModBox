import 'package:flutter/material.dart';

import '../../services/app_info_cache.dart';
import '../../services/format_utils.dart';
import '../../services/l10n/locale_controller.dart';
import '../../services/traffic_journal.dart';

Future<void> showTrafficJournalSheet(
  BuildContext context, {
  required int currentUp,
  required int currentDown,
}) {
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    builder: (_) => _TrafficJournalSheet(
      currentUp: currentUp,
      currentDown: currentDown,
    ),
  );
}

class _TrafficJournalSheet extends StatelessWidget {
  const _TrafficJournalSheet({
    required this.currentUp,
    required this.currentDown,
  });

  final int currentUp;
  final int currentDown;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return AnimatedBuilder(
      animation: TrafficJournal.I,
      builder: (context, _) {
        final journal = TrafficJournal.I.today;
        final topApps = journal.topApps;
        final maxApp = topApps.isEmpty ? 0 : topApps.first.total;

        return DraggableScrollableSheet(
          initialChildSize: 0.56,
          minChildSize: 0.4,
          maxChildSize: 0.85,
          expand: false,
          builder: (context, scrollController) => Column(
            children: [
              Container(
                width: 36,
                height: 4,
                margin: const EdgeInsets.symmetric(vertical: 10),
                decoration: BoxDecoration(
                  color: cs.onSurfaceVariant.withValues(alpha: 0.4),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                child: Row(
                  children: [
                    Icon(Icons.swap_vert, size: 20, color: cs.secondary),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        getLocalText.s("Traffic today"),
                        style: const TextStyle(
                          fontSize: 15,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    Text(
                      formatBytes(journal.total, spaced: true),
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: cs.secondary,
                      ),
                    ),
                  ],
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
                child: Row(
                  children: [
                    Text(
                      '↑ ${formatBytes(journal.upload, spaced: true)}',
                      style: TextStyle(fontSize: 12, color: cs.primary),
                    ),
                    const SizedBox(width: 16),
                    Text(
                      '↓ ${formatBytes(journal.download, spaced: true)}',
                      style: TextStyle(fontSize: 12, color: cs.tertiary),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),
              Expanded(
                child: ListView(
                  controller: scrollController,
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                  children: [
                    Text(
                      getLocalText.s("Top applications"),
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5,
                        color: cs.primary,
                      ),
                    ),
                    const SizedBox(height: 6),
                    if (topApps.isEmpty)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        child: Text(
                          getLocalText.s("No app traffic recorded yet"),
                          style: TextStyle(
                            fontSize: 12,
                            color: cs.onSurfaceVariant,
                          ),
                        ),
                      )
                    else
                      ...topApps.map(
                        (app) => _AppTrafficRow(
                          stat: app,
                          maxTotal: maxApp,
                        ),
                      ),
                    const SizedBox(height: 12),
                    const Divider(height: 1),
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: Icon(Icons.restart_alt, color: cs.onSurfaceVariant),
                      title: Text(
                        getLocalText.s("Reset current counter"),
                        style: const TextStyle(fontSize: 14),
                      ),
                      subtitle: Text(
                        getLocalText.s("Does not affect the traffic journal"),
                        style: TextStyle(
                          fontSize: 11,
                          color: cs.onSurfaceVariant,
                        ),
                      ),
                      onTap: () {
                        TrafficJournal.I.resetCounter(currentUp, currentDown);
                      },
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _AppTrafficRow extends StatelessWidget {
  const _AppTrafficRow({
    required this.stat,
    required this.maxTotal,
  });

  final JournalAppStat stat;
  final int maxTotal;

  @override
  Widget build(BuildContext context) {
    AppInfoCache.ensure(stat.packageName);
    final info = AppInfoCache.of(stat.packageName);
    final name = info?.appName.isNotEmpty == true
        ? info!.appName
        : stat.packageName;

    final cs = Theme.of(context).colorScheme;
    final fraction =
        maxTotal == 0 ? 0.0 : (stat.total / maxTotal).clamp(0.0, 1.0);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  name,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 13),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                formatBytes(stat.total, spaced: true),
                style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
              ),
            ],
          ),
          const SizedBox(height: 4),
          ClipRRect(
            borderRadius: BorderRadius.circular(2),
            child: LinearProgressIndicator(
              value: fraction,
              minHeight: 4,
              backgroundColor: cs.surfaceContainerHighest,
            ),
          ),
        ],
      ),
    );
  }
}
