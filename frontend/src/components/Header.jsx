import { AppBar, Toolbar, Typography } from "@mui/material";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";

export default function Header() {
  return (
    <AppBar position="static" color="primary">
      <Toolbar sx={{ gap: 1 }}>
        <AccountBalanceIcon />
        <Typography variant="h6" fontWeight="bold">
          Finance Named Entity Recognition
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
