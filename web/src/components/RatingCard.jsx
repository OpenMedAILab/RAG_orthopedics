import React from 'react';
import { Card, CardContent, CardHeader, Typography, Button, ButtonGroup, Box } from '@mui/material';

const RatingCard = ({ ratings, onRatingChange }) => {
  const dimensions = [
    {
      key: 'accuracy',
      title: '医学准确性',
      description: '回答中的医学信息是否正确、精准，且无安全隐患？'
    },
    {
      key: 'recall',
      title: '关键要点召回率',
      description: '回答是否全面覆盖了病例分析所必需的关键信息点？'
    },
    {
      key: 'logic',
      title: '逻辑完整性',
      description: '回答是否展现了清晰、连贯且符合临床实践的思维过程？'
    }
  ];

  const handleRatingSelect = (dimension, value) => {
    onRatingChange(dimension, value);
  };

  return (
    <Card sx={{ mb: 2, boxShadow: 3 }}>
      <CardHeader title="评分（3分制）" />
      <CardContent>
        {dimensions.map((dimension) => (
          <Box key={dimension.key} sx={{ mb: 3, pb: 3, borderBottom: '1px solid #eee' }}>
            <Typography variant="h6" gutterBottom>
              {dimension.title}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {dimension.description}
            </Typography>
            
            <ButtonGroup 
              variant="outlined" 
              fullWidth 
              sx={{ mt: 1 }}
            >
              {[1, 2, 3].map((value) => (
                <Button
                  key={value}
                  variant={ratings[dimension.key] === value ? 'contained' : 'outlined'}
                  color={ratings[dimension.key] === value ? 'primary' : 'inherit'}
                  onClick={() => handleRatingSelect(dimension.key, value)}
                  sx={{ flex: 1 }}
                >
                  {value}分
                </Button>
              ))}
            </ButtonGroup>
          </Box>
        ))}
      </CardContent>
    </Card>
  );
};

export default RatingCard;