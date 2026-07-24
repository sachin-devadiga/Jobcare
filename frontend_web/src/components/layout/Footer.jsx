'use client';
import { Box, Typography, Link, Container } from '@mui/material';

export default function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        py: 2,
        px: 3,
        borderTop: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
    >
      <Container maxWidth={false} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 1 }}>
        <Typography variant="caption" color="text.secondary">
          &copy; {new Date().getFullYear()} JobCare Voice. All rights reserved.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Link href="#" variant="caption" color="text.secondary" underline="hover">
            Privacy
          </Link>
          <Link href="#" variant="caption" color="text.secondary" underline="hover">
            Terms
          </Link>
          <Link href="#" variant="caption" color="text.secondary" underline="hover">
            Support
          </Link>
        </Box>
      </Container>
    </Box>
  );
}
