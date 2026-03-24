import React, { useState } from "react";
import {
  Box, TextField, Button, CircularProgress, Alert,
  Typography, Paper, Chip, Divider, Grid,
} from "@mui/material";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { extractEntities } from "../services/nerApi";
import HighlightedText from "../components/HighlightedText";

const SAMPLES = [
  {
    label: "Earnings Report",
    text: `Apple Inc. reported record revenue of $119.6 billion in Q1 2024, up 2% year-over-year. 
CEO Tim Cook said the company's EPS reached $2.18, beating analyst expectations. 
The stock ticker AAPL rose 3.5% on the NYSE following the announcement. 
Apple's market cap now exceeds $3 trillion, making it the most valuable company in the world.`,
  },
  {
    label: "M&A News",
    text: `Microsoft Corporation announced on January 18, 2024 that it completed its $68.7 billion 
acquisition of Activision Blizzard. The deal, which faced regulatory scrutiny from the FTC, 
is expected to boost Microsoft's gaming revenue by 15% in fiscal year 2025. 
Satya Nadella, CEO of Microsoft, called it a transformative moment for the gaming industry.`,
  },
  {
    label: "Fed Report",
    text: `The Federal Reserve raised interest rates by 25 basis points to 5.5% in July 2023. 
Fed Chair Jerome Powell indicated that inflation, currently at 3.2%, remains above the 2% target. 
Goldman Sachs and JPMorgan Chase both revised their GDP growth forecasts for the United States 
downward to 1.8% for Q3 2023.`,
  },
];

export default function ExtractPage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleExtract = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await extractEntities(text);
      setResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Extraction failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Extract Finance Entities</Typography>

      {/* Sample buttons */}
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2 }}>
        {SAMPLES.map((s) => (
          <Chip key={s.label} label={s.label} size="small" variant="outlined"
            onClick={() => setText(s.text)} clickable />
        ))}
      </Box>

      <TextField
        fullWidth multiline rows={6}
        label="Paste financial news or report text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        sx={{ mb: 2 }}
        helperText={`${text.split(/\s+/).filter(Boolean).length} words`}
      />

      <Button variant="contained" fullWidth size="large"
        disabled={!text.trim() || loading} onClick={handleExtract}
        startIcon={loading ? <CircularProgress size={18} color="inherit" /> : null}
      >
        {loading ? "Extracting..." : "Extract Entities"}
      </Button>

      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

      {result && (
        <Box sx={{ mt: 3 }}>
          {/* Stats */}
          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mb: 2 }}>
            <Chip label={`${result.total} entities found`} color="primary" />
            <Chip label={`${result.word_count} words`} variant="outlined" />
            <Chip label={`${result.label_counts.length} entity types`} variant="outlined" />
          </Box>

          <Grid container spacing={3}>
            {/* Highlighted text */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Annotated Text
              </Typography>
              <Paper variant="outlined" sx={{ p: 2 }}>
                <HighlightedText text={text} entities={result.entities} />
              </Paper>
            </Grid>

            {/* Entity counts bar chart */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Entity Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={result.label_counts} layout="vertical">
                  <XAxis type="number" allowDecimals={false} />
                  <YAxis type="category" dataKey="label_name" width={110} tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(v, n, p) => [v, p.payload.label_name]} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {result.label_counts.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Grid>

            {/* Entity list by type */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Entities by Type
              </Typography>
              {Object.entries(result.by_label).map(([label, values]) => (
                <Box key={label} sx={{ mb: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight="bold">
                    {label}
                  </Typography>
                  <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5, mt: 0.5 }}>
                    {values.map((v, i) => (
                      <Chip key={i} label={v} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              ))}
            </Grid>
          </Grid>
        </Box>
      )}
    </Box>
  );
}
