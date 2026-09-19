import 'package:flutter/material.dart';

/// Long explanatory text is shown as one compact line and can be expanded.
/// Short descriptions are left unchanged.
class CompactDescription extends StatefulWidget {
  const CompactDescription(
    this.text, {
    super.key,
    this.style,
    this.maxLinesBeforeCollapse = 3,
  });

  final String text;
  final TextStyle? style;
  final int maxLinesBeforeCollapse;

  @override
  State<CompactDescription> createState() => _CompactDescriptionState();
}

class _CompactDescriptionState extends State<CompactDescription> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final style = widget.style ?? DefaultTextStyle.of(context).style;

    return LayoutBuilder(
      builder: (context, constraints) {
        final available =
            (constraints.maxWidth - 28).clamp(0.0, double.infinity);
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
  }
}
