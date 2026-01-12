import { Box, Paper, Typography, Divider, CircularProgress, Alert } from '@mui/material';
import { Psychology } from '@mui/icons-material';
import { useChatStore } from '@/stores/chatStore';
import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

export default function ChatInterface() {
  const { messages, isStreaming, investigationId } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', bgcolor: '#1a1a1a' }}>
      {/* Chat Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Psychology color="primary" />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            AI Investigation Assistant
          </Typography>
        </Box>
        <Typography variant="caption" color="text.secondary">
          Powered by Amazon Bedrock • Claude Haiku 4.5
        </Typography>
      </Box>
      
      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          '&::-webkit-scrollbar': { width: 8 },
          '&::-webkit-scrollbar-thumb': { bgcolor: '#555', borderRadius: 4 },
        }}
      >
        {messages.length === 0 ? (
          <Paper
            sx={{
              p: 4,
              textAlign: 'center',
              bgcolor: 'background.paper',
              mt: 4,
            }}
          >
            <Psychology sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Ready to Investigate
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Click <strong>Investigate</strong> on any alarm to start AI-powered analysis
            </Typography>
            <Divider sx={{ my: 2 }} />
            <Typography variant="caption" color="text.secondary">
              The AI will automatically:
            </Typography>
            <Box component="ul" sx={{ textAlign: 'left', mt: 1, pl: 2 }}>
              <Typography component="li" variant="caption" color="text.secondary">
                Query Zabbix for host and trigger data
              </Typography>
              <Typography component="li" variant="caption" color="text.secondary">
                Analyze metrics and historical patterns
              </Typography>
              <Typography component="li" variant="caption" color="text.secondary">
                Identify root causes
              </Typography>
              <Typography component="li" variant="caption" color="text.secondary">
                Provide remediation steps
              </Typography>
            </Box>
          </Paper>
        ) : (
          <>
            {messages.map((msg, idx) => (
              <Box
                key={idx}
                sx={{
                  mb: 2,
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <Paper
                  sx={{
                    p: 2,
                    maxWidth: '85%',
                    bgcolor: msg.role === 'user' ? 'primary.dark' : 
                             msg.role === 'system' ? 'action.hover' : 'background.paper',
                  }}
                >
                  {msg.role === 'system' && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      SYSTEM
                    </Typography>
                  )}
                  <Box sx={{ 
                    '& p': { my: 1 },
                    '& code': { 
                      bgcolor: '#000', 
                      p: 0.5, 
                      borderRadius: 0.5,
                      fontFamily: 'monospace',
                      fontSize: '0.85em'
                    },
                    '& pre': {
                      bgcolor: '#000',
                      p: 1,
                      borderRadius: 1,
                      overflow: 'auto'
                    }
                  }}>
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                    {msg.timestamp.toLocaleTimeString()}
                  </Typography>
                </Paper>
              </Box>
            ))}
            {isStreaming && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
                <CircularProgress size={16} />
                <Typography variant="caption" color="text.secondary">
                  AI is analyzing...
                </Typography>
              </Box>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </Box>
      
      {investigationId && (
        <Alert severity="info" sx={{ m: 2 }}>
          Investigation ID: {investigationId}
        </Alert>
      )}
    </Box>
  );
}
