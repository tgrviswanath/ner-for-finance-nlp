import React, { useState } from "react";
import { Container, Box, Tabs, Tab } from "@mui/material";
import Header from "./components/Header";
import ExtractPage from "./pages/ExtractPage";
import BatchExtractPage from "./pages/BatchExtractPage";

export default function App() {
  const [tab, setTab] = useState(0);
  return (
    <>
      <Header />
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
          <Tab label="Single Extract" />
          <Tab label="Batch Extract" />
        </Tabs>
        <Box>{tab === 0 ? <ExtractPage /> : <BatchExtractPage />}</Box>
      </Container>
    </>
  );
}
