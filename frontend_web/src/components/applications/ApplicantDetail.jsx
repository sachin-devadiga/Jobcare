'use client';
import { useState, useRef } from 'react';
import {
  Box, Grid, Paper, Typography, Avatar, Chip, Button, IconButton,
  LinearProgress, Divider, TextField, List, ListItem, ListItemText,
  ListItemAvatar, Tab, Tabs, Rating, Card, CardContent,
} from '@mui/material';
import PhoneIcon from '@mui/icons-material/Phone';
import EmailIcon from '@mui/icons-material/Email';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import DownloadIcon from '@mui/icons-material/Download';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import NoteAddIcon from '@mui/icons-material/NoteAdd';
import SchoolIcon from '@mui/icons-material/School';
import WorkIcon from '@mui/icons-material/Work';
import { getInitials, getAvatarColor } from '@/utils/helpers';
import { formatDate, formatRelativeTime } from '@/utils/formatters';
import StatusBadge from '@/components/common/StatusBadge';
import StatusUpdateModal from './StatusUpdateModal';
import InterviewScheduler from './InterviewScheduler';

function TabPanel({ children, value, index }) {
  return value === index ? <Box sx={{ py: 2 }}>{children}</Box> : null;
}

export default function ApplicantDetail({ applicant, onStatusUpdate, onScheduleInterview, onAddNote }) {
  const [tabValue, setTabValue] = useState(0);
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [interviewModalOpen, setInterviewModalOpen] = useState(false);
  const [noteText, setNoteText] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  const matchScore = applicant.matchScore || applicant.aiScore || 0;

  const handlePlayVoice = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleAddNote = () => {
    if (noteText.trim() && onAddNote) {
      onAddNote(applicant._id || applicant.id, noteText);
      setNoteText('');
    }
  };

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 3, borderRadius: 3 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 3 }}>
              <Avatar
                src={applicant.avatar}
                sx={{
                  width: 80,
                  height: 80,
                  bgcolor: getAvatarColor(applicant.name || applicant.fullName),
                  fontSize: '1.5rem',
                  fontWeight: 600,
                }}
              >
                {getInitials(applicant.name || applicant.fullName)}
              </Avatar>
              <Box sx={{ flex: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
                  {applicant.name || applicant.fullName}
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 1 }}>
                  {applicant.currentPosition || applicant.headline || 'Candidate'}
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 1.5 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <EmailIcon sx={{ fontSize: 16 }} /> {applicant.email}
                  </Typography>
                  {applicant.phone && (
                    <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <PhoneIcon sx={{ fontSize: 16 }} /> {applicant.phone}
                    </Typography>
                  )}
                  {applicant.location && (
                    <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <LocationOnIcon sx={{ fontSize: 16 }} /> {applicant.location}
                    </Typography>
                  )}
                </Box>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <StatusBadge status={applicant.status} />
                  {applicant.appliedJob && (
                    <Chip label={`Applied for: ${applicant.appliedJob}`} size="small" variant="outlined" />
                  )}
                </Box>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'action.hover', borderRadius: 3 }}>
              <Typography variant="h3" sx={{ fontWeight: 800, color: matchScore >= 70 ? 'success.main' : matchScore >= 40 ? 'warning.main' : 'text.secondary' }}>
                {matchScore}%
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>AI Match Score</Typography>
              <LinearProgress
                variant="determinate"
                value={matchScore}
                sx={{ height: 8, borderRadius: 4, mb: 2 }}
              />
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                <Button variant="contained" size="small" onClick={() => setStatusModalOpen(true)}>
                  Update Status
                </Button>
                <Button variant="outlined" size="small" onClick={() => setInterviewModalOpen(true)}>
                  Schedule
                </Button>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ borderRadius: 3 }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)} sx={{ px: 2, pt: 1 }}>
          <Tab label="Profile" />
          <Tab label="Resume" />
          <Tab label="Voice Resume" />
          <Tab label="Notes" />
        </Tabs>
        <Divider />

        <Box sx={{ px: 3, pb: 3 }}>
          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>Skills</Typography>
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {(applicant.skills || []).map((skill) => (
                    <Chip key={skill} label={skill} variant="outlined" size="small" sx={{ borderRadius: 2 }} />
                  ))}
                  {(!applicant.skills || applicant.skills.length === 0) && (
                    <Typography variant="body2" color="text.secondary">No skills listed</Typography>
                  )}
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>Experience</Typography>
                {(applicant.experience || []).map((exp, idx) => (
                  <Box key={idx} sx={{ mb: 1.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{exp.title || exp.position}</Typography>
                    <Typography variant="caption" color="text.secondary">{exp.company} &middot; {exp.duration}</Typography>
                  </Box>
                ))}
                {(!applicant.experience || applicant.experience.length === 0) && (
                  <Typography variant="body2" color="text.secondary">No experience listed</Typography>
                )}
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Education</Typography>
                {(applicant.education || []).map((edu, idx) => (
                  <Box key={idx} sx={{ mb: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{edu.degree} in {edu.field}</Typography>
                    <Typography variant="caption" color="text.secondary">{edu.institution} &middot; {edu.year}</Typography>
                  </Box>
                ))}
                {(!applicant.education || applicant.education.length === 0) && (
                  <Typography variant="body2" color="text.secondary">No education listed</Typography>
                )}
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>AI Match Breakdown</Typography>
                {applicant.matchBreakdown ? (
                  <Grid container spacing={2}>
                    {Object.entries(applicant.matchBreakdown).map(([key, val]) => (
                      <Grid item xs={6} sm={3} key={key}>
                        <Box sx={{ textAlign: 'center', p: 1.5, bgcolor: 'action.hover', borderRadius: 2 }}>
                          <Typography variant="h6" sx={{ fontWeight: 700 }}>{val}%</Typography>
                          <Typography variant="caption" color="text.secondary">{key.replace(/_/g, ' ')}</Typography>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Typography variant="body2" color="text.secondary">No breakdown available</Typography>
                )}
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              {applicant.resumeUrl ? (
                <Box>
                  <iframe
                    src={applicant.resumeUrl}
                    title="Resume"
                    style={{ width: '100%', height: 600, border: 'none', borderRadius: 12 }}
                  />
                  <Button variant="contained" startIcon={<DownloadIcon />} sx={{ mt: 2 }}>
                    Download Resume
                  </Button>
                </Box>
              ) : (
                <Typography color="text.secondary">No resume uploaded</Typography>
              )}
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              {applicant.voiceResumeUrl ? (
                <Box>
                  <audio ref={audioRef} src={applicant.voiceResumeUrl} onEnded={() => setIsPlaying(false)} />
                  <Box
                    sx={{
                      width: 120,
                      height: 120,
                      borderRadius: '50%',
                      bgcolor: 'primary.main',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2,
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': { transform: 'scale(1.05)', boxShadow: 4 },
                    }}
                    onClick={handlePlayVoice}
                  >
                    {isPlaying ? <PauseIcon sx={{ fontSize: 48, color: '#fff' }} /> : <PlayArrowIcon sx={{ fontSize: 48, color: '#fff' }} />}
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {isPlaying ? 'Playing voice resume...' : 'Click to play voice resume'}
                  </Typography>
                </Box>
              ) : (
                <Typography color="text.secondary">No voice resume available</Typography>
              )}
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                multiline
                rows={3}
                placeholder="Add a note about this candidate..."
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                sx={{ mb: 1 }}
              />
              <Button variant="contained" startIcon={<NoteAddIcon />} onClick={handleAddNote} disabled={!noteText.trim()}>
                Add Note
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />
            {(applicant.notes || []).length === 0 ? (
              <Typography color="text.secondary">No notes yet</Typography>
            ) : (
              (applicant.notes || []).map((note, idx) => (
                <Paper key={idx} variant="outlined" sx={{ p: 2, mb: 1, borderRadius: 2 }}>
                  <Typography variant="body2">{note.content || note.text}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {note.author} &middot; {formatRelativeTime(note.createdAt)}
                  </Typography>
                </Paper>
              ))
            )}
          </TabPanel>
        </Box>
      </Paper>

      <StatusUpdateModal
        open={statusModalOpen}
        onClose={() => setStatusModalOpen(false)}
        currentStatus={applicant.status}
        onSubmit={(status, notes) => onStatusUpdate?.(applicant._id || applicant.id, status, notes)}
      />

      <InterviewScheduler
        open={interviewModalOpen}
        onClose={() => setInterviewModalOpen(false)}
        onSubmit={(data) => onScheduleInterview?.(applicant._id || applicant.id, data)}
      />
    </Box>
  );
}
