import { Box, Typography, Tooltip } from "@mui/material";

/**
 * Renders text with inline colored highlights for each entity span.
 * Overlapping spans are handled by sorting and de-overlapping.
 */
export default function HighlightedText({ text, entities }) {
  if (!entities || entities.length === 0) {
    return <Typography variant="body1" sx={{ lineHeight: 2 }}>{text}</Typography>;
  }

  // Sort by start position, remove overlaps
  const sorted = [...entities].sort((a, b) => a.start - b.start);
  const spans = [];
  let cursor = 0;

  for (const ent of sorted) {
    if (ent.start < cursor) continue; // skip overlapping
    if (ent.start > cursor) {
      spans.push({ type: "text", text: text.slice(cursor, ent.start) });
    }
    spans.push({ type: "entity", text: text.slice(ent.start, ent.end), ent });
    cursor = ent.end;
  }
  if (cursor < text.length) {
    spans.push({ type: "text", text: text.slice(cursor) });
  }

  return (
    <Typography variant="body1" component="div" sx={{ lineHeight: 2.2, whiteSpace: "pre-wrap" }}>
      {spans.map((span, i) =>
        span.type === "text" ? (
          <span key={i}>{span.text}</span>
        ) : (
          <Tooltip
            key={i}
            title={`${span.ent.icon} ${span.ent.label_name}`}
            arrow
          >
            <Box
              component="mark"
              sx={{
                bgcolor: span.ent.color + "33",   // 20% opacity
                borderBottom: `2px solid ${span.ent.color}`,
                borderRadius: "3px",
                px: 0.3,
                cursor: "help",
                fontWeight: 500,
                color: "text.primary",
              }}
            >
              {span.text}
              <Box
                component="sup"
                sx={{ fontSize: "0.6rem", color: span.ent.color, ml: 0.3, fontWeight: "bold" }}
              >
                {span.ent.label}
              </Box>
            </Box>
          </Tooltip>
        )
      )}
    </Typography>
  );
}
