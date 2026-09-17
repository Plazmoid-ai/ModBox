from pathlib import Path

helper = Path('app/lib/widgets/compact_description.dart')
s = helper.read_text(encoding='utf-8')
s = s.replace("    this.collapseAbove = 140,\n", "    this.maxLinesBeforeCollapse = 3,\n")
s = s.replace("  final int collapseAbove;\n", "  final int maxLinesBeforeCollapse;\n")
start = s.index('  @override\n  Widget build(BuildContext context) {')
end = s.index('\n  }\n}', start) + len('\n  }')
new_build = '''  @override
  Widget build(BuildContext context) {
    final style = widget.style ?? DefaultTextStyle.of(context).style;

    return LayoutBuilder(
      builder: (context, constraints) {
        // Measure the actual localized text on the current device. This is
        // deliberately based on rendered lines rather than character count:
        // Russian translations, font scale and screen width can turn a short
        // English string into 4+ lines.
        final available = (constraints.maxWidth - 28).clamp(0.0, double.infinity);
        final painter = TextPainter(
          text: TextSpan(text: widget.text, style: style),
          textDirection: Directionality.of(context),
          maxLines: widget.maxLinesBeforeCollapse,
        )..layout(maxWidth: available);
        final shouldCompact = painter.didExceedMaxLines;

        if (!shouldCompact) {
          return Text(widget.text, style: widget.style);
        }

        return AnimatedSize(
          duration: const Duration(milliseconds: 180),
          curve: Curves.easeOut,
          alignment: Alignment.topCenter,
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Text(
                  widget.text,
                  style: widget.style,
                  softWrap: _expanded,
                  maxLines: _expanded ? null : 1,
                  overflow: _expanded
                      ? TextOverflow.visible
                      : TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 2),
              InkWell(
                borderRadius: BorderRadius.circular(16),
                onTap: () => setState(() => _expanded = !_expanded),
                child: Padding(
                  padding: const EdgeInsets.all(4),
                  child: Icon(
                    _expanded ? Icons.expand_less : Icons.expand_more,
                    size: 18,
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }'''
s = s[:start] + new_build + s[end:]
helper.write_text(s, encoding='utf-8')

mode = Path('app/lib/screens/vpn_mode_tab.dart')
s = mode.read_text(encoding='utf-8')
if "../widgets/compact_description.dart" not in s:
    s = s.replace("import 'lazy_persist_mixin.dart';", "import 'lazy_persist_mixin.dart';\nimport '../widgets/compact_description.dart';")
s = s.replace('''        Text(
          _modeDescription(_cfg.mode),
          style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
        ),''', '''        CompactDescription(
          _modeDescription(_cfg.mode),
          style: tt.bodySmall?.copyWith(color: cs.onSurfaceVariant),
        ),''')
mode.write_text(s, encoding='utf-8')
