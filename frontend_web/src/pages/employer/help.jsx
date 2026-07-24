import { Box, Typography, Paper, Accordion, AccordionSummary, AccordionDetails, TextField, Button } from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpIcon from '@mui/icons-material/Help';
import { useState } from 'react';

const faqs = [
  { q: 'How do I post a new job?', a: 'Navigate to "Post Job" from the sidebar, fill in the job details, and click "Publish Job" to make it live. You can also save it as a draft to publish later.' },
  { q: 'How do I review applicants?', a: 'Go to "Applicants" in the sidebar. You can view all applicants, filter by status, and click on any applicant to see their full profile, resume, and voice resume.' },
  { q: 'What is the AI Match Score?', a: 'The AI Match Score is a percentage that indicates how well an applicant\'s skills and experience match your job requirements. It\'s calculated using our advanced AI algorithm.' },
  { q: 'How do I schedule an interview?', a: 'Open an applicant\'s detail page and click the "Schedule" button. Choose the date, time, interview type, and add any notes.' },
  { q: 'Can I customize my company profile?', a: 'Yes! Go to "Company Profile" in the sidebar to update your company information, logo, banner, and social links.' },
  { q: 'How does billing work?', a: 'Visit "Subscriptions" to view available plans. You can upgrade, downgrade, or cancel your subscription at any time.' },
  { q: 'What analytics are available?', a: 'The Analytics dashboard provides insights into job views, applications, interview conversion rates, revenue trends, and more.' },
  { q: 'How do I reset my password?', a: 'Go to the login page and click "Forgot password?" to receive a password reset link via email.' },
];

export default function HelpPage() {
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Help & Support</Typography>
        <Typography variant="body2" color="text.secondary">Find answers and get support</Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>Frequently Asked Questions</Typography>
        {faqs.map((faq, idx) => (
          <Accordion key={idx} sx={{ boxShadow: 'none', '&:before': { display: 'none' }, borderBottom: '1px solid', borderColor: 'divider' }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>{faq.q}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" color="text.secondary">{faq.a}</Typography>
            </AccordionDetails>
          </Accordion>
        ))}
      </Paper>

      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>Contact Support</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Can&apos;t find what you&apos;re looking for? Send us a message.
        </Typography>
        <Box sx={{ maxWidth: 500 }}>
          <TextField fullWidth label="Subject" value={subject} onChange={(e) => setSubject(e.target.value)} sx={{ mb: 2 }} />
          <TextField fullWidth multiline rows={4} label="Message" value={message} onChange={(e) => setMessage(e.target.value)} sx={{ mb: 2 }} />
          <Button variant="contained" disabled={!subject || !message}>Send Message</Button>
        </Box>
      </Paper>
    </DashboardLayout>
  );
}
