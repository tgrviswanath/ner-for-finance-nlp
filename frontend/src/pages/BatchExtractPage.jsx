import React, { useState } from "react";
import {
  Box, TextField, Button, CircularProgress, Alert, Typography,
  Paper, Chip, Table, TableHead, TableRow, TableCell,
  TableBody, TableContainer,
} from "@mui/material";
import { extractBatch } from "../services/nerApi";

const PLACEHOLDER = `Apple Inc. reported revenue of $119.6 billion in Q1 2024.
Microsoft acquired Activision Blizzard for $68.7 billion in January 2024.
The Federal Reserve raised rates by 25 basis points to 5.5%.`;

export default function BatchExtractPage() {
  const [input, setInput] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleBatch = async () => {
    const texts = input.split("\n").map((t) => t.trim()).filter(Boolean);
    if (!texts.length) return;
    setLoading(true);
    setError("");
    try {
      const res = await extractBatch(texts);
      setResults(res.data.map((r, i) => ({ ...r, text: texts[i] })));
    } catch (e) {
      setError(e.response?.data?.detail || "Batch extraction failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>Batch Extract (one text per line)</Typography>

      <TextField
        fullWidth multiline rows={6}
        label="Enter texts (one per line)"
        placeholder={PLACEHOLDER}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        sx={{ mb: 2 }}
      />

      <Button variant="contained" fullWidth size="large"
        disabled={!input.trim() || loading} onClick={handleBatch}
        startIcon={loading ? <CircularProgress size={18} color="inherit" /> : null}
      >
        {loading ? "Extracting..." : "Extract All"}
      </Button>

      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}

      {results.length > 0 && (
        <Box sx={{ mt: 3 }}>
          {results.map((r, i) => (
            <Paper key={i} variant="outlined" sx={{ p: 2, mb: 2 }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                <strong>#{i + 1}</strong> — {r.text.slice(0, 100)}{r.text.length > 100 ? "..." : ""}
              </Typography>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                {r.entities.map((ent, j) => (
                  <Chip
                    key={j}
                    label={`${ent.icon} ${ent.text}`}
                    size="small"
                    sx={{ bgcolor: ent.color + "22", borderColor: ent.color, color: "text.primary" }}
                    variant="outlined"
                    title={ent.label_name}
                  />
                ))}
                {r.entities.length === 0 && (
                  <Typography variant="body2" color="text.secondary">No entities found</Typography>
                )}
              </Box>
            </Paper>
          ))}
        </Box>
      )}
    </Box>
  );
}
