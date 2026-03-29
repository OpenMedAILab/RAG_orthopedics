import React from 'react';
import { Card, CardContent, CardHeader, Typography, Paper } from '@mui/material';

const CaseContentCard = ({ item }) => {
  if (!item) return null;

  return (
    <Card sx={{ mb: 2, boxShadow: 3 }}>
      <CardHeader title="病例内容" />
      <CardContent>
        {item.qa_pairs && item.qa_pairs.length > 0 ? (
          <div>
            {item.qa_pairs.map((pair, index) => (
              <Paper 
                key={index} 
                sx={{ 
                  p: 2, 
                  mb: 2, 
                  borderLeft: 4, 
                  borderLeftColor: 'primary.main' 
                }}
              >
                <Typography variant="h6" color="primary" gutterBottom>
                  问题 {index + 1}:
                </Typography>
                <Typography paragraph>
                  {pair.question}
                </Typography>
                
                <Typography variant="h6" color="success.main" gutterBottom>
                  回答:
                </Typography>
                <Typography paragraph>
                  {pair.answer}
                </Typography>
              </Paper>
            ))}

            {item.rag_context && item.rag_context.trim() !== '' && (
              <Paper 
                sx={{ 
                  p: 2, 
                  mt: 2, 
                  backgroundColor: 'orange.50',
                  borderLeft: 4, 
                  borderLeftColor: 'orange.400' 
                }}
              >
                <Typography variant="h6" color="warning.main" gutterBottom>
                  RAG上下文
                </Typography>
                <Typography paragraph>
                  {item.rag_context}
                </Typography>
              </Paper>
            )}
          </div>
        ) : (
          <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 4 }}>
            请选择一个项目以查看病例内容
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default CaseContentCard;